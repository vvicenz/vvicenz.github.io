"""Maré de equilíbrio (forçante astronômica) e análise harmônica.

eta = sum_b (M_b/M_p) R^4/d_b^3 * P2(cos z_b) + termo de grau 3 da lua.
É a maré de um oceano global sem inércia: a forçante que a costa (F6)
amplifica ou amortece conforme plataforma e baía. Sem números de Love.
"""
import numpy as np


def altura_equilibrio(lat, lon, corpos_eq, theta, R, M_p):
    """corpos_eq: lista de (massa, vetores (N,3) planetocêntricos no equador
    da data). theta: ângulo sideral de Greenwich (N,). Retorna eta (m)."""
    lat = np.radians(lat); lon = np.radians(lon)
    obs = np.stack([np.cos(lat) * np.cos(theta + lon), np.cos(lat) * np.sin(theta + lon),
                    np.full_like(theta, np.sin(lat))], 1)
    eta = np.zeros_like(theta)
    for massa, v in corpos_eq:
        d = np.linalg.norm(v, axis=1)
        c = (obs * v).sum(1) / d
        eta += (massa / M_p) * R**4 / d**3 * (1.5 * c**2 - 0.5)
        eta += (massa / M_p) * R**5 / d**4 * (2.5 * c**3 - 1.5 * c)   # grau 3
    return eta


def velocidades(theta_dot, s_dot, h_dot, p_dot):
    """Velocidades (rad/s) das constituintes a partir das taxas de Doodson:
    tau = theta - s + pi (tempo lunar), s, h (sol médio), p (perigeu)."""
    tau = theta_dot - s_dot
    return {
        "M2": 2 * tau, "S2": 2 * (tau + s_dot - h_dot), "N2": 2 * tau - s_dot + p_dot,
        "K2": 2 * (tau + s_dot), "K1": tau + s_dot, "O1": tau - s_dot,
        "P1": tau + s_dot - 2 * h_dot, "Q1": tau - 2 * s_dot + p_dot,
        "Mf": 2 * s_dot, "Mm": s_dot - p_dot, "Ssa": 2 * h_dot,
    }


def ajuste_harmonico(t, eta, vel):
    """Mínimos quadrados: eta ~ c + sum A_k cos(w_k t - g_k). Retorna amplitudes (m)."""
    nomes = list(vel)
    cols = [np.ones_like(t)]
    for k in nomes:
        cols += [np.cos(vel[k] * t), np.sin(vel[k] * t)]
    X = np.stack(cols, 1)
    coef, *_ = np.linalg.lstsq(X, eta, rcond=None)
    amp = {k: float(np.hypot(coef[1 + 2 * j], coef[2 + 2 * j])) for j, k in enumerate(nomes)}
    resid = eta - X @ coef
    return amp, float(np.sqrt(np.mean(resid**2)))
