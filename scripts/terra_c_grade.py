"""Teste terrestre C: grade geodésica do nível 1 com dados da Terra.

Constrói a grade f=300 (~25 km), mede uniformidade e conservação de área,
e amostra a máscara terra/mar GLOBE de 1 km da Terra: a fração de terra pela
grade tem de dar a da própria máscara (≈29 %), e a média sem pesos numa
grade lat/lon regular tem de dar errado (prova de que o peso por área importa).
"""
import json, sys, pathlib, time
import numpy as np
from global_land_mask import globe

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from mundo.grade import Grade
from mundo.constantes import R_PLANETA

RAIZ = pathlib.Path(__file__).resolve().parents[1]
OUT = RAIZ / "dados/f1"; (OUT / "terra").mkdir(parents=True, exist_ok=True)

res = {}
for f in (75, 150, 300):
    tic = time.time(); g = Grade(f); dt = time.time() - tic
    A = g.area * R_PLANETA**2 / 1e6                          # km2
    esp = g.comp_aresta * R_PLANETA / 1e3                    # km
    res[f] = dict(n_celulas=int(g.n), segundos=round(dt, 1), soma_area_sobre_4pi=float(g.area.sum() / (4 * np.pi)),
                  area_media_km2=float(A.mean()), area_min_km2=float(A.min()), area_max_km2=float(A.max()),
                  area_cv=float(A.std() / A.mean()), espacamento_medio_km=float(esp.mean()),
                  espacamento_min_km=float(esp.min()), espacamento_max_km=float(esp.max()),
                  pentagonos=int((g.grau == 5).sum()), hexagonos=int((g.grau == 6).sum()),
                  outros=int(((g.grau != 5) & (g.grau != 6)).sum()), sha256=g.hash())
    print(f, res[f])
    if f == 300:
        G = g

# quadratura: integrais de harmônicos que devem dar zero
lat = np.radians(G.lat); lon = np.radians(G.lon)
quad = {}
for nome, fun in [("P2(sen lat)", 1.5 * np.sin(lat) ** 2 - 0.5),
                  ("cos^3 lat cos 3 lon", np.cos(lat) ** 3 * np.cos(3 * lon)),
                  ("Y(20,7) aprox", np.cos(lat) ** 7 * np.sin(lat) ** 13 * np.sin(7 * lon))]:
    quad[nome] = float((fun * G.area).sum() / (np.abs(fun) * G.area).sum())
print("quadratura (integral/integral |f|):", quad)

# fração de terra da Terra
terra_grade = globe.is_land(G.lat, G.lon)
fr_grade_pesada = float((terra_grade * G.area).sum() / G.area.sum())
fr_grade_contagem = float(terra_grade.mean())
# verdade da própria máscara: grade regular de 0,05 grau com peso cos(lat)
la = np.arange(-89.975, 90, 0.05); lo = np.arange(-179.975, 180, 0.05)
soma = peso = ingenua = 0.0
for i in range(0, len(la), 200):
    LA, LO = np.meshgrid(la[i:i + 200], lo, indexing="ij")
    m = globe.is_land(LA, LO)
    w = np.cos(np.radians(LA))
    soma += (m * w).sum(); peso += w.sum(); ingenua += m.sum()
fr_mascara = float(soma / peso); fr_ingenua = float(ingenua / (len(la) * len(lo)))
print(f"terra: grade (área) {fr_grade_pesada:.4f}, grade (contagem) {fr_grade_contagem:.4f}, "
      f"máscara 0,05° (cos lat) {fr_mascara:.4f}, lat/lon sem peso {fr_ingenua:.4f}")
res["quadratura"] = quad
res["fracao_terra"] = dict(grade_por_area=fr_grade_pesada, grade_por_contagem=fr_grade_contagem,
                           mascara_cos_lat=fr_mascara, latlon_sem_peso=fr_ingenua)
(OUT / "terra/resumo_grade.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
np.savez_compressed(RAIZ / "dados/f1/terra/_grade300_terra.npz", lat=G.lat.astype("f4"),
                    lon=G.lon.astype("f4"), terra=terra_grade, area=G.area.astype("f4"))
