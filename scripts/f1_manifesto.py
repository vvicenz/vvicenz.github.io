"""Gera dados/f1/manifesto.json: arquivos da fase com sha256, tamanho e
como regenerar. Arquivos com prefixo "_" são intermediários (não versionados)."""
import hashlib, json, pathlib, subprocess, sys, platform
import numpy, scipy, astropy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from mundo.constantes import PLANETA, TERRA
from mundo.semente import SEMENTE_PROVISORIA

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


arquivos = []
for pasta in ("dados/f1", "out/f1"):
    for p in sorted((RAIZ / pasta).rglob("*")):
        if p.is_file() and not p.name.startswith("_") and p.name != "manifesto.json":
            arquivos.append(dict(caminho=str(p.relative_to(RAIZ)), bytes=p.stat().st_size, sha256=sha(p)))
grade = json.loads((RAIZ / "dados/f1/terra/resumo_grade.json").read_text())
try:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=RAIZ, text=True).strip()
except Exception:
    commit = None
man = dict(
    fase="F1 · Astros e globo", plano="docs/v5-0-plano.md (rev. 1)", relatorio="docs/f1-relatorio.md",
    semente=SEMENTE_PROVISORIA, semente_status="provisória (a semente do planeta é escolhida na F2/F7)",
    codigo_base_commit=commit,
    ambiente=dict(python=platform.python_version(), numpy=numpy.__version__, scipy=scipy.__version__,
                  astropy=astropy.__version__),
    regenerar=["python3 scripts/terra_a_insolacao.py", "python3 scripts/terra_b_lua.py",
               "python3 scripts/terra_c_grade.py", "python3 scripts/planeta_a_lua_mare.py",
               "python3 scripts/planeta_b_insolacao_calendario.py", "python3 scripts/f1_graficos.py",
               "python3 scripts/f1_manifesto.py"],
    parametros_planeta={k: getattr(PLANETA, k) for k in ("ano_tropico_d", "excentricidade", "obliquidade_graus",
                                                          "lon_sol_perielio_graus", "lunacao_d", "s0")},
    derivados_planeta=PLANETA.derivados,
    grade_nivel1=dict(frequencia=300, n_celulas=grade["300"]["n_celulas"], sha256=grade["300"]["sha256"],
                      nota="não versionada: regenerar com mundo.grade.Grade(300) (~16 s); o hash confere"),
    arquivos=arquivos,
)
(RAIZ / "dados/f1/manifesto.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
print(len(arquivos), "arquivos no manifesto")
