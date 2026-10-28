"""Gráficos da F1 (out/f1/*.png) a partir de dados/f1/."""
import json, sys, pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
RAIZ = pathlib.Path(__file__).resolve().parents[1]
D = RAIZ / "dados/f1"; OUT = RAIZ / "out/f1"; OUT.mkdir(parents=True, exist_ok=True)

# paleta de referência (skill dataviz), modo claro
SUP, TXT, TXT2, GRADE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3de"
S1, S2, S3, S4, S5, S6, S7, S8 = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                                  "#e87ba4", "#008300", "#6250d6", "#e34948")
AZUL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#104281", "#0d366b"]
seq_azul = LinearSegmentedColormap.from_list("azul", ["#f3f8fe"] + AZUL)
seq_sol = LinearSegmentedColormap.from_list("sol", ["#1e1a17", "#5c2f17", "#a8461e", "#eb6834",
                                                    "#f6a76f", "#fde7d3"])
div = LinearSegmentedColormap.from_list("div", ["#104281", "#3987e5", "#9ec5f4", "#f0efec",
                                               "#f4a9a8", "#e34948", "#9b1c1c"])
plt.rcParams.update({
    "figure.facecolor": SUP, "axes.facecolor": SUP, "savefig.facecolor": SUP,
    "axes.edgecolor": GRADE, "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
    "text.color": TXT, "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "lines.linewidth": 2, "axes.titlepad": 20, "legend.frameon": False, "figure.dpi": 110,
})
MESES = [f"{m}" for m in range(1, 13)]


def eixo_meses(ax, y=False):
    tk = np.arange(0, 361, 30)
    (ax.set_yticks if y else ax.set_xticks)(tk + 15 if False else tk)
    (ax.set_yticklabels if y else ax.set_xticklabels)([""] * len(tk))
    pos = np.arange(15, 360, 30)
    if y:
        ax.set_yticks(pos, minor=True); ax.set_yticklabels(MESES, minor=True)
    else:
        ax.set_xticks(pos, minor=True); ax.set_xticklabels(MESES, minor=True)
    ax.tick_params(which="minor", length=0)
    (ax.set_ylabel if y else ax.set_xlabel)("mês do calendário (12 × 30 dias)")


def salvar(fig, nome):
    fig.savefig(OUT / nome, bbox_inches="tight", dpi=130); plt.close(fig); print("ok", nome)


def subtitulo(ax, txt):
    import re
    txt = re.sub(r"(\d)\.(\d)", r"\1,\2", txt)        # vírgula decimal
    ax.text(0, 1.02, txt, transform=ax.transAxes, color=TXT2, fontsize=9, va="bottom")


ins = np.load(D / "planeta/_insolacao.npz")
Q, QT, DL, DLT, CIV, LATS = ins["Q"], ins["QT"], ins["DL"], ins["DLT"], ins["CIV"], ins["lats"]
RI = json.loads((D / "planeta/resumo_insolacao_calendario.json").read_text())
marcos = {k: v["t_dias"] for k, v in RI["marcos"].items()}
dias = np.arange(360) + 0.5

# ------------------------------------------------------------ 01 insolação lat x dia
fig, ax = plt.subplots(figsize=(10, 5.6))
im = ax.pcolormesh(np.arange(361), np.arange(-90.5, 91), Q, cmap=seq_sol, vmin=0, vmax=570, shading="flat")
cs = ax.contour(dias, LATS, Q, levels=[100, 200, 300, 400, 500], colors="#fcfcfb", linewidths=0.6, alpha=0.7)
ax.clabel(cs, fmt="%d", fontsize=7, colors="#fcfcfb")
ax.contour(dias, LATS, DL, levels=[0.001], colors=AZUL[1], linewidths=1.2, linestyles="--")
for nome, tt in marcos.items():
    if "equin" in nome or "solst" in nome:
        ax.axvline(tt, color="#fcfcfb", lw=0.8, alpha=0.6)
