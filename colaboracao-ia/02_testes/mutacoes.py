#!/usr/bin/env python3
"""Teste de mutação: prova que a suíte detecta defeitos reais no verificador.

Para cada mutação, copia `05_ferramentas/`, `02_testes/` e `01_dados/` para uma pasta temporária,
introduz UM defeito em `verificar_dados.py` e roda a suíte. Uma mutação "morta" (a suíte falha) é
o resultado esperado. Uma mutação "sobrevivente" significa que nenhum teste percebeu o defeito.

Uso: python3 colaboracao-ia/02_testes/mutacoes.py
Saída: 0 se todas as mutações foram detectadas; 1 se alguma sobreviveu.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

MUTACOES = [
    ("tradução entra no roteiro (gravações seriam invalidadas por tradução)",
     '                                       s["pausa_depois_ms"], imp_j))',
     '                                       s["pausa_depois_ms"], imp_j, I.get(("frase", s["id_frase"]), {}).get("imp_traducao", "")))'),
    ("seleção de áudio ignora os bytes do arquivo",
     'regs.append(registro(e["ordem"], r, a["sha256_arquivo"], a["imp_roteiro_gerado"]))',
     'regs.append(registro(e["ordem"], r, a["imp_roteiro_gerado"]))'),
    ("validação pedagógica da frase ignora a explicação",
     '                      "PEDAGOGICA": [f["imp_japones"], f["imp_traducao"], f["imp_explicacao"]]}[dimensao]',
     '                      "PEDAGOGICA": [f["imp_japones"], f["imp_traducao"]]}[dimensao]'),
    ("validação pedagógica do exercício ignora a gravação usada",
     '        return impressao(nome, imp_x, reg_resp, lista(reg_fr), lista(reg_fx), sel), resolvidos, None',
     '        return impressao(nome, imp_x, reg_resp, lista(reg_fr), lista(reg_fx)), resolvidos, None'),
    ("não detecta gravação com roteiro desatualizado",
     '            if arq["imp_roteiro_gerado"] and arq["imp_roteiro_gerado"] != atual:',
     '            if False:'),
    ("sem a regra 2 (resposta correta obrigatória)",
     '                self._exige(bool(corretas), "SEM_RESPOSTA_CORRETA", loc, "exercício ativo sem resposta CORRETA ativa")',
     '                pass'),
    ("atualizar-impressoes não sobe a versão",
     '                    if antiga and l[c_ver].isdigit():',
     '                    if False:'),
    ("permite duas gravações ativas (regra 7)",
     '            if len(arqs) > 1:',
     '            if len(arqs) > 2:'),
    ("aprovação de IA conta como final",
     '                if vig["status"] == "APROVADO" and vig["revisor"] not in APROVADORES_FINAIS[dim]:',
     '                if False:'),
    ("regra 6 não confere a tomada",
     "                esperado = f\"{l['id_audio']}_v{l['velocidade']}_r{l['versao_roteiro']}_t{l['tomada']}\"",
     '                esperado = k'),
    ("modo ATIVO não resolve a gravação ativa",
     '                    if len(ativos) == 1:\n                        arq = ativos[0]',
     '                    if len(ativos) == 1:\n                        arq = None'),
    ("FIXO aceita gravação de outra velocidade",
     '                        if arq["id_audio"] != e["id_audio"] or arq["velocidade"] != e["velocidade"]:',
     '                        if arq["id_audio"] != e["id_audio"]:'),
    ("validação desatualizada continua valendo",
     '            atuais = [t for t in vs if t[2] is not None and t[1]["imp_validada"] == t[2]',
     '            atuais = [t for t in vs if t[2] is not None'),
    ("japonês ignora a forma reduzida (furigana/texto da forma reduzida)",
     '"imp_japones": impressao("japones", f["forma_completa"], f["forma_reduzida"]),',
     '"imp_japones": impressao("japones", f["forma_completa"]),'),
    # Observação: retirar o campo `ordem` de dentro do registro do segmento é uma mutação
    # EQUIVALENTE (os segmentos já são ordenados por `ordem` antes do cálculo, e uma lacuna na
    # numeração é erro de dados). Por isso, a mutação abaixo ataca a ordenação em si.
    ("segmentos não são ordenados por `ordem` antes do cálculo do roteiro",
     '        for v in self.SEG.values():\n            v.sort(key=lambda s: int(s["ordem"]) if RE["inteiro_pos"].match(s["ordem"]) else 0)',
     '        for v in self.SEG.values():\n            pass'),
]


PASTAS = ("05_ferramentas", "02_testes", "01_dados", "03_revisao")


def rodar_suite(texto_verificador: str):
    with tempfile.TemporaryDirectory() as tmp:
        for pasta in PASTAS:
            shutil.copytree(RAIZ / pasta, Path(tmp) / pasta, ignore=shutil.ignore_patterns("__pycache__"))
        (Path(tmp) / "05_ferramentas" / "verificar_dados.py").write_text(texto_verificador, encoding="utf-8")
        return subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "02_testes", "-p", "test_*.py"],
                              cwd=tmp, capture_output=True, text=True)


def main():
    alvo_rel = Path("05_ferramentas/verificar_dados.py")
    original = (RAIZ / alvo_rel).read_text(encoding="utf-8")
    # Controle: sem mutação, a suíte tem de passar na cópia temporária. Senão, uma falha do ambiente
    # (pasta não copiada, teste dependente de git) "mataria" todas as mutações por engano.
    controle = rodar_suite(original)
    if controle.returncode != 0:
        print("CONTROLE FALHOU: a suíte não passa na cópia sem mutação; resultados seriam inválidos.")
        print("\n".join(l for l in controle.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))))
        return 2
    print("controle: suíte passa na cópia sem mutação\n")
    sobreviventes = []
    for nome, de, para in MUTACOES:
        if original.count(de) != 1:
            print(f"ERRO  trecho não encontrado exatamente uma vez: {nome}")
            sobreviventes.append(nome)
            continue
        r = rodar_suite(original.replace(de, para, 1))
        falhou = r.returncode != 0
        detalhe = [l for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        print(f"{'MORTA ' if falhou else 'VIVA  '} {nome}" + (f"  ← {detalhe[0]}" if detalhe else ""))
        if not falhou:
            sobreviventes.append(nome)
    print(f"\n{len(MUTACOES) - len(sobreviventes)} de {len(MUTACOES)} mutações detectadas")
    return 0 if not sobreviventes else 1


if __name__ == "__main__":
    sys.exit(main())
