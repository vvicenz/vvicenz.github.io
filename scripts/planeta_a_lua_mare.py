"""F1 · planeta v5: lua, fases, eclipses e maré (três corpos, 100 anos).

Mesmo código do teste terrestre B, agora com as decisões da seção 3.
Também roda 6 sementes extras só para mostrar que a FORMA (frequência e
mistura de eclipses) não depende da semente; as datas dependem.
"""
import json, sys, pathlib, time
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from mundo.constantes import (G, DIA, PLANETA, R_PLANETA, R_LUA, R_SOL, M_PLANETA, M_LUA)
from mundo.sistema import Sistema
from mundo.nbody import estado_para_elementos
from mundo.lua import eclipses, lon_lat
from mundo.mare import altura_equilibrio, velocidades, ajuste_harmonico

RAIZ = pathlib.Path(__file__).resolve().parents[1]
OUT = RAIZ / "dados/f1/planeta"; OUT.mkdir(parents=True, exist_ok=True)
ANOS = 100
A = PLANETA; Y = A.ano_tropico_d


def data_civil(t):
    """t (d) -> (ano, mês, dia, hh:mm) do calendário 12 x 30."""
    ano = int(np.floor(t / Y)); r = t - ano * Y
    mes = int(r // 30) + 1; dia = int(r % 30) + 1
    m = int(round((r % 1) * 1440)); hh, mm = divmod(m, 60)
    if hh == 24:
        hh = 23; mm = 59
    return ano, mes, dia, f"{hh:02d}:{mm:02d}"


def estatistica_eclipses(lista, anos):
    tipos = {}
    for e in lista:
        k = f"{e['corpo']}:{e['tipo'].split()[0]}"
        tipos[k] = tipos.get(k, 0) + 1
    n_sol = sum(v for k, v in tipos.items() if k.startswith("sol"))
    n_lua = sum(v for k, v in tipos.items() if k.startswith("lua"))
    por_ano = np.bincount([int(e["t"] // Y) for e in lista], minlength=anos)[:anos]
    return dict(por_seculo=tipos, sol_por_ano=n_sol / anos, lua_por_ano=n_lua / anos,
                eclipses_ano_min=int(por_ano.min()), eclipses_ano_max=int(por_ano.max()))


# ---------------------------------------------------------------- semente provisória
sis = Sistema()
print("ajuste da lua (semente provisória):")
tic = time.time()
TB = json.loads((RAIZ / "dados/f1/terra/resumo_lua_mare.json").read_text())
sis.ajustar_forma(TB["lua_e_media"], np.radians(TB["lua_i_media_graus"]))
sis.ajustar_lua(anos=12)
resid_ajuste = sis.ajustar_lua(anos=ANOS, iter_=3)
a_lua_ajustado, delta_ajustado = sis.a_lua, sis.delta
sis.integrar(ANOS)
print(f"integração {ANOS} anos: {time.time() - tic:.1f} s")
ef = sis.ef
t = sis.t_d

# fases
fases = {}
for nome, alvo in (("nova", 0.0), ("quarto crescente", np.pi / 2), ("cheia", np.pi),
                   ("quarto minguante", 3 * np.pi / 2)):
    fases[nome] = ef.sizigias(alvo)
novas, cheias = fases["nova"], fases["cheia"]
n = np.round(novas / 30.0)
S_med, t0_med = np.polyfit(n, novas, 1)
desvio_nova_h = (novas - 30.0 * n) * 24
desvio_cheia_h = (cheias - (30.0 * np.round((cheias - 15) / 30) + 15)) * 24
print(f"mês sinódico médio em 100 anos: {S_med:.6f} d; lua nova verdadeira - início do mês: "
      f"{desvio_nova_h.min():+.1f} a {desvio_nova_h.max():+.1f} h")

linhas = []
for nome, tt in fases.items():
    for x in tt:
        a, m_, d_, hm = data_civil(x)
        linhas.append((x, nome, a, m_, d_, hm))
linhas.sort()
with open(OUT / "fases_lua_100anos.csv", "w") as f:
    f.write("t_dias,fase,ano,mes,dia,hora\n")
    for x, nome, a, m_, d_, hm in linhas:
        f.write(f"{x:.4f},{nome},{a},{m_},{d_},{hm}\n")

# elementos médios da órbita da lua
el = estado_para_elementos(G * (M_PLANETA + M_LUA), sis.mvec, sis.vlua)
anos_t = t / Y
taxa_nodo = np.polyfit(anos_t, np.unwrap(el["Omega"]), 1)[0]       # rad/ano (inercial)
taxa_peri = np.polyfit(anos_t, np.unwrap(el["varpi"]), 1)[0]
dist = np.linalg.norm(sis.mvec, axis=1)
dist_sol = np.linalg.norm(sis.s, axis=1)
psi_ano = sis.psi_dot * Y * DIA
# meses: sideral, trópico, draconítico, anomalístico
n_lua = 2 * np.pi / 30.0 + 2 * np.pi / A.derivados["ano_sideral_d"]   # rad/d inercial
mes_drac = 2 * np.pi / (n_lua - taxa_nodo / Y)
mes_anom = 2 * np.pi / (n_lua - taxa_peri / Y)
ano_eclipse = 2 * np.pi / (2 * np.pi / A.derivados["ano_sideral_d"] - taxa_nodo / Y)
# declinação da lua (equador da data) e o ciclo de paralisação
m_eq = sis.para_equador(sis.mvec)
dec_lua = np.degrees(np.arcsin(m_eq[:, 2] / dist))
mes_idx = (t // 30).astype(int)
dec_max_mes = np.array([np.abs(dec_lua[mes_idx == k]).max() for k in range(ANOS * 12)])
diam_lua = np.degrees(2 * np.arcsin(R_LUA / dist)) * 60
diam_sol = np.degrees(2 * np.arcsin(R_SOL / dist_sol)) * 60

# eclipses
ecl = eclipses(ef, R_PLANETA, R_LUA, R_SOL)
with open(OUT / "eclipses_100anos.csv", "w") as f:
    f.write("t_dias,corpo,tipo,ano,mes,dia,hora,gama_raios,grandeza\n")
    for e in ecl:
        a, m_, d_, hm = data_civil(e["t"])
        f.write(f"{e['t']:.4f},{e['corpo']},{e['tipo']},{a},{m_},{d_},{hm},{e['gama']:.4f},{e['grandeza']:.4f}\n")
est = estatistica_eclipses(ecl, ANOS)
print("eclipses (semente provisória):", est)

# maré de equilíbrio
s_eq = sis.para_equador(sis.s)
theta = sis.angulo_sideral(t)
w = A.derivados["omega_rot"]
h_dot = 2 * np.pi / (Y * DIA)
s_dot = h_dot + 2 * np.pi / (30.0 * DIA)
p_dot = (taxa_peri + psi_ano) / (Y * DIA)
vel = velocidades(w, s_dot, h_dot, p_dot)
amps, serie = {}, {}
for lat in (0.0, 45.0):
    eta = altura_equilibrio(lat, 0.0, [(A.m_estrela, s_eq), (M_LUA, m_eq)], theta, R_PLANETA, M_PLANETA)
    amps[lat], rms = ajuste_harmonico(t * DIA, eta, vel)
    serie[lat] = eta
    print(f"maré lat {lat}: resíduo {rms*100:.2f} cm")
constit = {}
for k, v in vel.items():
    lat = 0.0 if k.endswith("2") else 45.0
    constit[k] = dict(periodo_h=float(2 * np.pi / v / 3600), amplitude_m=amps[lat][k],
                      latitude_de_referencia=lat)
with open(OUT / "mare_constituintes.csv", "w") as f:
    f.write("constituinte,periodo_h,amplitude_equilibrio_m,lat_ref\n")
    for k, c in constit.items():
        f.write(f"{k},{c['periodo_h']:.5f},{c['amplitude_m']:.5f},{c['latitude_de_referencia']:.0f}\n")
# amplitude no equador: amplitude semidiurna local em cada sizígia e quadratura
def amplitude_local(tc, eta):
    i = np.searchsorted(t, tc)
    j = slice(max(i - 13, 0), i + 13)
    return (eta[j].max() - eta[j].min()) / 2
sizig = np.sort(np.r_[novas, cheias]); quadr = np.sort(np.r_[fases["quarto crescente"], fases["quarto minguante"]])
amp_siz = np.array([amplitude_local(x, serie[0.0]) for x in sizig[1:-1]])
amp_qua = np.array([amplitude_local(x, serie[0.0]) for x in quadr[1:-1]])
# marés de perigeu-sizígia: lua a menos de 1 dia do perigeu na sizígia
d_siz = np.interp(sizig, t, dist)
h2 = t <= 2 * Y
np.savez_compressed(OUT / "_series_planeta.npz", t2_d=t[h2], eta2=serie[0.0][h2].astype("f4"),
                    t_d=t[::3].astype("f8"),
                    eta_eq=serie[0.0][::3].astype("f4"), eta45=serie[45.0][::3].astype("f4"),
                    dec_lua=dec_lua[::3].astype("f4"), dist_lua=dist[::3].astype("f4"),
                    novas=novas, cheias=cheias, quartos=quadr, dec_max_mes=dec_max_mes,
                    desvio_nova_h=desvio_nova_h, desvio_cheia_h=desvio_cheia_h,
                    amp_siz=amp_siz, amp_qua=amp_qua, sizig=sizig[1:-1], quadr=quadr[1:-1],
                    d_siz=d_siz, diam_lua=diam_lua[::24], diam_sol=diam_sol[::24])

# ---------------------------------------------------------------- outras sementes
sementes = {}
for sem in range(1, 7):
    s2 = Sistema(semente=sem)
    s2.a_lua, s2.delta = a_lua_ajustado, delta_ajustado
    s2.e_lua, s2.i_lua = sis.e_lua, sis.i_lua
    s2.ajustar_forma(TB["lua_e_media"], np.radians(TB["lua_i_media_graus"]), iter_=2, verbose=False)
    s2.ajustar_lua(anos=40, iter_=3, verbose=False)
    s2.integrar(ANOS, passo_h=1.0)
    e2 = eclipses(s2.ef, R_PLANETA, R_LUA, R_SOL)
    sementes[sem] = estatistica_eclipses(e2, ANOS)
    print(f"semente {sem}: {sementes[sem]}")

res = dict(
    semente=sis.semente, e_osculador_inicial=float(sis.e_lua), i_osculador_inicial_graus=float(np.degrees(sis.i_lua)), nodo_inicial_graus=float(np.degrees(sis.Omega0)),
    perigeu_inicial_graus=float(np.degrees(sis.varpi0)),
    a_lua_osculador_inicial_km=a_lua_ajustado / 1e3,
    lua_distancia_media_km=float(dist.mean() / 1e3), lua_perigeu_min_km=float(dist.min() / 1e3),
    lua_apogeu_max_km=float(dist.max() / 1e3),
    lua_e_media=float(el["e"].mean()), lua_i_media_graus=float(np.degrees(el["i"]).mean()),
    mes_sinodico_medio_d=float(S_med), mes_sideral_d=float(2 * np.pi / n_lua),
    mes_draconitico_d=float(mes_drac), mes_anomalistico_d=float(mes_anom),
    ano_de_eclipses_d=float(ano_eclipse),
    periodo_nodo_anos=float(2 * np.pi / taxa_nodo), periodo_perigeu_anos=float(2 * np.pi / taxa_peri),
    lua_nova_desvio_h=[float(desvio_nova_h.min()), float(desvio_nova_h.max()), float(np.abs(desvio_nova_h).mean())],
    lua_cheia_desvio_h=[float(desvio_cheia_h.min()), float(desvio_cheia_h.max())],
    declinacao_lua_max_mensal_graus=[float(dec_max_mes.min()), float(dec_max_mes.max())],
    diametro_lua_arcmin=[float(diam_lua.min()), float(diam_lua.mean()), float(diam_lua.max())],
    diametro_sol_arcmin=[float(diam_sol.min()), float(diam_sol.mean()), float(diam_sol.max())],
    eclipses=est, eclipses_outras_sementes=sementes,
    mare_constituintes=constit,
    mare_equador_amplitude_sizigia_m=[float(amp_siz.min()), float(amp_siz.mean()), float(amp_siz.max())],
    mare_equador_amplitude_quadratura_m=[float(amp_qua.min()), float(amp_qua.mean()), float(amp_qua.max())],
    lunacao_ajuste_residuo=dict(S_menos_30_s=float(resid_ajuste[0] * 86400), fase_h=float(resid_ajuste[1] * 24)),
)
(OUT / "resumo_lua_mare.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
for k, v in res.items():
    if k not in ("mare_constituintes", "eclipses_outras_sementes"):
        print(k, v)