ax.axhspan(-15, 78, xmin=0, xmax=0.012, color=S3)
ax.text(4, 80, "faixa do continente de jogo (15° S–78° N)", fontsize=8, color="#fcfcfb")
ax.text(110, -84, "noite polar (tracejado)", fontsize=8, color=AZUL[1])
ax.text(300, 84, "noite polar", fontsize=8, color=AZUL[1])
ax.set_yticks(range(-90, 91, 30)); ax.set_ylabel("latitude (°)"); ax.grid(False)
eixo_meses(ax)
cb = fig.colorbar(im, ax=ax, pad=0.015); cb.set_label("W/m², média de 24 h no topo da atmosfera")
ax.set_title("Insolação diária por latitude ao longo do ano")
subtitulo(ax, "Linhas verticais: equinócios e solstícios. Periélio em 04/01: o verão do sul recebe ~7 % mais no polo.")
salvar(fig, "f1_01_insolacao_latitude_dia.png")

# ------------------------------------------------------------ 02 diferença com a Terra
fig, ax = plt.subplots(figsize=(10, 4.6))
dif = Q - QT
lim = np.abs(dif).max()
im = ax.pcolormesh(np.arange(361), np.arange(-90.5, 91), dif, cmap=div, norm=TwoSlopeNorm(0, -lim, lim))
ax.set_yticks(range(-90, 91, 30)); ax.set_ylabel("latitude (°)"); ax.grid(False); eixo_meses(ax)
cb = fig.colorbar(im, ax=ax, pad=0.015); cb.set_label("planeta − Terra (W/m²)")
ax.set_title("Planeta menos Terra, no mesmo ponto do ano")
subtitulo(ax, f"Diferença máxima {lim:.1f} W/m² ({lim / Q.max() * 100:.1f} % do pico): obliquidade 23,5° × 23,44° e e = 0,017 × 0,0167.")
salvar(fig, "f1_02_insolacao_diferenca_terra.png")

# ------------------------------------------------------------ 03 anual por latitude
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.axvspan(-15, 78, color=S3, alpha=0.08, lw=0)
ax.text(31, 20, "continente de jogo", color=TXT2, fontsize=9, ha="center")
iJ = int(marcos["solstício de junho"]); iD = int(marcos["solstício de dezembro"])
ax.plot(LATS, Q.mean(1), color=S1, label="média anual")
ax.plot(LATS, Q[:, iJ], color=S2, label="solstício de junho (20/06)")
ax.plot(LATS, Q[:, iD], color=S7, label="solstício de dezembro (21/12)")
ax.plot(LATS, QT.mean(1), color=TXT, lw=1, ls=(0, (2, 2)), label="Terra, média anual")
for y, c, txt in ((Q.mean(1)[90], S1, "anual"), ):
    pass
ax.set_xlim(-90, 90); ax.set_xticks(range(-90, 91, 15)); ax.set_ylim(0, 600)
ax.set_xlabel("latitude (°)"); ax.set_ylabel("W/m²")
ax.legend(loc="upper center", ncol=2, fontsize=9)
ax.set_title("Insolação por latitude: média anual e solstícios")
subtitulo(ax, f"Média global {RI['insolacao_media_global_wm2']:.1f} W/m² (= S₀/4 corrigido pela excentricidade). "
              "No solstício o polo recebe mais que o equador.")
salvar(fig, "f1_03_insolacao_anual_latitude.png")

# ------------------------------------------------------------ 04 duração do dia
fig, ax = plt.subplots(figsize=(10, 5.2))
LAT_L = [78, 70, 60, 45, 30, 15, 0, -15]
cores = ["#0d366b", "#104281", "#184f95", "#256abf", "#3987e5", "#6da7ec", "#86b6ef", S2]
for l, c in zip(LAT_L, cores):
    i = int(np.where(LATS == l)[0][0])
    ax.plot(dias, DL[i], color=c, lw=2)
    yv = DL[i][int(marcos["solstício de junho"])]
    ax.text(172, yv + (0.35 if l != 70 else -0.9), f"{abs(l)}° {'N' if l > 0 else ('S' if l < 0 else '')}",
            color=TXT, fontsize=8.5, ha="left")
