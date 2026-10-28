"""Semente única do mundo e fluxos derivados (princípio 6).

Cada módulo pede um gerador pelo nome (ex.: "astros/lua"); blocos espaciais
acrescentam suas coordenadas inteiras. O resultado só depende da semente
mestra, do nome e da chave do bloco — nunca da ordem em que os módulos rodam.
"""
import hashlib
import numpy as np

# Semente provisória. A semente do planeta é escolhida na F2 (tectônica) e
# fechada na F7; tudo o que a F1 sorteia é refeito com a semente final.
SEMENTE_PROVISORIA = 0


def gerador(nome, semente=SEMENTE_PROVISORIA, *bloco):
    chave = hashlib.sha256(f"{nome}|{','.join(map(str, bloco))}".encode()).digest()
    palavras = np.frombuffer(chave, dtype="<u4").tolist()
    return np.random.default_rng(np.random.SeedSequence([int(semente) & 0xFFFFFFFF,
                                                          int(semente) >> 32, *palavras]))
