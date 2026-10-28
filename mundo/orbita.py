"""Órbita kepleriana do planeta e geometria do sol (seção 3).

Tempo t em dias solares médios contados do início do ano civil (dia 1 do
mês 1, 00:00 no meridiano 0). O ano civil é o ano trópico, então o
equinócio não deriva no calendário. A fase do periélio no ano é dada pelo
instante do solstício de dezembro, fixado em `t_solsticio_dez`.
"""
import numpy as np


def kepler_E(M, e, n_iter=8):
    """Anomalia excêntrica por Newton (vetorizado)."""
    M = np.asarray(M, dtype=float)
    E = M + e * np.sin(M)
    for _ in range(n_iter):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E


def anomalia_verdadeira(M, e):
    E = kepler_E(M, e)
    return 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))


def anomalia_media_de_verdadeira(nu, e):
    E = 2 * np.arctan2(np.sqrt(1 - e) * np.sin(nu / 2), np.sqrt(1 + e) * np.cos(nu / 2))
    return E - e * np.sin(E)


class Orbita:
    """Sol aparente visto do planeta, em referencial do equinócio da data."""

    def __init__(self, astros, t_solsticio_dez):
        self.A = astros
        self.e = astros.excentricidade
        self.eps = astros.obliq
        self.lp = astros.lon_peri          # longitude do sol no periélio
        self.Y = astros.ano_tropico_d
        # anomalia média no solstício de dezembro (lambda = 270 graus)
        M_sol = anomalia_media_de_verdadeira(np.radians(270.0) - self.lp, self.e)
        self.t_peri = t_solsticio_dez - (M_sol % (2 * np.pi)) / (2 * np.pi) * self.Y
        self.t_peri = self.t_peri % self.Y

    def anomalia_media(self, t):
        return 2 * np.pi * (np.asarray(t) - self.t_peri) / self.Y

    def sol(self, t):
        """Retorna dict com longitude eclíptica, declinação, AR, distância/a,
        e equação do tempo (minutos; relógio de sol menos relógio médio)."""
        M = self.anomalia_media(t)
        nu = anomalia_verdadeira(M, self.e)
        lam = (nu + self.lp) % (2 * np.pi)
        r = (1 - self.e**2) / (1 + self.e * np.cos(nu))   # em unidades de a
        dec = np.arcsin(np.sin(self.eps) * np.sin(lam))
        ra = np.arctan2(np.cos(self.eps) * np.sin(lam), np.cos(lam)) % (2 * np.pi)
        L_medio = (M + self.lp) % (2 * np.pi)
        eot = ((L_medio - ra + np.pi) % (2 * np.pi) - np.pi) * 1440 / (2 * np.pi)
        return dict(lam=lam, dec=dec, ra=ra, r=r, eot_min=eot, M=M, L_medio=L_medio)

    def instante_longitude(self, lam_graus, ano=0):
        """Instante (dias desde o ano 0) em que o sol atinge a longitude dada."""
        nu = np.radians(lam_graus) - self.lp
        M = anomalia_media_de_verdadeira(nu, self.e) % (2 * np.pi)
        t = self.t_peri + M / (2 * np.pi) * self.Y
        return (t % self.Y) + ano * self.Y


def insolacao_diaria(lat, dec, r, s0):
    """Média diária no topo da atmosfera (W/m2). lat, dec em rad; r em unidades de a."""
    lat, dec = np.broadcast_arrays(np.asarray(lat, float), np.asarray(dec, float))
    x = -np.tan(lat) * np.tan(dec)
    h0 = np.arccos(np.clip(x, -1, 1))
    q = (s0 / np.pi) / r**2 * (h0 * np.sin(lat) * np.sin(dec)
                                + np.cos(lat) * np.cos(dec) * np.sin(h0))
    return np.maximum(q, 0.0)


def duracao_dia(lat, dec, alt_graus=-0.833):
    """Horas com o centro do sol acima de alt_graus (-0,833: nascer/pôr com
    refração e semidiâmetro). -6: fim do crepúsculo civil."""
    lat, dec = np.broadcast_arrays(np.asarray(lat, float), np.asarray(dec, float))
    h = np.radians(alt_graus)
    x = (np.sin(h) - np.sin(lat) * np.sin(dec)) / (np.cos(lat) * np.cos(dec))
    return 24 / np.pi * np.arccos(np.clip(x, -1, 1))


def insolacao_instantanea(lat, dec, r, hora_solar, s0):
    """Fluxo instantâneo (W/m2) em hora solar verdadeira (12 = sol no meridiano)."""
    H = np.radians(15.0 * (np.asarray(hora_solar) - 12.0))
    cz = np.sin(lat) * np.sin(dec) + np.cos(lat) * np.cos(dec) * np.cos(H)
    return np.maximum(cz, 0) * s0 / r**2