for nome, tt in marcos.items():
    if "equin" in nome or "solst" in nome:
        ax.axvline(tt, color=TXT2, lw=0.6, ls=":")
ax.set_ylim(0, 24.5); ax.set_yticks(range(0, 25, 3)); ax.set_ylabel("horas de sol (nascer ao pôr, com refração)")
eixo_meses(ax); ax.set_xlim(0, 360)
ax.set_title("Duração do dia nas latitudes do continente")
subtitulo(ax, "Azul do mais escuro (78° N) ao mais claro (equador); laranja: 15° S, com as estações invertidas.")
salvar(fig, "f1_04_duracao_do_dia.png")

# ------------------------------------------------------------ 05 dias e noites polares
pol = np.loadtxt(D / "planeta/dias_noites_polares.csv", delimiter=",", skiprows=1)
fig, ax = plt.subplots(figsize=(9, 4.4))
m = np.abs(pol[:, 0]) >= 60
for hem, sinal, ls in (("norte", 1, "-"), ("sul", -1, (0, (4, 2)))):
    k = m & (np.sign(pol[:, 0]) == sinal)
    la = np.abs(pol[k, 0])
    ax.plot(la, pol[k, 1], color=S4, ls=ls, label=f"sol de 24 h ({hem})")
    ax.plot(la, pol[k, 2], color=S1, ls=ls, label=f"sem sol ({hem})")
    ax.plot(la, pol[k, 3], color=S7, ls=ls, lw=1.2, label=f"sem crepúsculo civil ({hem})")
ax.axvline(78, color=TXT2, lw=0.8, ls=":"); ax.text(78.3, 160, "limite norte do\ncontinente (78° N)", fontsize=8, color=TXT2)
ax.axvline(66.5, color=TXT2, lw=0.8, ls=":"); ax.text(66.8, 160, "círculo polar\n(66,5°)", fontsize=8, color=TXT2)
ax.set_xlim(60, 90); ax.set_xlabel("latitude (°, norte ou sul)"); ax.set_ylabel("dias por ano")
ax.legend(fontsize=8, ncol=2, loc="lower right")
ax.set_title("Dias e noites polares")
subtitulo(ax, "A refração faz o sol de meia-noite começar abaixo do círculo polar; o sul tem um pouco menos dias de sol (periélio no seu verão, verão mais curto).")
salvar(fig, "f1_05_dias_noites_polares.png")

# ------------------------------------------------------------ 06 insolação horária
lin = [l.strip().split(",") for l in open(D / "planeta/insolacao_horaria_wm2.csv")]
cab = lin[0]; horas = np.array([float(h[1:]) for h in cab[2:]])
fig, axs = plt.subplots(1, 4, figsize=(13, 3.8), sharey=True)
nomes = ["equinócio de março", "solstício de junho", "equinócio de setembro", "solstício de dezembro"]
LH = [78, 60, 45, 30, 0, -15]; cH = ["#0d366b", "#184f95", "#256abf", "#3987e5", "#86b6ef", S2]
for ax, nome in zip(axs, nomes):
    for l, c in zip(LH, cH):
        row = [r for r in lin[1:] if r[0] == nome and int(r[1]) == l][0]
        ax.plot(horas, np.array(row[2:], float), color=c, label=f"{abs(l)}°{'N' if l > 0 else ('S' if l < 0 else '')}")
    ax.set_title(nome + f"\n({RI['marcos'][nome]['data'][:5]})", fontsize=10)
    ax.set_xticks(range(0, 25, 6)); ax.set_xlim(0, 24); ax.set_xlabel("hora solar")
