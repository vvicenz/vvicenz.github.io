"""Testes rápidos da F1 (pytest). Os testes terrestres completos estão em scripts/terra_*.py."""
import numpy as np
from mundo.constantes import PLANETA, TERRA
from mundo.orbita import Orbita, insolacao_diaria, kepler_E, duracao_dia
from mundo.grade import Grade
from mundo.semente import gerador
from mundo.nbody import elementos_para_estado, estado_para_elementos


def test_kepler():
    M = np.linspace(0, 2 * np.pi, 50)
    E = kepler_E(M, 0.2)
    assert np.allclose(E - 0.2 * np.sin(E), M, atol=1e-13)


def test_media_global_insolacao():
    orb = Orbita(PLANETA, 350.5)
    t = np.arange(360) + 0.5
    s = orb.sol(t)
    lat = np.radians(np.linspace(-89.95, 89.95, 1800))[:, None]
    q = insolacao_diaria(lat, s["dec"][None], s["r"][None], PLANETA.s0)
    w = np.cos(lat)
    media = (q * w).sum() / (w.sum() * 360)
    esperado = PLANETA.s0 / 4 / np.sqrt(1 - PLANETA.excentricidade**2)
    assert abs(media - esperado) < 0.05


def test_solsticio_e_equinocio_no_lugar():
    orb = Orbita(PLANETA, 350.5)
    assert abs(np.degrees(orb.sol(350.5)["lam"]) - 270) < 1e-9
    assert abs(orb.instante_longitude(270) - 350.5) < 1e-9


def test_duracao_dia_equador_simetrica():
    dl = duracao_dia(0.0, np.radians(np.linspace(-23.5, 23.5, 11)))
    # com refração o dia equatorial varia ~1 min com a declinação
    assert np.all(np.abs(dl - dl[0]) < 0.02) and 12.0 < dl[0] < 12.2


def test_grade_deterministica_e_aninhada():
    a, b = Grade(20), Grade(20)
    assert a.hash() == b.hash()
    assert abs(a.area.sum() - 4 * np.pi) < 1e-10
    assert (a.grau == 5).sum() == 12 and ((a.grau == 5) | (a.grau == 6)).all()
    c = Grade(40)
    d = np.min(np.linalg.norm(c.xyz[None, :, :] - a.xyz[:200, None, :], axis=2), axis=1)
    assert d.max() < 1e-12


def test_semente():
    x = gerador("astros/lua", 7).uniform(size=3)
    y = gerador("astros/lua", 7).uniform(size=3)
    z = gerador("astros/lua", 8).uniform(size=3)
    w = gerador("outro", 7).uniform(size=3)
    assert np.array_equal(x, y) and not np.array_equal(x, z) and not np.array_equal(x, w)


def test_elementos_ida_e_volta():
    gm = 4e14
    r, v = elementos_para_estado(gm, 3.9e8, 0.055, 0.09, 1.0, 2.0, 0.5)
    el = estado_para_elementos(gm, r, v)
    assert abs(el["a"][0] / 3.9e8 - 1) < 1e-12 and abs(el["e"][0] - 0.055) < 1e-12
    assert abs(el["i"][0] - 0.09) < 1e-12
    assert abs((el["L"][0] - (1.0 + 2.0 + 0.5) + np.pi) % (2 * np.pi) - np.pi) < 1e-10


def test_derivados_terra():
    d = TERRA.derivados
    assert abs(d["ano_sideral_d"] - 365.25636) < 1e-3
    assert abs(d["mes_sideral_d"] - 27.32166) < 1e-3
    assert abs(d["precessao_periodo_anos"] - 25772) < 100
