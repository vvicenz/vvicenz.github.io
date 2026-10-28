"""Teste terrestre B: três corpos Sol-Terra-Lua a partir do estado real de
2024-01-01 (efeméride ERFA embutida no astropy), 19 anos em passos de 1 h.

Compara com a Terra real: posição da lua (astropy), mês sinódico, regressão
dos nodos, precessão do perigeu, lista de eclipses 2024-2028 (NASA/Espenak) e
amplitudes de equilíbrio das constituintes de maré (Cartwright-Tayler-Edden).
"""
import json, sys, pathlib, time
import numpy as np
import erfa
from astropy.time import Time
from astropy.coordinates import get_body_barycentric_posvel, get_body
import astropy.units as u

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from mundo.constantes import G, GM_SOL, GM_PLANETA, M_LUA, R_LUA, R_SOL, R_PLANETA, DIA
from mundo.nbody import TresCorpos, estado_para_elementos
from mundo.lua import Efemeride, eclipses
from mundo.mare import altura_equilibrio, velocidades, ajuste_harmonico

RAIZ = pathlib.Path(__file__).resolve().parents[1]
OUT = RAIZ / "dados/f1/terra"; OUT.mkdir(parents=True, exist_ok=True)
ANOS = 19.0

t0 = Time("2024-01-01T00:00:00", scale="tdb")
pv = {b: get_body_barycentric_posvel(b, t0, ephemeris="builtin") for b in ("sun", "earth", "moon")}
X = {b: pv[b][0].xyz.to(u.m).value for b in pv}
V = {b: pv[b][1].xyz.to(u.m / u.s).value for b in pv}
m0, m1, m2 = GM_SOL / G, GM_PLANETA / G, M_LUA
mu1 = m1 + m2
r1 = X["moon"] - X["earth"]; v1 = V["moon"] - V["earth"]
Xb = (m1 * X["earth"] + m2 * X["moon"]) / mu1; Vb = (m1 * V["earth"] + m2 * V["moon"]) / mu1
r2 = Xb - X["sun"]; v2 = Vb - V["sun"]

sis = TresCorpos(m0, m1, m2)

# A velocidade da lua na ERFA embutida é aproximada (o modelo de posição é
# truncado); um erro de 1e-5 no movimento médio vira 10' por ano. Ajusta-se o
# estado inicial da lua às posições ERFA dos primeiros 120 dias (6 parâmetros,
# mínimos quadrados) e testa-se fora da amostra, nos anos seguintes.
from scipy.optimize import least_squares
dias_aj = np.arange(0, 121, 1.0)
alvo = get_body("moon", t0 + dias_aj * u.day, ephemeris="builtin").cartesian.xyz.to(u.m).value.T
def resid(p):
    y0 = np.concatenate([r1 + p[:3] * 1e3, v1 + p[3:] * 1e-2, r2, v2])
    _, R1a, _, _, _ = sis.integrar(y0, 120 * DIA, DIA, rtol=1e-11)
    return ((R1a - alvo) / 1e3).ravel()
aj = least_squares(resid, np.zeros(6), x_scale=1.0, diff_step=1e-4)
print("ajuste do estado inicial da lua: Δr (km)", aj.x[:3].round(3), "Δv (cm/s)", aj.x[3:].round(3),
      "rms (km)", np.sqrt(np.mean(aj.fun**2)).round(2))
r1 = r1 + aj.x[:3] * 1e3; v1 = v1 + aj.x[3:] * 1e-2
tic = time.time()
t, R1, V1, R2, V2 = sis.integrar(np.concatenate([r1, v1, r2, v2]), ANOS * 365.25 * DIA, 3600.0)
print(f"integração {ANOS} anos: {time.time() - tic:.1f} s, {len(t)} amostras")
Xs, Xp, Xm = sis.posicoes(R1, R2)
s_geo = Xs - Xp; m_geo = R1

# --- posição da lua vs efeméride real, fora da amostra: dias 120 a 5 anos (a cada 2 dias)
idx = np.arange(120 * 24, int(5 * 365.25 * 24), 48)
tt = t0 + t[idx] * u.s
lua_real = get_body("moon", tt, ephemeris="builtin")  # GCRS
lua_real_v = lua_real.cartesian.xyz.to(u.m).value.T
ang = np.degrees(np.arccos(np.clip((lua_real_v * m_geo[idx]).sum(1) /
                  np.linalg.norm(lua_real_v, axis=1) / np.linalg.norm(m_geo[idx], axis=1), -1, 1)))
print(f"lua: erro angular vs ERFA, dia 120 a ano 5: médio {ang.mean()*3600:.1f}\", máx {ang.max()*3600:.1f}\"")

# --- referencial eclíptico J2000 (ICRS girado pela obliquidade)
eps0 = np.radians(23.4392911)
R_ecl = np.array([[1, 0, 0], [0, np.cos(eps0), np.sin(eps0)], [0, -np.sin(eps0), np.cos(eps0)]])
ef = Efemeride(t / DIA, s_geo, m_geo, R_ecl)
novas = ef.sizigias(0.0)
sinodico = np.polyfit(np.arange(len(novas)), novas, 1)[0]
print("mês sinódico médio (d):", sinodico)

# --- elementos osculadores da lua -> nodo e perigeu
el = estado_para_elementos(G * mu1, m_geo @ R_ecl.T, V1 @ R_ecl.T)
anos = t / DIA / 365.25
p_nodo = 2 * np.pi / np.polyfit(anos, np.unwrap(el["Omega"]), 1)[0]
p_peri = 2 * np.pi / np.polyfit(anos, np.unwrap(el["varpi"]), 1)[0]
print(f"período do nodo {p_nodo:.3f} a; do perigeu {p_peri:.3f} a; e médio {el['e'].mean():.4f}; "
      f"i médio {np.degrees(el['i']).mean():.3f}")

