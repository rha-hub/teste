#!/usr/bin/env python3
"""Confere que os quatro arquivos originais do projeto continuam intactos e que a branch só
altera caminhos dentro de `colaboracao-ia/`.

Verifica, para cada original:
  1. o blob no commit avaliado (padrão: HEAD) é igual ao blob registrado em `main`
     no commit ae55c1ae9afcaa2f438ef6639d63f565500d3fae;
  2. o arquivo na cópia de trabalho não tem alteração não commitada.
E também:
  3. `git diff --name-only <base> <commit>` só lista caminhos em `colaboracao-ia/`.

Uso: python3 verificar_originais.py [--commit HEAD] [--base ae55c1a…]
Saída: 0 = íntegro; 1 = alteração detectada; 3 = erro de uso (fora de um repositório git).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BASE_MAIN = "ae55c1ae9afcaa2f438ef6639d63f565500d3fae"
ORIGINAIS = {
    "O Japonês que Encolhe.html": "e9ba45b4fb3c00074f6ec80162d4a900280f7146",
    "paginas-modelo.html": "2a7eda7b13c243abf257a40be8997e5add574561",
    "docs/index.html": "1826247758d0a524c55afe208b09ba387aba9a49",
    "docs/Páginas-modelo · Cap. 4 · A tinta e carimbo  B educacional limpo (1).pdf": "4f255ddcfb1298f17d92f4ecc309f9fe8ad304a2",
}
PASTA_PERMITIDA = "colaboracao-ia/"


def git(raiz, *args):
    return subprocess.run(["git", "-C", str(raiz), "-c", "core.quotepath=off", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def main(argv=None):
    p = argparse.ArgumentParser(description="integridade dos arquivos originais")
    p.add_argument("--commit", default="HEAD")
    p.add_argument("--base", default=BASE_MAIN)
    p.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent)
    a = p.parse_args(argv)
    try:
        raiz = git(a.repo, "rev-parse", "--show-toplevel")
        commit = git(raiz, "rev-parse", a.commit)
    except subprocess.CalledProcessError:
        print("não foi possível localizar o repositório ou o commit", file=sys.stderr)
        return 3
    falhas = []
    print(f"Repositório: {raiz}\nCommit avaliado: {commit}\nBase: {a.base}\n")
    for caminho, esperado in ORIGINAIS.items():
        try:
            blob = git(raiz, "rev-parse", f"{commit}:{caminho}")
        except subprocess.CalledProcessError:
            blob = "(ausente)"
        sujo = git(raiz, "status", "--porcelain", "--", caminho) != ""
        ok = blob == esperado and not sujo
        print(f"{'OK   ' if ok else 'FALHA'} {caminho}\n      esperado {esperado}\n      no commit {blob}"
              + ("\n      alteração não commitada na cópia de trabalho" if sujo else ""))
        if not ok:
            falhas.append(caminho)
    try:
        base_ok = git(raiz, "cat-file", "-t", a.base) == "commit"
    except subprocess.CalledProcessError:
        base_ok = False
    if not base_ok:
        print(f"\nFALHA base {a.base} não encontrada (faça fetch com histórico suficiente)")
        falhas.append("base")
    else:
        alterados = [l for l in git(raiz, "diff", "--name-only", a.base, commit).splitlines() if l]
        fora = [c for c in alterados if not c.startswith(PASTA_PERMITIDA)]
        print(f"\nArquivos alterados entre base e commit: {len(alterados)}; fora de {PASTA_PERMITIDA}: {len(fora)}")
        for c in fora:
            print(f"FALHA alterado fora da pasta: {c}")
        falhas += fora
    print("\nResultado:", "ÍNTEGRO" if not falhas else f"{len(falhas)} FALHA(S)")
    return 0 if not falhas else 1


if __name__ == "__main__":
    sys.exit(main())