axs[0].set_ylabel("W/m² (topo da atmosfera)")
axs[-1].legend(fontsize=8, loc="upper right")
fig.suptitle("Insolação hora a hora nas datas-chave", x=0.02, y=1.1, ha="left", fontweight="bold")
salvar(fig, "f1_06_insolacao_horaria.png")

# ------------------------------------------------------------ 07 equação do tempo + analema
eot, dec = ins["eot"], np.degrees(ins["dec"])
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw=dict(width_ratios=[2.2, 1]))
ax.plot(dias, eot, color=S1, label="planeta")
ax.plot(dias, ins["eotT"], color=TXT, lw=1, ls=(0, (2, 2)), label="Terra")
ax.axhline(0, color=TXT2, lw=0.8)
ax.set_ylabel("relógio de sol − relógio médio (min)"); eixo_meses(ax); ax.set_xlim(0, 360); ax.legend()
ax.set_title("Equação do tempo")
subtitulo(ax, f"De {eot.min():+.1f} a {eot.max():+.1f} min: o meio-dia do relógio de sol oscila ±¼ h ao longo do ano.")
ax2.plot(-eot / 4, dec, color=S1, lw=1.5)
for d0 in range(0, 360, 30):
    ax2.plot(-eot[d0] / 4, dec[d0], "o", ms=5, color=S1, mec=SUP, mew=1.5)
    ax2.annotate(f"{d0 // 30 + 1}", (-eot[d0] / 4, dec[d0]), xytext=(5, 0), textcoords="offset points", fontsize=7, color=TXT2)
ax2.set_xlabel("deslocamento do sol ao meio-dia médio (°)"); ax2.set_ylabel("declinação (°)")
ax2.set_title("Analema (sol às 12:00 médio)")
salvar(fig, "f1_07_equacao_do_tempo.png")

# ------------------------------------------------------------ 08 calendário
fig, ax = plt.subplots(figsize=(13, 6.2))
i45 = int(np.where(LATS == 45)[0][0])
C = DL[i45].reshape(12, 30)
im = ax.imshow(C, cmap=seq_azul, aspect="auto", extent=(0.5, 30.5, 12.5, 0.5))
ax.grid(False)
ax.set_xticks(range(1, 31)); ax.set_yticks(range(1, 13)); ax.set_xlabel("dia do mês"); ax.set_ylabel("mês")
# fases da lua (média): nova no dia 1, quarto crescente 8/9, cheia 16, minguante 23/24
from matplotlib.patches import Circle, Wedge
for d in range(1, 31):
    idade = d - 0.5
    ilum = (1 - np.cos(2 * np.pi * idade / 30)) / 2
    x, y = d, 0.0
    ax.add_patch(Circle((x, y), 0.32, color="#2b2b2b", clip_on=False, zorder=4))
    # parte iluminada: semicírculo + elipse
    from matplotlib.patches import Ellipse
    lado = 1 if idade < 15 else -1
    ax.add_patch(Wedge((x, y), 0.32, -90 if lado > 0 else 90, 90 if lado > 0 else 270, color="#f2eee2", zorder=5, clip_on=False))
    k = abs(1 - 2 * ilum)
    cor = "#2b2b2b" if ilum < 0.5 else "#f2eee2"
    ax.add_patch(Ellipse((x, y), 0.64 * k, 0.64, color=cor, zorder=6, clip_on=False))