# --- eclipses 2024-2028
ecl = eclipses(ef, R_PLANETA, R_LUA, R_SOL)
REAIS = [("2024-03-25", "lua", "penumbral"), ("2024-04-08", "sol", "total"),
         ("2024-09-18", "lua", "parcial"), ("2024-10-02", "sol", "anular"),
         ("2025-03-14", "lua", "total"), ("2025-03-29", "sol", "parcial"),
         ("2025-09-07", "lua", "total"), ("2025-09-21", "sol", "parcial"),
         ("2026-02-17", "sol", "anular"), ("2026-03-03", "lua", "total"),
         ("2026-08-12", "sol", "total"), ("2026-08-28", "lua", "parcial"),
         ("2027-02-06", "sol", "anular"), ("2027-02-20", "lua", "penumbral"),
         ("2027-07-18", "lua", "penumbral"), ("2027-08-02", "sol", "total"),
         ("2027-08-17", "lua", "penumbral"), ("2028-01-12", "lua", "parcial"),
         ("2028-01-26", "sol", "anular"), ("2028-07-06", "lua", "parcial"),
         ("2028-07-22", "sol", "total"), ("2028-12-31", "lua", "total")]
fim = (Time("2029-01-01", scale="tdb") - t0).to(u.day).value
mod = [e for e in ecl if e["t"] < fim]
linhas = []
for e in mod:
    data = (t0 + e["t"] * u.day).utc.iso[:16]
    linhas.append(dict(data_utc=data, corpo=e["corpo"], tipo=e["tipo"],
                       gama=round(e["gama"], 4), grandeza=round(e["grandeza"], 4)))
casam = 0
for d, c, tp in REAIS:
    achou = [l for l in linhas if l["data_utc"][:10] == d and l["corpo"] == c]
    if achou and achou[0]["tipo"].split()[0] == tp:
        casam += 1
    print(f"real {d} {c:3s} {tp:9s} | modelo: {achou[0]['tipo'] + ' ' + achou[0]['data_utc'] if achou else '—'}")
print(f"eclipses: {casam}/{len(REAIS)} reais reproduzidos (data e tipo); modelo lista {len(mod)}")

# --- maré de equilíbrio: equador da data via precessão-nutação ERFA, GMST06
jd_tt = t0.jd + t / DIA
pnm = erfa.pnm06a(2400000.5, jd_tt - 2400000.5)
uso = np.arange(len(t))
s_eq = np.einsum("nij,nj->ni", pnm, s_geo); m_eq = np.einsum("nij,nj->ni", pnm, m_geo)
gmst = erfa.gmst06(2400000.5, jd_tt - 2400000.5 - 69.2 / DIA, 2400000.5, jd_tt - 2400000.5)
gr = 2 * np.pi / 360 / DIA  # grau/dia -> rad/s
vel = velocidades(theta_dot=2 * np.pi * 1.00273790935 / DIA, s_dot=360 / 27.321582 * gr,
                  h_dot=360 / 365.24219 * gr, p_dot=360 / (8.8475 * 365.25) * gr)
REF = dict(M2=0.242334, S2=0.112841, N2=0.046398, K2=0.030704,
           K1=0.141565, O1=0.100514, P1=0.046843, Q1=0.019256)
amps, serie = {}, {}
for lat in (0.0, 45.0):
    eta = altura_equilibrio(lat, 0.0, [(m0, s_eq), (m2, m_eq)], gmst, R_PLANETA, m1)
    a, rms = ajuste_harmonico(t, eta, vel)
    amps[lat] = a; serie[lat] = eta
    print(f"lat {lat}: resíduo rms {rms*100:.2f} cm; amplitude máx {np.abs(eta).max():.3f} m")
tab = {}
for k, ref in REF.items():
    modelo = amps[0.0][k] if k.endswith("2") else amps[45.0][k]
    tab[k] = dict(modelo_m=round(modelo, 5), referencia_m=ref, razao=round(modelo / ref, 4))
    print(f"  {k}: modelo {modelo:.5f} m  ref {ref:.5f} m  razão {modelo/ref:.4f}")

resumo = dict(
    lua_erro_angular_5anos_medio_arcsec=float(ang.mean() * 3600),
    lua_erro_angular_5anos_max_arcsec=float(ang.max() * 3600),
    mes_sinodico_d=float(sinodico), mes_sinodico_real_d=29.530589,
    periodo_nodo_anos=float(p_nodo), periodo_nodo_real_anos=-18.613,
    lua_e_media=float(el['e'].mean()), lua_i_media_graus=float(np.degrees(el['i']).mean()),
    periodo_perigeu_anos=float(p_peri), periodo_perigeu_real_anos=8.849,
    eclipses_reais=len(REAIS), eclipses_reproduzidos=casam, eclipses_modelo=len(mod),
    eclipses_modelo_lista=linhas, mare=tab,
)
# série de 19 anos, para comparar sizígia/quadratura com o planeta
np.savez_compressed(OUT / "_mare_terra.npz", t_h=t / 3600, eq=serie[0.0].astype("f4"),
                    lat45=serie[45.0].astype("f4"), novas_d=novas, cheias_d=ef.sizigias(np.pi))
(OUT / "resumo_lua_mare.json").write_text(json.dumps(resumo, indent=1, ensure_ascii=False))
