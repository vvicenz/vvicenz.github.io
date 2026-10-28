"""Fases da lua, sizígias e eclipses a partir das posições integradas.

Entradas: vetores planetocêntricos da estrela `s(t)` e da lua `m(t)` num
referencial cuja matriz `R_ecl` leva à eclíptica (identidade no planeta v5;
rotação pela obliquidade J2000 no teste terrestre, que usa ICRS).
"""
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq, minimize_scalar


def lon_lat(v):
    lon = np.arctan2(v[..., 1], v[..., 0])
    lat = np.arctan2(v[..., 2], np.hypot(v[..., 0], v[..., 1]))
    return lon, lat


class Efemeride:
    """Interpolação cúbica das posições amostradas (passo de 1 h ou menor)."""

    def __init__(self, t, s, m, R_ecl=np.eye(3)):
        self.t = t
        self.s = CubicSpline(t, s @ R_ecl.T)
        self.m = CubicSpline(t, m @ R_ecl.T)

    def elong(self, t):
        ls, _ = lon_lat(self.s(t)); lm, _ = lon_lat(self.m(t))
        return (lm - ls) % (2 * np.pi)

    def sizigias(self, alvo=0.0):
        """Instantes em que a elongação em longitude cruza `alvo` (0 = lua nova,
        pi = lua cheia, pi/2 e 3pi/2 = quartos)."""
        D = (self.elong(self.t) - alvo + np.pi) % (2 * np.pi) - np.pi
        idx = np.where((D[:-1] < 0) & (D[1:] >= 0))[0]
        f = lambda x: (self.elong(x) - alvo + np.pi) % (2 * np.pi) - np.pi
        return np.array([brentq(f, self.t[i], self.t[i + 1], xtol=1e-3) for i in idx])

    def iluminacao(self, t):
        s = self.s(t); m = self.m(t)
        ms = s - m                                    # lua -> estrela
        cos_fase = -(m * ms).sum(-1) / (np.linalg.norm(m, axis=-1) * np.linalg.norm(ms, axis=-1))
        return (1 + cos_fase) / 2


def _solar(ef, t, R_e, R_m, R_s):
    """Geometria do eclipse do sol no instante t. Distâncias em metros."""
    s = ef.s(t); m = ef.m(t)
    u = m - s; D_sm = np.linalg.norm(u); u = u / D_sm         # eixo da sombra
    L = np.dot(-m, u)                                         # lua -> plano fundamental
    gama = np.linalg.norm(-m - L * u)                         # eixo ao centro do planeta
    tf1 = (R_s + R_m) / D_sm; tf2 = (R_s - R_m) / D_sm
    r_pen = R_m + L * tf1
    r_umb = R_m - L * tf2                                     # <0: antiumbra (anular)
    return gama, r_pen, r_umb, L, tf2


def _lunar(ef, t, R_e, R_m, R_s, alargamento=1.02):
    s = ef.s(t); m = ef.m(t)
    w = -s; D_se = np.linalg.norm(w); w = w / D_se            # eixo da sombra do planeta
    L = np.dot(m, w)
    delta = np.linalg.norm(m - L * w)
    r_umb = alargamento * (R_e - L * (R_s - R_e) / D_se)
    r_pen = alargamento * (R_e + L * (R_s + R_e) / D_se)
    return delta, r_pen, r_umb


def eclipses(ef, R_e, R_m, R_s):
    """Lista de eclipses (instante do máximo, tipo, grandeza)."""
    out = []
    for tn in ef.sizigias(0.0):
        f = lambda x: _solar(ef, x, R_e, R_m, R_s)[0]
        r = minimize_scalar(f, bounds=(tn - 0.25, tn + 0.25), method="bounded",
                            options=dict(xatol=1e-5))
        tm = r.x
        gama, r_pen, r_umb, L, tf2 = _solar(ef, tm, R_e, R_m, R_s)
        if gama > R_e + r_pen:
            continue
        if gama < R_e:                                       # eixo toca o planeta
            Ls = L - np.sqrt(R_e**2 - gama**2)               # ponto da superfície mais próximo
            r_sup = R_m - Ls * tf2
            if r_umb > 0:
                tipo = "total"
            elif r_sup > 0:
                tipo = "híbrido"
            else:
                tipo = "anular"
        elif gama < R_e + abs(r_umb):
            tipo = "total não central" if r_umb > 0 else "anular não central"
        else:
            tipo = "parcial"
        grandeza = (R_e + r_pen - gama) / (r_pen - r_umb)    # fração do diâmetro (fundamental)
        out.append(dict(t=tm, corpo="sol", tipo=tipo, gama=gama / R_e, grandeza=grandeza))
    for tc in ef.sizigias(np.pi):
        f = lambda x: _lunar(ef, x, R_e, R_m, R_s)[0]
        r = minimize_scalar(f, bounds=(tc - 0.25, tc + 0.25), method="bounded",
                            options=dict(xatol=1e-5))
        tm = r.x
        delta, r_pen, r_umb = _lunar(ef, tm, R_e, R_m, R_s)
        if delta > r_pen + R_m:
            continue
        g_umb = (r_umb + R_m - delta) / (2 * R_m)
        g_pen = (r_pen + R_m - delta) / (2 * R_m)
        if g_umb >= 1:
            tipo = "total"
        elif g_umb > 0:
            tipo = "parcial"
        else:
            tipo = "penumbral"
        out.append(dict(t=tm, corpo="lua", tipo=tipo, gama=delta / R_e,
                        grandeza=g_umb if g_umb > 0 else g_pen))
    return sorted(out, key=lambda d: d["t"])