ax.set_ylim(12.5, -0.6)
for nome, tt in marcos.items():
    mm = int(tt // 30) + 1; dd = int(tt % 30) + 1
    curto = {"equinócio de março": "equinócio", "solstício de junho": "solstício", "equinócio de setembro": "equinócio",
             "solstício de dezembro": "solstício", "periélio": "periélio", "afélio": "afélio"}[nome]
    ax.plot(dd, mm, marker="*", ms=13, color=S4, mec=TXT, mew=0.6, zorder=7)
    ax.annotate(curto, (dd, mm), xytext=(8, -9), textcoords="offset points", fontsize=8, color=TXT,
                bbox=dict(boxstyle="round,pad=0.15", fc=SUP, ec="none", alpha=0.85))
cb = fig.colorbar(im, ax=ax, pad=0.01); cb.set_label("horas de sol a 45° N")
ax.set_title("Calendário: 12 meses × 30 dias, cada mês uma lunação", pad=34)
subtitulo(ax, "Linha de cima: fase média da lua, a mesma em todo mês (nova no dia 1, cheia no 16). Cor: horas de sol a 45° N.")
ax.texts[-1].set_y(1.075)
salvar(fig, "f1_08_calendario.png")

# ------------------------------------------------------------ lua, eclipses e maré
RL = json.loads((D / "planeta/resumo_lua_mare.json").read_text())
ser = np.load(D / "planeta/_series_planeta.npz")
Y = 360.0
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.plot(ser["novas"] / Y, ser["desvio_nova_h"], ".", ms=3, color=S1, label="lua nova verdadeira − dia 1, 00:00")
ax.plot(ser["cheias"] / Y, ser["desvio_cheia_h"], ".", ms=3, color=S2, label="lua cheia verdadeira − dia 16, 00:00")
ax.axhline(0, color=TXT2, lw=0.8)
ax.set_xlabel("ano"); ax.set_ylabel("horas")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=9, markerscale=3)
ax.set_title("Os meses ficam em fase com a lua por 100 anos")
subtitulo(ax, f"Mês sinódico médio {RL['mes_sinodico_medio_d']:.5f} d. A lua verdadeira oscila ±{np.abs(ser['desvio_nova_h']).max():.0f} h "
              "em torno da média (órbita excêntrica), sem deriva.")
salvar(fig, "f1_09_lua_fase_e_calendario.png")

fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
meses = np.arange(len(ser["dec_max_mes"])) / 12
ax.plot(meses, ser["dec_max_mes"], color=S1, lw=1.5)
ax.axhline(23.5, color=TXT2, lw=0.8, ls=":"); ax.text(0.5, 23.8, "obliquidade 23,5°", fontsize=8, color=TXT2)
ax.set_ylabel("declinação máx. no mês (°)")
ax.set_title("Lua: paralisação (ciclo do nodo) e perigeu")
subtitulo(ax, f"Período do nodo {abs(RL['periodo_nodo_anos']):.2f} anos (Terra 18,61): a lua sobe até {RL['declinacao_lua_max_mensal_graus'][1]:.1f}° e "
              f"no mínimo só {RL['declinacao_lua_max_mensal_graus'][0]:.1f}°.")
ax.set_xlabel("ano")
salvar(fig, "f1_10_lua_declinacao.png")

fig, ax2 = plt.subplots(figsize=(10, 3.6))
td = ser["t_d"]; dl = ser["dist_lua"] / 1e6
k = td <= 3 * 360
ax2.plot(td[k] / 360, dl[k], color=S1, lw=1.2)
ax2.set_ylabel("distância (mil km)"); ax2.set_xlabel("ano")
ax2.set_title("Distância da lua nos primeiros 3 anos")
media = f"{RL['lua_distancia_media_km']:,.0f}".replace(",", " ")
subtitulo(ax2, f"Média {media} km (Terra 384 400); perigeus de {RL['lua_perigeu_min_km']/1e3:.0f} mil a apogeus de {RL['lua_apogeu_max_km']/1e3:.0f} mil km. "
               f"Os perigeus mais fundos caem quando o perigeu aponta para o sol (ciclo de {RL['periodo_perigeu_anos']:.2f} anos).")
salvar(fig, "f1_10b_lua_distancia.png")

