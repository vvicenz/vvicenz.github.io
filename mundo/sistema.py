"""Sistema estrela-planeta-lua do mundo v5, montado a partir das decisões.

Âncoras do calendário (decisão desta fase, F1):
  * t = 0: início do dia 1 do mês 1, 00:00 no meridiano 0 (hora solar média).
  * Solstício de dezembro ao meio-dia de 21/12 (t = 350,5 d), como no
    calendário gregoriano; ano civil = ano trópico de 360 d, sem bissexto.
  * Lua nova média no início de cada mês (t = 0, 30, 60, ...).

O semieixo da lua e a longitude média inicial são ajustados para que o mês
sinódico MÉDIO da integração dê 30,000 d e a lua nova média caia em t = 0:
é a decisão 3 sendo cumprida, não um resultado forçado. Nodo e perigeu
iniciais da lua saem da semente ("astros/lua").
"""
import numpy as np

from .constantes import (G, DIA, M_PLANETA, M_LUA, E_LUA, I_LUA, R_PLANETA, R_LUA,
                         PLANETA)
from .orbita import Orbita
from .nbody import TresCorpos, elementos_para_estado, estado_para_elementos
from .lua import Efemeride
from .semente import gerador, SEMENTE_PROVISORIA

T_SOLSTICIO_DEZ = 350.5


class Sistema:
    def __init__(self, astros=PLANETA, semente=SEMENTE_PROVISORIA):
        self.A = astros
        d = astros.derivados
        self.orb = Orbita(astros, T_SOLSTICIO_DEZ)
        self.m = (astros.m_estrela, M_PLANETA, M_LUA)
        self.tc = TresCorpos(*self.m)
        self.psi_dot = 2 * np.pi / (d["precessao_periodo_anos"] * astros.ano_tropico_d * DIA)
        rng = gerador("astros/lua", semente)
        self.Omega0 = rng.uniform(0, 2 * np.pi)       # nodo ascendente
        self.varpi0 = rng.uniform(0, 2 * np.pi)       # perigeu
        self.a_lua = d["a_lua_kepler_m"]
        self.delta = 0.0
        self.e_lua, self.i_lua = E_LUA, I_LUA     # osculadores iniciais
        self.semente = semente

    def estado_inicial(self):
        A = self.A; d = A.derivados
        M0 = float(self.orb.anomalia_media(0.0))
        varpi_p = A.lon_peri - np.pi                   # periélio heliocêntrico do baricentro
        r2, v2 = elementos_para_estado(G * sum(self.m), d["semieixo_m"], A.excentricidade,
                                       0.0, 0.0, varpi_p, M0)
        L_sol = (M0 + A.lon_peri)                      # longitude média do sol
        L_lua = L_sol + self.delta
        r1, v1 = elementos_para_estado(G * (self.m[1] + self.m[2]), self.a_lua, self.e_lua, self.i_lua,
                                       self.Omega0, self.varpi0 - self.Omega0,
                                       L_lua - self.varpi0)
        return np.concatenate([r1, v1, r2, v2])

    def integrar(self, anos, passo_h=1.0):
        t, R1, V1, R2, V2 = self.tc.integrar(self.estado_inicial(),
                                             anos * self.A.ano_tropico_d * DIA, passo_h * 3600)
        Xs, Xp, Xm = self.tc.posicoes(R1, R2)
        self.t_d = t / DIA
        self.s = Xs - Xp; self.mvec = R1; self.vlua = V1
        self.ef = Efemeride(self.t_d, self.s, self.mvec)
        return self

    def _medir_lunacao(self, anos):
        self.integrar(anos, passo_h=2.0)
        novas = self.ef.sizigias(0.0)
        n = np.arange(len(novas))          # cada cruzamento é uma lua nova
        S, t0 = np.polyfit(n, novas, 1)
        L = self.A.lunacao_d
        return np.array([S - L, ((t0 + L / 2) % L) - L / 2])

    def ajustar_lua(self, anos=12, iter_=6, verbose=True):
        """Newton 2x2 em (a_lua, delta) para mês sinódico médio = lunação
        decidida e lua nova média em t = 0. Os dois parâmetros se acoplam
        (a fase inicial muda a relação entre semieixo osculador e médio)."""
        x = np.array([self.a_lua, self.delta])
        escala = np.array([1e4, 1e-3])                 # passos de diferença finita
        def f(x):
            self.a_lua, self.delta = x
            return self._medir_lunacao(anos)
        r = f(x)
        for k in range(iter_):
            if verbose:
                print(f"  ajuste {k}: S - L = {r[0]*86400:+.1f} s, lua nova média em t = {r[1]*24:+.3f} h")
            if abs(r[0]) < 1e-5 and abs(r[1]) < 1e-3:
                break
            J = np.empty((2, 2))
            for c in range(2):
                dx = np.zeros(2); dx[c] = escala[c]
                J[:, c] = (f(x + dx) - r) / escala[c]
            x = x - np.linalg.solve(J, r)
            r = f(x)
        self.a_lua, self.delta = x
        return r

    def ajustar_forma(self, e_alvo, i_alvo, anos=12, iter_=3, verbose=True):
        """Excentricidade e inclinação MÉDIAS (osculadoras, médias no tempo)
        iguais às da Lua real medida do mesmo jeito no teste terrestre."""
        for k in range(iter_):
            self.ajustar_lua(anos=anos, verbose=False)
            self.integrar(anos, passo_h=2.0)
            el = estado_para_elementos(G * (self.m[1] + self.m[2]), self.mvec, self.vlua)
            de, di = e_alvo - el["e"].mean(), i_alvo - el["i"].mean()
            if verbose:
                print(f"  forma {k}: e médio {el['e'].mean():.5f}, i médio {np.degrees(el['i'].mean()):.4f}°")
            if abs(de) < 2e-4 and abs(di) < 1e-4:
                break
            self.e_lua += de; self.i_lua += di
        return self

    # --- referencial do equinócio da data e equador da data
    def para_data(self, v):
        """Eclíptica inercial da época -> eclíptica do equinócio da data."""
        ang = self.psi_dot * self.t_d * DIA
        c, s = np.cos(ang), np.sin(ang)
        return np.stack([c * v[:, 0] - s * v[:, 1], s * v[:, 0] + c * v[:, 1], v[:, 2]], 1)

    def para_equador(self, v):
        e = self.A.obliq
        vd = self.para_data(v)
        return np.stack([vd[:, 0], np.cos(e) * vd[:, 1] - np.sin(e) * vd[:, 2],
                         np.sin(e) * vd[:, 1] + np.cos(e) * vd[:, 2]], 1)

    def angulo_sideral(self, t_d):
        """Hora sideral em Greenwich-0: ascensão reta do sol médio + pi + 2 pi t."""
        L_medio = self.orb.anomalia_media(t_d) + self.A.lon_peri
        return (L_medio + np.pi + 2 * np.pi * t_d) % (2 * np.pi)
