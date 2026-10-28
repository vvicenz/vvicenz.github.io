"""Grade esférica geodésica (nível 1 da seção 17).

Icosaedro com cada face dividida em f x f triângulos (classe I). Os pontos
de cada face são postos na esfera por uma interpolação "slerp" baricêntrica,
que é exata nas arestas e reduz a distorção de área da projeção gnomônica.
Células: Voronoi dos vértices (12 pentágonos, o resto hexágonos).

Determinística: só depende de f. Frequências que dividem f geram grades
cujos vértices são subconjunto exato desta (ex.: 75 ⊂ 150 ⊂ 300).
"""
import hashlib
import numpy as np

PHI = (1 + 5 ** 0.5) / 2


def icosaedro():
    v = np.array([[-1, PHI, 0], [1, PHI, 0], [-1, -PHI, 0], [1, -PHI, 0],
                  [0, -1, PHI], [0, 1, PHI], [0, -1, -PHI], [0, 1, -PHI],
                  [PHI, 0, -1], [PHI, 0, 1], [-PHI, 0, -1], [-PHI, 0, 1]], float)
    v /= np.linalg.norm(v, axis=1)[:, None]
    # gira para pôr um vértice em cada polo (pentágonos nos polos, simetria N-S)
    a = v[0] / np.linalg.norm(v[0]); z = np.array([0, 0, 1.0])
    k = np.cross(a, z); s = np.linalg.norm(k); c = a @ z; k /= s
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    Rm = np.eye(3) + s * K + (1 - c) * K @ K
    v = v @ Rm.T
    f = np.array([[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
                  [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
                  [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
                  [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]])
    return v, f


def _mapa(A, B, C, b, metodo):
    if metodo == "gnomonica":
        p = b[:, :1] * A + b[:, 1:2] * B + b[:, 2:] * C
    else:
        th = np.arccos(np.clip(A @ B, -1, 1))       # ângulo de aresta (igual nas 3)
        w = np.sin(b * th) / np.sin(th)
        p = w[:, :1] * A + w[:, 1:2] * B + w[:, 2:] * C
    return p / np.linalg.norm(p, axis=1)[:, None]


def _area_tri(a, b, c):
    num = np.abs(np.einsum("ij,ij->i", a, np.cross(b, c)))
    den = 1 + np.einsum("ij,ij->i", a, b) + np.einsum("ij,ij->i", b, c) + np.einsum("ij,ij->i", c, a)
    return 2 * np.arctan2(num, den)


class Grade:
    def __init__(self, f, metodo="slerp"):
        self.f = f
        V, F = icosaedro()
        # índices baricêntricos inteiros (i, j) com k = f - i - j
        ij = np.array([(i, j) for i in range(f + 1) for j in range(f + 1 - i)])
        bar = np.c_[ij, f - ij.sum(1)] / f
        loc = {tuple(x): n for n, x in enumerate(map(tuple, ij))}
        # triângulos locais
        tl = []
        for i in range(f):
            for j in range(f - i):
                tl.append((loc[(i, j)], loc[(i + 1, j)], loc[(i, j + 1)]))
                if i + j < f - 1:
                    tl.append((loc[(i + 1, j)], loc[(i + 1, j + 1)], loc[(i, j + 1)]))
        tl = np.array(tl)
        # chave global exata: vértice expresso em inteiros sobre os vértices do icosaedro
        pts, chaves, tris = [], [], []
        for fi, (a, b, c) in enumerate(F):
            p = _mapa(V[a], V[b], V[c], bar, metodo)
            ii = (ij[:, 0]).astype(np.int64); jj = ij[:, 1].astype(np.int64); kk = f - ii - jj
            # chave canônica: pares (vértice do ico, peso) ordenados
            ch = np.zeros((len(ij), 3, 2), np.int64)
            ch[:, 0] = np.c_[np.where(ii > 0, a, 99), ii]
            ch[:, 1] = np.c_[np.where(jj > 0, b, 99), jj]
            ch[:, 2] = np.c_[np.where(kk > 0, c, 99), kk]
            ordem = np.argsort(ch[:, :, 0] * (f + 1) + ch[:, :, 1], axis=1)
            ch = np.take_along_axis(ch, ordem[:, :, None], 1)
            chaves.append(ch.reshape(len(ij), 6)); pts.append(p)
            tris.append(tl + fi * len(ij))
        chaves = np.concatenate(chaves); pts = np.concatenate(pts); tris = np.concatenate(tris)
        _, primeiro, inv = np.unique(chaves, axis=0, return_index=True, return_inverse=True)
        inv = inv.ravel()
        # ordena os vértices por latitude decrescente e longitude (estável, legível)
        p = pts[primeiro]
        lat = np.arcsin(np.clip(p[:, 2], -1, 1)); lon = np.arctan2(p[:, 1], p[:, 0])
        ordem = np.lexsort((np.round(lon, 12), -np.round(lat, 12)))
        rank = np.empty_like(ordem); rank[ordem] = np.arange(len(ordem))
        self.xyz = p[ordem]
        self.tri = rank[inv[tris]]
        self.n = len(self.xyz)
        self.lat = np.degrees(np.arcsin(np.clip(self.xyz[:, 2], -1, 1)))
        self.lon = np.degrees(np.arctan2(self.xyz[:, 1], self.xyz[:, 0]))
        self._vizinhos_e_areas()

    def _vizinhos_e_areas(self):
        T = self.tri; X = self.xyz
        a, b, c = X[T[:, 0]], X[T[:, 1]], X[T[:, 2]]
        cc = np.cross(b - a, c - a); cc /= np.linalg.norm(cc, axis=1)[:, None]  # circuncentro
        area = np.zeros(self.n)
        for (p, q, r) in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
            P, Q, Rr = X[T[:, p]], X[T[:, q]], X[T[:, r]]
            mpq = P + Q; mpq /= np.linalg.norm(mpq, axis=1)[:, None]
            mpr = P + Rr; mpr /= np.linalg.norm(mpr, axis=1)[:, None]
            np.add.at(area, T[:, p], _area_tri(P, mpq, cc) + _area_tri(P, cc, mpr))
        self.area = area                          # esferorradianos; soma = 4 pi
        arestas = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
        arestas = np.unique(np.sort(arestas, axis=1), axis=0)
        self.arestas = arestas
        grau = np.bincount(arestas.ravel(), minlength=self.n)
        self.grau = grau
        ordem = np.argsort(np.r_[arestas[:, 0], arestas[:, 1]], kind="stable")
        viz = np.r_[arestas[:, 1], arestas[:, 0]][ordem]
        self.viz_ptr = np.r_[0, np.cumsum(grau)]
        self.viz = viz
        self.comp_aresta = np.arccos(np.clip((X[arestas[:, 0]] * X[arestas[:, 1]]).sum(1), -1, 1))

    def hash(self):
        h = hashlib.sha256()
        h.update(np.round(self.xyz, 12).astype("<f8").tobytes())
        h.update(self.tri.astype("<i4").tobytes())
        return h.hexdigest()