# eclipses
ecl = [l.strip().split(",") for l in open(D / "planeta/eclipses_100anos.csv")][1:]
fig, ax = plt.subplots(figsize=(11, 5.2))
estilo = {("sol", "total"): (S8, "o", "sol total"), ("sol", "híbrido"): (S8, "D", "sol híbrido"),
          ("sol", "anular"): (S8, "s", "sol anular"), ("sol", "parcial"): (S8, "^", "sol parcial"),
          ("lua", "total"): (S1, "o", "lua total"), ("lua", "parcial"): (S1, "^", "lua parcial"),
          ("lua", "penumbral"): (S1, "v", "lua penumbral")}
for (corpo, tipo), (c, mk, rot) in estilo.items():
    sel = [e for e in ecl if e[1] == corpo and e[2].split()[0] == tipo]
    if not sel:
        continue
    x = np.array([float(e[0]) for e in sel])
    cheio = tipo in ("total", "híbrido")
    ax.scatter(x / Y, x % Y, s=22, marker=mk, color=c if cheio else SUP, edgecolor=c, lw=1.1, label=f"{rot} ({len(sel)})")
ax.set_xlabel("ano"); eixo_meses(ax, y=True); ax.set_ylim(-6, 366); ax.set_xlim(-1, 101)
ax.legend(ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.13))
E = RL["eclipses"]
ax.set_title("Eclipses em 100 anos: as estações de eclipse recuam no calendário")
subtitulo(ax, f"{E['sol_por_ano']:.2f} do sol e {E['lua_por_ano']:.2f} da lua por ano (Terra ~2,4 e ~2,4); "
              f"faixas recuam {360 - RL['ano_de_eclipses_d']:.1f} d por ano (ano de eclipses {RL['ano_de_eclipses_d']:.1f} d). Semente provisória.")
salvar(fig, "f1_11_eclipses_100anos.png")

# eclipses do sol: mistura de tipos planeta x Terra (Espenak, -1999 a +3000)
fig, ax = plt.subplots(figsize=(8, 3.4))
terra_frac = dict(total=26.7, anular=33.2, híbrido=4.8, parcial=35.3)
tipos = ["total", "híbrido", "anular", "parcial"]
seeds = [RL["eclipses"]] + list(RL["eclipses_outras_sementes"].values())
def frac(est):
    n = {t: est["por_seculo"].get(f"sol:{t}", 0) for t in tipos}; tot = sum(n.values())
    return np.array([n[t] / tot * 100 for t in tipos])
F = np.array([frac(s) for s in seeds])
y = np.arange(len(tipos))
ax.barh(y + 0.2, F.mean(0), height=0.38, color=S1, label="planeta (7 sementes, média; barra = faixa)")
ax.errorbar(F.mean(0), y + 0.2, xerr=[F.mean(0) - F.min(0), F.max(0) - F.mean(0)], fmt="none", ecolor=TXT, lw=1, capsize=3)
ax.barh(y - 0.2, [terra_frac[t] for t in tipos], height=0.38, color=S2, label="Terra (catálogo de 5 000 anos)")
ax.set_yticks(y); ax.set_yticklabels(tipos); ax.set_xlabel("% dos eclipses do sol"); ax.invert_yaxis()
ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
ax.set_title("Lua aparente menor: mais anulares, menos totais")
subtitulo(ax, f"Diâmetro médio da lua {RL['diametro_lua_arcmin'][1]:.1f}′ contra o sol {RL['diametro_sol_arcmin'][1]:.1f}′ (Terra 31,1′ e 32,0′).")
salvar(fig, "f1_12_eclipses_tipos.png")

# maré: sizígia e quadratura, 60 dias
mt = np.load(D / "terra/_mare_terra.npz")
fig, axs = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
k = ser["t2_d"] <= 60
axs[0].plot(ser["t2_d"][k], ser["eta2"][k] * 100, color=S1, lw=0.9)
for x in ser["novas"][(ser["novas"] < 60)]:
    axs[0].axvline(x, color=TXT2, lw=0.8, ls=":"); axs[0].text(x, 62, "nova", fontsize=7, color=TXT2, ha="center")
