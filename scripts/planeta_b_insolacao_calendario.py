"""F1 · planeta v5: insolação, duração do dia, dias/noites polares, estações,
equação do tempo e calendário de 12 x 30 dias.

Usa `mundo.orbita`, validado no teste terrestre A. Para comparação, calcula
o mesmo com os parâmetros da Terra, alinhando os anos pela fração do ano
trópico a partir do solstício de dezembro.
"""
import json, sys, pathlib
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from mundo.constantes import PLANETA, TERRA
from mundo.orbita import Orbita, insolacao_diaria, duracao_dia, insolacao_instantanea
from mundo.sistema import T_SOLSTICIO_DEZ

RAIZ = pathlib.Path(__file__).resolve().parents[1]
OUT = RAIZ / "dados/f1/planeta"; OUT.mkdir(parents=True, exist_ok=True)
A = PLANETA; Y = A.ano_tropico_d
orb = Orbita(A, T_SOLSTICIO_DEZ)
dias = np.arange(360)
sol = orb.sol(dias + 0.5)
LATS = np.arange(-90, 91, 1)
latr = np.radians(LATS)[:, None]

Q = insolacao_diaria(latr, sol["dec"][None], sol["r"][None], A.s0)          # (181, 360)
DL = duracao_dia(latr, sol["dec"][None])
CIV = duracao_dia(latr, sol["dec"][None], -6.0)

# Terra no mesmo "ano normalizado" (dia do planeta -> mesma fração do ano após o solstício)
orbT = Orbita(TERRA, 355.39)          # solstício de dez/2024 em dias desde 1/jan (teste A)
tT = 355.39 + ((dias + 0.5) - T_SOLSTICIO_DEZ) / Y * TERRA.ano_tropico_d
solT = orbT.sol(tT)
QT = insolacao_diaria(latr, solT["dec"][None], solT["r"][None], TERRA.s0)
DLT = duracao_dia(latr, solT["dec"][None])


def salvar_matriz(nome, M, fmt="%.2f"):
    cab = "dia_do_ano," + ",".join(f"lat{l:+d}" for l in LATS)
    np.savetxt(OUT / nome, np.c_[dias + 1, M.T], delimiter=",", fmt=fmt, header=cab, comments="")


salvar_matriz("insolacao_diaria_wm2.csv", Q, "%.1f")
salvar_matriz("duracao_dia_h.csv", DL, "%.3f")
salvar_matriz("duracao_dia_com_crepusculo_civil_h.csv", CIV, "%.3f")

# instantes astronômicos do ano
marcos = {}
for nome, lam in (("equinócio de março", 0), ("solstício de junho", 90),
                  ("equinócio de setembro", 180), ("solstício de dezembro", 270)):
    marcos[nome] = float(orb.instante_longitude(lam))
marcos["periélio"] = float(orb.t_peri)
marcos["afélio"] = float((orb.t_peri + Y / 2) % Y)


