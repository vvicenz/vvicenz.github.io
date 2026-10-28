"""Teste terrestre A: insolação, duração do dia e equação do tempo.

Roda o módulo `mundo.orbita` com os parâmetros da Terra e compara com a
efeméride real do sol (astropy/ERFA) para 2024, em 9 latitudes.
Saída: dados/f1/terra/insolacao_comparacao.csv e números para o relatório.
"""
import json, sys, pathlib
import numpy as np
from astropy.time import Time
from astropy.coordinates import get_sun, EarthLocation, AltAz
import astropy.units as u

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from mundo.constantes import TERRA, S0_TERRA, UA
from mundo.orbita import Orbita, insolacao_diaria, duracao_dia

OUT = pathlib.Path(__file__).resolve().parents[1] / "dados/f1/terra"
OUT.mkdir(parents=True, exist_ok=True)

LATS = [-60, -45, -30, -15, 0, 15, 30, 45, 60, 66, 70, 78]
t0 = Time("2024-01-01T00:00:00", scale="utc")
passo_min = 5
n_dias = 366
amostras = np.arange(0, n_dias * 1440 + passo_min, passo_min) / 1440.0  # dias
tempos = t0 + amostras * u.day

sol = get_sun(tempos)
dist_ua = sol.distance.to(u.au).value

# solstício de dezembro de 2024, pela efeméride real (para ancorar o modelo)
from astropy.coordinates import GeocentricTrueEcliptic
lam_real = sol.transform_to(GeocentricTrueEcliptic(equinox=tempos)).lon.deg
k = np.where((lam_real[:-1] < 270) & (lam_real[1:] >= 270))[0][0]
f = (270 - lam_real[k]) / (lam_real[k + 1] - lam_real[k])
t_solst = amostras[k] + f * (amostras[k + 1] - amostras[k])
print("solstício dez 2024 (dias desde 1/jan 00 UTC):", t_solst)

orb = Orbita(TERRA, t_solsticio_dez=t_solst)
dias = np.arange(n_dias)

linhas, resumo = [], {}
for lat in LATS:
    loc = EarthLocation(lat=lat * u.deg, lon=0 * u.deg, height=0 * u.m)
    alt = sol.transform_to(AltAz(obstime=tempos, location=loc, pressure=0)).alt.deg
    # insolação real: integral do fluxo em cada dia (trapézios de 5 min)
    fluxo = S0_TERRA / dist_ua**2 * np.maximum(np.sin(np.radians(alt)), 0)
    por_dia = 1440 // passo_min
    q_real = np.array([np.trapezoid(fluxo[d * por_dia:(d + 1) * por_dia + 1], dx=1 / por_dia)
                       for d in dias])
    # duração do dia real: amostras acima de -0,833 grau, com interpolação nas bordas
    acima = alt > -0.833
    dl_real = []
    for d in dias:
        a = alt[d * por_dia:(d + 1) * por_dia + 1]
        s = (a > -0.833).astype(float)[:-1] * passo_min
        # correção linear nas transições
        for i in np.where(np.diff(a > -0.833))[0]:
            frac = (-0.833 - a[i]) / (a[i + 1] - a[i])
            s[i] = passo_min * (1 - frac) if a[i + 1] > a[i] else passo_min * frac
        dl_real.append(s.sum() / 60)
    dl_real = np.array(dl_real)
    # modelo: sol ao meio-dia de cada dia
    s_mod = orb.sol(dias + 0.5)
    q_mod = insolacao_diaria(np.radians(lat), s_mod["dec"], s_mod["r"], TERRA.s0)
    dl_mod = duracao_dia(np.radians(lat), s_mod["dec"])
    for d in dias:
        linhas.append((lat, d, q_real[d], q_mod[d], dl_real[d], dl_mod[d]))
    # fora dos dias de transição polar, onde o dia "começa" ou "acaba"
    ok = (dl_real > 0.5) & (dl_real < 23.5)
    resumo[lat] = dict(
        q_real_medio=float(q_real.mean()), q_mod_medio=float(q_mod.mean()),
        q_dif_max=float(np.abs(q_mod - q_real).max()),
        q_dif_rms=float(np.sqrt(np.mean((q_mod - q_real) ** 2))),
        dl_dif_max_min=float(np.abs(dl_mod - dl_real)[ok].max() * 60) if ok.any() else None,
        dl_real_max_h=float(dl_real.max()), dl_real_min_h=float(dl_real.min()),
        dl_mod_max_h=float(dl_mod.max()), dl_mod_min_h=float(dl_mod.min()),
    )
    print(lat, {k: round(v, 3) if v is not None else None for k, v in resumo[lat].items()})

# equação do tempo: real = AR média menos AR verdadeira, via hora do trânsito em lon 0
eot_real = []
loc = EarthLocation(lat=0 * u.deg, lon=0 * u.deg)
sub = np.arange(0, n_dias, 5)
for d in sub:
    tt = t0 + (d + np.linspace(11.5, 12.5, 721) / 24) * u.day
    a = get_sun(tt).transform_to(AltAz(obstime=tt, location=loc, pressure=0)).alt.deg
    i = np.argmax(a)
    eot_real.append((12 - (11.5 + i / 720)) * 60)   # min: sol passa antes do meio-dia -> positivo
eot_real = np.array(eot_real)
eot_mod = orb.sol(sub + 0.5)["eot_min"]
resumo["eot"] = dict(dif_max_min=float(np.abs(eot_mod - eot_real).max()),
                     real_max=float(eot_real.max()), real_min=float(eot_real.min()),
                     mod_max=float(eot_mod.max()), mod_min=float(eot_mod.min()))
print("EoT", resumo["eot"])

np.savetxt(OUT / "insolacao_comparacao.csv", np.array(linhas), delimiter=",", fmt="%.4f",
           header="lat_graus,dia_2024,q_real_wm2,q_modelo_wm2,dia_real_h,dia_modelo_h", comments="")
np.savetxt(OUT / "eot_comparacao.csv", np.c_[sub, eot_real, eot_mod], delimiter=",", fmt="%.3f",
           header="dia_2024,eot_real_min,eot_modelo_min", comments="")
(OUT / "resumo_insolacao.json").write_text(json.dumps(resumo, indent=1))
