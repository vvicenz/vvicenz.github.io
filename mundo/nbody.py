"""Problema de três corpos estrela-planeta-lua (seção 3).

Integração direta em coordenadas de Jacobi: r1 = lua - planeta,
r2 = baricentro(planeta+lua) - estrela. Nada de teoria lunar pronta: a
regressão dos nodos, a precessão do perigeu, a evecção e a variação saem da
gravidade da estrela sobre o par planeta-lua.

Referencial: inercial, eclíptica da época (XY = plano da órbita do
baricentro planeta-lua, X = equinócio de março na época).
"""
import numpy as np
from scipy.integrate import solve_ivp

from .constantes import G


class TresCorpos:
    def __init__(self, m0, m1, m2):
        self.m = (m0, m1, m2)
        self.mu1 = m1 + m2
        self.M = m0 + m1 + m2

    def posicoes(self, r1, r2):
        m0, m1, m2 = self.m
        Xs = -(self.mu1 / self.M) * r2
        Xb = (m0 / self.M) * r2
        Xp = Xb - (m2 / self.mu1) * r1
        Xm = Xb + (m1 / self.mu1) * r1
        return Xs, Xp, Xm

    def _deriv(self, t, y):
        m0, m1, m2 = self.m
        r1, v1, r2, v2 = y[0:3], y[3:6], y[6:9], y[9:12]
        # vetores relativos montados sem passar por coordenadas absolutas
        d_pm = r1                                   # planeta -> lua
        d_sp = r2 - (m2 / self.mu1) * r1            # estrela -> planeta
        d_sm = r2 + (m1 / self.mu1) * r1            # estrela -> lua
        f_pm = G * d_pm / np.dot(d_pm, d_pm) ** 1.5
        f_sp = G * d_sp / np.dot(d_sp, d_sp) ** 1.5
        f_sm = G * d_sm / np.dot(d_sm, d_sm) ** 1.5
        a_s = m1 * f_sp + m2 * f_sm
        a_p = -m0 * f_sp + m2 * f_pm
        a_m = -m0 * f_sm - m1 * f_pm
        a1 = a_m - a_p
        a2 = (m1 * a_p + m2 * a_m) / self.mu1 - a_s
        return np.concatenate([v1, a1, v2, a2])

    def integrar(self, y0, t_fim_s, passo_saida_s, rtol=1e-12):
        t_eval = np.arange(0.0, t_fim_s + 0.5 * passo_saida_s, passo_saida_s)
        atol = np.array([1e-3] * 3 + [1e-9] * 3 + [1e-2] * 3 + [1e-9] * 3)
        sol = solve_ivp(self._deriv, (0.0, t_eval[-1]), y0, method="DOP853",
                        t_eval=t_eval, rtol=rtol, atol=atol)
        if not sol.success:
            raise RuntimeError(sol.message)
        y = sol.y.T
        return t_eval, y[:, 0:3], y[:, 3:6], y[:, 6:9], y[:, 9:12]


def elementos_para_estado(gm, a, e, i, Omega, omega, M):
    """Elementos keplerianos -> posição e velocidade (referencial da eclíptica)."""
    E = M
    for _ in range(30):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    x = a * (np.cos(E) - e)
    y = a * np.sqrt(1 - e**2) * np.sin(E)
    n = np.sqrt(gm / a**3)
    vx = -a * n * np.sin(E) / (1 - e * np.cos(E))
    vy = a * n * np.sqrt(1 - e**2) * np.cos(E) / (1 - e * np.cos(E))
    cO, sO, ci, si, cw, sw = (np.cos(Omega), np.sin(Omega), np.cos(i), np.sin(i),
                              np.cos(omega), np.sin(omega))
    R = np.array([[cO * cw - sO * sw * ci, -cO * sw - sO * cw * ci, sO * si],
                  [sO * cw + cO * sw * ci, -sO * sw + cO * cw * ci, -cO * si],
                  [sw * si, cw * si, ci]])
    return R @ np.array([x, y, 0.0]), R @ np.array([vx, vy, 0.0])


def estado_para_elementos(gm, r, v):
    """Vetorizado (N,3) -> a, e, i, Omega, varpi (longitude do pericentro), L (longitude média)."""
    r = np.atleast_2d(r); v = np.atleast_2d(v)
    rn = np.linalg.norm(r, axis=1)
    h = np.cross(r, v)
    hn = np.linalg.norm(h, axis=1)
    i = np.arccos(h[:, 2] / hn)
    Omega = np.arctan2(h[:, 0], -h[:, 1])
    ev = np.cross(v, h) / gm - r / rn[:, None]
    e = np.linalg.norm(ev, axis=1)
    en = (v**2).sum(1) / 2 - gm / rn
    a = -gm / (2 * en)
    # longitude do pericentro e longitude verdadeira, "quebradas" no nodo
    nodo = np.stack([np.cos(Omega), np.sin(Omega), np.zeros_like(Omega)], 1)
    def ang_no_plano(u):
        c = (u * nodo).sum(1)
        s = (np.cross(nodo, u) * h).sum(1) / hn
        return np.arctan2(s, c)
    omega = ang_no_plano(ev / e[:, None])
    u_lat = ang_no_plano(r / rn[:, None])
    nu = u_lat - omega
    E = 2 * np.arctan2(np.sqrt(1 - e) * np.sin(nu / 2), np.sqrt(1 + e) * np.cos(nu / 2))
    M = E - e * np.sin(E)
    varpi = Omega + omega
    return dict(a=a, e=e, i=i, Omega=Omega, varpi=varpi, L=varpi + M)
