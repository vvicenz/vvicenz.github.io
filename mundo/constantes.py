"""Constantes físicas e parâmetros dos astros (plano v5, seções 3, 4 e 22).

Dois conjuntos com a mesma forma: TERRA (para o teste terrestre, princípio 8)
e PLANETA (o mundo v5). Tudo em SI; tempo em segundos, salvo onde dito "d"
(dia solar médio de 86 400 s).

Só os valores decididos no plano entram como entrada. Tudo o que deles
decorre por física (distância da estrela, luminosidade, distância da lua,
precessão) é derivado aqui, não escolhido.
"""
from dataclasses import dataclass, field
import math

G = 6.67430e-11            # m^3 kg^-1 s^-2
DIA = 86400.0              # s, dia solar médio
UA = 1.495978707e11        # m
M_SOL = 1.98840987e30      # kg (GM_sol / G)
GM_SOL = 1.32712440018e20  # m^3 s^-2
R_SOL = 6.957e8            # m (raio nominal IAU)
L_SOL = 3.828e26           # W (nominal IAU)
S0_TERRA = 1361.0          # W m^-2, irradiância solar total a 1 UA

# Planeta: raio, massa, rotação e achatamento dinâmico terrestres (seção 4).
R_PLANETA = 6.371e6        # m, raio médio
GM_PLANETA = 3.986004418e14
M_PLANETA = GM_PLANETA / G
H_DINAMICO = 0.0032737949  # (C-A)/C da Terra; mesmo dia de 24 h -> mesmo achatamento

# Lua "do tamanho da nossa" (seção 3)
M_LUA = 7.342e22           # kg
R_LUA = 1.7374e6           # m
E_LUA = 0.0549             # excentricidade média
I_LUA = math.radians(5.145)  # inclinação sobre a eclíptica


def taxa_precessao(n_sol, e_sol, n_lua, e_lua, i_lua, obliq, omega_rot,
                   razao_massa_lua=M_LUA / M_PLANETA, h=H_DINAMICO):
    """Precessão lunissolar do eixo (rad/s), torque médio de estrela e lua
    sobre o bojo equatorial: psi' = 3/2 H cos(eps)/omega * soma n^2 (...)."""
    sol = n_sol**2 / (1 - e_sol**2) ** 1.5
    lua = (n_lua**2 * razao_massa_lua / (1 + razao_massa_lua)
           * (1 - 1.5 * math.sin(i_lua) ** 2) / (1 - e_lua**2) ** 1.5)
    return 1.5 * h * math.cos(obliq) / omega_rot * (sol + lua)


@dataclass
class Astros:
    nome: str
    ano_tropico_d: float        # dias solares médios
    excentricidade: float
    obliquidade_graus: float
    # longitude eclíptica do sol (geocêntrica) no periélio, medida do equinócio
    # de março; Terra hoje: 282,9 graus (periélio ~13 dias após o solstício de dezembro)
    lon_sol_perielio_graus: float
    lunacao_d: float            # mês sinódico médio
    m_estrela: float = M_SOL
    r_estrela: float = R_SOL
    s0: float = S0_TERRA        # fluxo no topo da atmosfera na distância média (semieixo)
    derivados: dict = field(default_factory=dict)

    @property
    def obliq(self):
        return math.radians(self.obliquidade_graus)

    @property
    def lon_peri(self):
        return math.radians(self.lon_sol_perielio_graus)

    def derivar(self, prec_periodo_anos=None, iter_=4):
        """Deriva semieixo da órbita, luminosidade, mês sideral, distância da
        lua e precessão (iterando, porque o ano sideral depende da precessão)."""
        Y = self.ano_tropico_d * DIA
        omega_rot = 2 * math.pi * (self.ano_tropico_d + 1) / self.ano_tropico_d / DIA
        P = prec_periodo_anos * Y if prec_periodo_anos else 1e300
        for _ in range(iter_):
            Ys = 1.0 / (1.0 / Y - 1.0 / P)           # ano sideral
            n_s = 2 * math.pi / Ys
            Tm = 1.0 / (1.0 / (self.lunacao_d * DIA) + 1.0 / Ys)  # mês sideral
            n_m = 2 * math.pi / Tm
            psi = taxa_precessao(n_s, self.excentricidade, n_m, E_LUA, I_LUA,
                                 self.obliq, omega_rot)
            if prec_periodo_anos is None:
                P = 2 * math.pi / psi
        m_tot = self.m_estrela + M_PLANETA + M_LUA
        a = (G * m_tot * (Ys / (2 * math.pi)) ** 2) ** (1 / 3)
        a_lua_kepler = (G * (M_PLANETA + M_LUA) * (Tm / (2 * math.pi)) ** 2) ** (1 / 3)
        lum = self.s0 * 4 * math.pi * a**2
        self.derivados = dict(
            ano_sideral_d=Ys / DIA, mes_sideral_d=Tm / DIA,
            semieixo_m=a, semieixo_ua=a / UA, luminosidade_lsol=lum / L_SOL,
            teff_k=5772.0 * (lum / L_SOL) ** 0.25 * (R_SOL / self.r_estrela) ** 0.5,
            a_lua_kepler_m=a_lua_kepler,
            precessao_periodo_anos=2 * math.pi / psi / Y,
            precessao_arcsec_ano=math.degrees(psi * Y) * 3600,
            dia_sideral_s=2 * math.pi / omega_rot, omega_rot=omega_rot,
            n_sol=n_s, n_lua=n_m,
        )
        return self


# Terra: valores reais de época J2000-2024, para o teste terrestre.
TERRA = Astros("Terra", ano_tropico_d=365.24219, excentricidade=0.016709,
               obliquidade_graus=23.4393, lon_sol_perielio_graus=282.94,
               lunacao_d=29.530589).derivar()

# Planeta v5: decisões 1-3 da seção 22. Estrela de 1 massa solar; o fluxo
# igual ao da Terra (seção 3) define a luminosidade, não o contrário.
PLANETA = Astros("Planeta v5", ano_tropico_d=360.0, excentricidade=0.017,
                 obliquidade_graus=23.5, lon_sol_perielio_graus=282.94,
                 lunacao_d=30.0).derivar()