def civil(t):
    m = int(t // 30) + 1; d = int(t % 30) + 1
    hm = int(round((t % 1) * 1440)); return f"{d:02d}/{m:02d} {hm // 60:02d}:{hm % 60:02d}"


tempos = sorted(marcos.items(), key=lambda kv: kv[1])
ordem = ["equinócio de março", "solstício de junho", "equinócio de setembro", "solstício de dezembro"]
estacoes = {}
for i, nome in enumerate(ordem):
    t1 = marcos[nome]; t2 = marcos[ordem[(i + 1) % 4]]
    estacoes[nome] = float((t2 - t1) % Y)
nomes_norte = dict(zip(ordem, ["primavera", "verão", "outono", "inverno"]))

# dias e noites polares (dias civis com sol sempre acima / sempre abaixo do horizonte)
polar = []
for i, l in enumerate(LATS):
    polar.append((l, int((DL[i] >= 23.999).sum()), int((DL[i] <= 0.001).sum()),
                  int((CIV[i] <= 0.001).sum()), int((DLT[i] >= 23.999).sum()), int((DLT[i] <= 0.001).sum())))
np.savetxt(OUT / "dias_noites_polares.csv", np.array(polar), delimiter=",", fmt="%d",
           header="lat,dias_sol_24h,dias_sem_sol,dias_sem_crepusculo_civil,terra_dias_sol_24h,terra_dias_sem_sol",
           comments="")

# insolação horária nas datas-chave
LAT_H = [78, 70, 60, 45, 30, 15, 0, -15]
horas = np.arange(0, 24.01, 0.5)
with open(OUT / "insolacao_horaria_wm2.csv", "w") as f:
    f.write("marco,lat," + ",".join(f"h{h:04.1f}" for h in horas) + "\n")
    for nome in ordem:
        s = orb.sol(marcos[nome])
        for l in LAT_H:
            v = insolacao_instantanea(np.radians(l), s["dec"], s["r"], horas, A.s0)
            f.write(f"{nome},{l}," + ",".join(f"{x:.1f}" for x in v) + "\n")

# calendário: um ano (todos os anos são iguais em sol e em fase média da lua)
LAT_CAL = [78, 70, 60, 45, 30, 15, 0, -15]
with open(OUT / "calendario.csv", "w") as f:
    f.write("dia_do_ano,mes,dia,idade_lua_media_d,fase_media,iluminacao_media,lon_sol_graus,"
            "declinacao_graus,dist_sol_rel,eq_tempo_min,marco,"
            + ",".join(f"dia_h_lat{l:+d}" for l in LAT_CAL) + ","
            + ",".join(f"insol_lat{l:+d}" for l in LAT_CAL) + "\n")
    for d in dias:
        idade = (d + 0.5) % 30
        ilum = (1 - np.cos(2 * np.pi * idade / 30)) / 2
        fase = ["nova", "crescente", "quarto crescente", "gibosa crescente", "cheia",
                "gibosa minguante", "quarto minguante", "minguante"][int(((idade / 30) * 8 + 0.5) % 8)]
        marco = ";".join(n for n, tt in marcos.items() if int(tt) == d)
        li = [int(np.where(LATS == l)[0][0]) for l in LAT_CAL]
        f.write(f"{d+1},{d//30+1},{d%30+1},{idade:.1f},{fase},{ilum:.3f},{np.degrees(sol['lam'][d]):.3f},"
                f"{np.degrees(sol['dec'][d]):.3f},{sol['r'][d]:.5f},{sol['eot_min'][d]:.2f},{marco},"
                + ",".join(f"{DL[i, d]:.2f}" for i in li) + ","
                + ",".join(f"{Q[i, d]:.1f}" for i in li) + "\n")

anual = Q.mean(1); anualT = QT.mean(1)
w = np.cos(latr[:, 0])
res = dict(
    marcos={k: dict(t_dias=v, data=civil(v)) for k, v in marcos.items()},
    estacoes_norte_dias={nomes_norte[k]: v for k, v in estacoes.items()},
    insolacao_media_global_wm2=float((anual * w).sum() / w.sum()),
    insolacao_media_global_terra_wm2=float((anualT * w).sum() / w.sum()),
    insolacao_anual_equador=float(anual[90]), insolacao_anual_polo_norte=float(anual[180]),
    insolacao_anual_polo_sul=float(anual[0]),
    insolacao_max_diaria=dict(valor=float(Q.max()), lat=int(LATS[np.unravel_index(Q.argmax(), Q.shape)[0]]),
                              dia=int(np.unravel_index(Q.argmax(), Q.shape)[1] + 1)),
    polo_norte_solsticio_jun=float(Q[180, int(marcos["solstício de junho"])]),
    polo_sul_solsticio_dez=float(Q[0, int(marcos["solstício de dezembro"])]),
    contraste_hemisferios_max_insolacao_polar=float(Q[0].max() / Q[180].max()),
    eq_tempo_min=[float(sol["eot_min"].min()), float(sol["eot_min"].max())],
    dia_mais_longo_h={int(l): float(DL[i].max()) for i, l in enumerate(LATS) if l in LAT_CAL},
    dia_mais_curto_h={int(l): float(DL[i].min()) for i, l in enumerate(LATS) if l in LAT_CAL},
    circulo_polar_lat=float(90 - A.obliquidade_graus), tropico_lat=A.obliquidade_graus,
)
(OUT / "resumo_insolacao_calendario.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
print(json.dumps(res, indent=1, ensure_ascii=False))
np.savez_compressed(OUT / "_insolacao.npz", Q=Q, QT=QT, DL=DL, DLT=DLT, CIV=CIV, lats=LATS,
                    eot=sol["eot_min"], dec=sol["dec"], eotT=solT["eot_min"], decT=solT["dec"])