for x in ser["cheias"][(ser["cheias"] < 60)]:
    axs[0].axvline(x, color=TXT2, lw=0.8, ls=":"); axs[0].text(x, 62, "cheia", fontsize=7, color=TXT2, ha="center")
axs[0].set_ylabel("cm"); axs[0].set_ylim(-40, 70)
axs[0].set_title("Maré de equilíbrio no equador, meridiano 0: planeta, meses 1 e 2")
subtitulo(axs[0], "A forçante astronômica pura; a amplitude real de cada costa sai da plataforma e das baías (F6).")
kt = mt["t_h"] / 24 <= 60
axs[1].plot(mt["t_h"][kt] / 24, mt["eq"][kt] * 100, color=S2, lw=0.9)
axs[1].set_ylabel("cm"); axs[1].set_ylim(-40, 70); axs[1].set_xlabel("dias")
axs[1].set_title("Terra, mesma conta (jan–fev 2024)", fontsize=10)
salvar(fig, "f1_13_mare_sizigia_quadratura.png")

# constituintes planeta x Terra
TM = json.loads((D / "terra/resumo_lua_mare.json").read_text())["mare"]
nomes_c = ["M2", "S2", "N2", "K2", "K1", "O1", "P1", "Q1"]
pl = [RL["mare_constituintes"][c]["amplitude_m"] * 100 for c in nomes_c]
te = [TM[c]["modelo_m"] * 100 for c in nomes_c]
fig, ax = plt.subplots(figsize=(9, 3.8))
x = np.arange(len(nomes_c))
ax.bar(x - 0.2, pl, 0.38, color=S1, label="planeta")
ax.bar(x + 0.2, te, 0.38, color=S2, label="Terra (modelo; ≤1,2 % de Cartwright-Tayler)")
for i, c in enumerate(nomes_c):
    ax.text(i - 0.2, pl[i] + 0.4, f"{RL['mare_constituintes'][c]['periodo_h']:.2f} h", fontsize=7, ha="center", color=TXT2, rotation=90, va="bottom")
ax.set_xticks(x); ax.set_xticklabels(nomes_c); ax.set_ylabel("amplitude de equilíbrio (cm)"); ax.legend(fontsize=8)
ax.set_ylim(0, 33)
ax.set_title("Constituintes de maré")
subtitulo(ax, "Semidiurnas no equador, diurnas a 45°. Rótulo: período no planeta (Terra M2 = 12,42 h).")
salvar(fig, "f1_14_mare_constituintes.png")

# ------------------------------------------------------------ grade
from mundo.grade import Grade
from mundo.constantes import R_PLANETA
g = Grade(12)
fig = plt.figure(figsize=(12, 4.8))
ax = fig.add_subplot(1, 2, 1)
# projeção ortográfica centrada em 30N 0E
lat0 = np.radians(30)
def orto(xyz):
    x, y, z = xyz[..., 0], xyz[..., 1], xyz[..., 2]
    X = y; Y = -np.sin(lat0) * x + np.cos(lat0) * z; vis = np.cos(lat0) * x + np.sin(lat0) * z
    return X, Y, vis
for a, b in g.arestas:
    pa, pb = g.xyz[a], g.xyz[b]
    seg = np.array([pa + (pb - pa) * s for s in np.linspace(0, 1, 6)]); seg /= np.linalg.norm(seg, axis=1)[:, None]
    X, Yy, v = orto(seg)
    if (v > 0).all():
        ax.plot(X, Yy, color=AZUL[4], lw=0.6)
X, Yy, v = orto(g.xyz)
p5 = g.grau == 5
ax.plot(X[p5 & (v > 0)], Yy[p5 & (v > 0)], "o", color=S2, ms=6, mec=SUP)
ax.add_patch(Circle((0, 0), 1, fill=False, color=TXT2, lw=0.8))
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Grade geodésica (f = 12 para ver; a do nível 1 é f = 300)")
ax.text(-1, -1.12, "laranja: vértices de 5 vizinhos (12 no globo, 2 nos polos)", fontsize=8, color=TXT2)
GR = json.loads((D / "terra/resumo_grade.json").read_text())
ax2 = fig.add_subplot(1, 2, 2)
G3 = Grade(300)
A3 = G3.area * R_PLANETA**2 / 1e6
ax2.hist(A3, bins=60, color=S1, edgecolor=SUP, lw=0.5)
ax2.set_xlabel("área da célula (km², f = 300)"); ax2.set_ylabel("células")
r3 = GR["300"]
ax2.set_title("Áreas das células")
subtitulo(ax2, f"{r3['n_celulas']:,} células; espaçamento {r3['espacamento_medio_km']:.1f} km; área ±{r3['area_cv']*100:.0f} % (dp).".replace(",", " "))
salvar(fig, "f1_15_grade_geodesica.png")

# ------------------------------------------------------------ teste terrestre
cmp_ = np.loadtxt(D / "terra/insolacao_comparacao.csv", delimiter=",", skiprows=1)
RT = json.loads((D / "terra/resumo_lua_mare.json").read_text())
fig, axs = plt.subplots(1, 3, figsize=(14, 4))
lats_t = sorted(set(cmp_[:, 0]))
cT = dict(zip([78, 70, 66, 60, 45, 30, 15, 0, -15, -30, -45, -60], [AZUL[7], AZUL[6], AZUL[5], AZUL[5], AZUL[4], AZUL[3], AZUL[2], AZUL[1]] + [S2] * 4))
for l in [78, 60, 45, 0, -45]:
    k = cmp_[:, 0] == l
    axs[0].plot(cmp_[k, 1], cmp_[k, 3] - cmp_[k, 2], lw=1, color=cT[l], label=f"{l:+d}°")
axs[0].set_title("Insolação diária: modelo − efeméride", fontsize=10); axs[0].set_ylabel("W/m²"); axs[0].set_xlabel("dia de 2024")
axs[0].legend(fontsize=7, ncol=2); axs[0].set_ylim(-0.5, 0.5)
for l in [60, 45, 0, -45]:
    k = cmp_[:, 0] == l
    axs[1].plot(cmp_[k, 1], (cmp_[k, 5] - cmp_[k, 4]) * 60, lw=1, color=cT[l], label=f"{l:+d}°")
axs[1].set_title("Duração do dia: modelo − efeméride", fontsize=10); axs[1].set_ylabel("minutos"); axs[1].set_xlabel("dia de 2024")
axs[1].legend(fontsize=7); axs[1].set_ylim(-1, 1)
mm = RT["mare"]
axs[2].bar(range(len(mm)), [(v["razao"] - 1) * 100 for v in mm.values()], color=S1, width=0.6)
axs[2].set_xticks(range(len(mm))); axs[2].set_xticklabels(list(mm)); axs[2].axhline(0, color=TXT2, lw=0.8)
axs[2].set_ylim(-2, 2); axs[2].set_ylabel("% de diferença")
axs[2].set_title("Maré: modelo × Cartwright-Tayler", fontsize=10)
fig.suptitle(f"Teste terrestre · eclipses 2024–2028: {RT['eclipses_reproduzidos']}/{RT['eclipses_reais']} com data e tipo certos; "
             + (f"nodo {abs(RT['periodo_nodo_anos']):.2f} a (real 18,61); perigeu {RT['periodo_perigeu_anos']:.2f} a (real 8,85)").replace(".", ","),
             x=0.02, ha="left", fontweight="bold", fontsize=11)
fig.tight_layout()
salvar(fig, "f1_00_teste_terrestre.png")
