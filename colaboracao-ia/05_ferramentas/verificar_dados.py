#!/usr/bin/env python3
"""Verificador de integridade e dependências — O Japonês por Trás das Palavras.

Implementa o esquema v5 de `01_dados/ESQUEMA.md`. Só usa a biblioteca padrão do Python (3.9+).

Subcomandos:
  verificar             lê os CSVs, confere estrutura, relações, impressões, gravações e
                        validações, e imprime um relatório. Não altera nenhum arquivo.
  atualizar-impressoes  recalcula as impressões CORRENTES (imp_japones, imp_traducao,
                        imp_explicacao, imp_exercicio, imp_resposta, imp_roteiro) e sobe a
                        versão da faceta que mudou. Nunca altera instantâneos
                        (imp_japones_usada, imp_roteiro_gerado, validações).
  fechar-roteiro ID     grava em audio_segmentos.imp_japones_usada a imp_japones atual das
                        frases da faixa ID (registra que o roteiro foi conferido).
  impressao-validacao ITEM DIMENSAO
                        imprime a imp_validada e os arquivos_audio_resolvidos que uma nova
                        linha de validacoes.csv deve conter para esse item e dimensão.
  verificar-apontamentos
                        confere 03_revisao/apontamentos.csv contra as regras do PROTOCOLO.md
                        (IDs únicos, evidência obrigatória, verificação independente).

Códigos de saída de `verificar`:
  0 = sem erros e sem pendências   1 = há ERRO (dados inválidos)
  2 = sem erros, mas há PENDENCIA (validação faltando/desatualizada, gravação desatualizada…)
  3 = erro de uso (pasta inexistente, argumento inválido)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

VERSAO_ESQUEMA = 5
PREFIXO_IMP = "imp-v1"
US, RS, GS = "\x1f", "\x1e", "\x1d"  # separadores: campos, registro interno, lista de registros
VELOCIDADES_PILOTO = {"100", "080"}

# ---------------------------------------------------------------------------
# Definição das tabelas (cabeçalhos exatos, na ordem)
# ---------------------------------------------------------------------------
CABECALHOS = {
    "frases.csv": ["id_frase", "capitulo", "licao", "forma_completa", "forma_reduzida", "reducao", "registro",
                   "traducao_ptbr", "explicacao_curta", "versao_japones", "versao_traducao", "versao_explicacao",
                   "imp_japones", "imp_traducao", "imp_explicacao", "situacao", "observacoes"],
    "exercicios.csv": ["id_exercicio", "capitulo", "licao", "degrau", "tipo", "enunciado", "frases_usadas",
                       "secao_que_ensina", "regra_comparacao", "versao", "imp_exercicio", "situacao", "observacoes"],
    "respostas.csv": ["id_resposta", "id_exercicio", "rotulo", "texto", "tipo", "explicacao", "versao",
                      "imp_resposta", "situacao", "observacoes"],
    "audios.csv": ["id_audio", "capitulo", "descricao", "versao_roteiro", "imp_roteiro", "qr_pagina", "situacao",
                   "observacoes"],
    "audio_segmentos.csv": ["id_audio", "ordem", "id_frase", "forma_falada", "personagem", "voz", "pausa_depois_ms",
                            "imp_japones_usada"],
    "arquivos_audio.csv": ["id_arquivo_audio", "id_audio", "velocidade", "versao_roteiro", "tomada",
                           "imp_roteiro_gerado", "arquivo", "sha256_arquivo", "gerado_em", "servico_modelo_voz",
                           "plano_licenca", "transcricao_confere", "situacao", "observacoes"],
    "exercicio_audios.csv": ["id_exercicio", "ordem", "id_audio", "velocidade", "modo_selecao", "id_arquivo_audio",
                             "uso", "observacoes"],
    "validacoes.csv": ["id_validacao", "data", "id_item", "dimensao", "imp_validada", "arquivos_audio_resolvidos",
                       "status", "revisor", "revisor_identificacao", "commit_revisado", "apontamento", "observacoes"],
}

RE = {
    "frase": re.compile(r"^J(\d{2})-\d{2,3}$"),
    "faixa": re.compile(r"^A(\d{2})-\d{2,3}$"),
    "exercicio": re.compile(r"^X(\d{2})-[A-Za-z0-9]+$"),
    "resposta": re.compile(r"^(X\d{2}-[A-Za-z0-9]+)-[a-z0-9]+$"),
    "arquivo": re.compile(r"^(A\d{2}-\d{2,3})_v(\d{3})_r([1-9]\d*)_t([1-9]\d*)$"),
    "validacao": re.compile(r"^V-(\d{4,})$"),
    "apontamento": re.compile(r"^(C\d{2}-[A-Z]+-\d{3}|P\d{2}|CL-\d{2})$"),
    "sha256": re.compile(r"^[0-9a-f]{64}$"),
    "commit": re.compile(r"^[0-9a-f]{40}$"),
    "velocidade": re.compile(r"^\d{3}$"),
    "inteiro_pos": re.compile(r"^[1-9]\d*$"),
    "inteiro_nn": re.compile(r"^(0|[1-9]\d*)$"),
    "capitulo": re.compile(r"^(0|[1-9]\d?)$"),
    "licao": re.compile(r"^\d{1,2}(\.\d{1,2})?$"),
    "data": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})$"),
}

ENUM = {
    "registro": {"FORMAL", "NEUTRO_POLIDO", "CASUAL", "RUDE", "REGIONAL"},
    "situacao_item": {"ATIVA", "RETIRADA"},
    "situacao_arquivo": {"ATIVO", "SUBSTITUIDO", "RETIRADO"},
    "degrau": {"RECONHECER", "ESCREVER", "ESCOLHER_TOM"},
    "tipo_exercicio": {"MULTIPLA_ESCOLHA", "ESCRITA", "ESCUTA"},
    "regra_comparacao": {"EXATA", "IGNORA_PONTUACAO_FINAL", "MANUAL"},
    "tipo_resposta": {"CORRETA", "ACEITA", "ERRADA"},
    "forma_falada": {"COMPLETA", "REDUZIDA"},
    "modo_selecao": {"ATIVO", "FIXO"},
    "uso": {"ESTIMULO", "APOIO"},
    "transcricao": {"SIM", "NAO", ""},
    "dimensao": {"LINGUISTICA", "TRADUCAO", "PEDAGOGICA", "ROTEIRO", "GRAVACAO", "ESCUTA"},
    "status": {"APROVADO", "AJUSTAR", "NAO_USAR", "PENDENTE_DE_VALIDACAO"},
    "revisor": {"HUMANO_JAPONES", "HUMANO_RESPONSAVEL", "HUMANO_OUTRO", "IA_CHATGPT", "IA_CLAUDE"},
}

# Quem pode dar aprovação FINAL em cada dimensão (decisões de 2026-10-30, 04_historico/DECISOES.md).
# Aprovação de IA é registrada como APROVADO_AUXILIAR e nunca conta como final.
APROVADORES_FINAIS = {
    "LINGUISTICA": {"HUMANO_JAPONES"},
    "TRADUCAO": {"HUMANO_JAPONES"},
    "PEDAGOGICA": {"HUMANO_JAPONES", "HUMANO_RESPONSAVEL"},
    "ROTEIRO": {"HUMANO_JAPONES", "HUMANO_RESPONSAVEL"},
    "GRAVACAO": {"HUMANO_JAPONES"},
    "ESCUTA": {"HUMANO_JAPONES", "HUMANO_RESPONSAVEL"},
}

FURIGANA_GRUPO = re.compile(r"\{([^{}|]+)\|([^{}|]+)\}")


# ---------------------------------------------------------------------------
# Impressões
# ---------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    """NFC, quebras de linha CRLF/CR -> LF, sem espaços nas pontas."""
    return unicodedata.normalize("NFC", texto.replace("\r\n", "\n").replace("\r", "\n")).strip()


def registro(*campos: str) -> str:
    return RS.join(normalizar(str(c)) for c in campos)


def lista(registros) -> str:
    return GS.join(registros)


def impressao(nome: str, *partes: str) -> str:
    entrada = US.join([PREFIXO_IMP, nome, *partes])
    return hashlib.sha256(entrada.encode("utf-8")).hexdigest()


def sha256_arquivo_em_disco(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 16), b""):
            h.update(bloco)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------
@dataclass
class Achado:
    severidade: str  # ERRO | PENDENCIA | AVISO
    codigo: str
    local: str
    mensagem: str

    def como_dict(self):
        return {"severidade": self.severidade, "codigo": self.codigo, "local": self.local, "mensagem": self.mensagem}


@dataclass
class Resultado:
    achados: list = field(default_factory=list)
    impressoes: dict = field(default_factory=dict)       # (tipo, id) -> {nome: valor}
    resolucao: dict = field(default_factory=dict)        # id_exercicio -> [id_arquivo|None]
    status_validacao: dict = field(default_factory=dict) # (id_item, dimensao) -> dict
    aprovacao_exercicio: dict = field(default_factory=dict)
    contagem_linhas: dict = field(default_factory=dict)

    def add(self, sev, cod, local, msg):
        self.achados.append(Achado(sev, cod, local, msg))

    def tem(self, codigo, local_contem=""):
        return any(a.codigo == codigo and local_contem in a.local for a in self.achados)

    def codigos(self):
        return sorted({a.codigo for a in self.achados})

    @property
    def codigo_saida(self):
        if any(a.severidade == "ERRO" for a in self.achados):
            return 1
        if any(a.severidade == "PENDENCIA" for a in self.achados):
            return 2
        return 0


# ---------------------------------------------------------------------------
# Leitura dos CSVs
# ---------------------------------------------------------------------------
def ler_tabela(pasta: Path, nome: str, R: Resultado):
    caminho = pasta / nome
    if not caminho.exists():
        R.add("ERRO", "ARQUIVO_AUSENTE", nome, "arquivo obrigatório não encontrado")
        return None
    bruto = caminho.read_bytes()
    if bruto.startswith(b"\xef\xbb\xbf"):
        R.add("ERRO", "CODIFICACAO", nome, "arquivo começa com BOM; use UTF-8 sem BOM")
        bruto = bruto[3:]
    if b"\r" in bruto:
        R.add("ERRO", "FIM_DE_LINHA", nome, "fim de linha CR/CRLF; use LF")
    try:
        texto = bruto.decode("utf-8")
    except UnicodeDecodeError as e:
        R.add("ERRO", "CODIFICACAO", nome, f"não é UTF-8 válido: {e}")
        return None
    leitor = csv.reader(io.StringIO(texto, newline=""))
    linhas = list(leitor)
    if not linhas:
        R.add("ERRO", "CABECALHO", nome, "arquivo vazio (falta o cabeçalho)")
        return None
    cab = linhas[0]
    esperado = CABECALHOS[nome]
    if cab != esperado:
        faltam = [c for c in esperado if c not in cab]
        sobram = [c for c in cab if c not in esperado]
        R.add("ERRO", "CABECALHO", nome,
              f"cabeçalho diferente do esquema v{VERSAO_ESQUEMA}; faltam {faltam}, sobram {sobram}"
              + ("" if faltam or sobram else "; ordem diferente"))
        return None
    dados = []
    for n, valores in enumerate(linhas[1:], start=2):
        if not valores or (len(valores) == 1 and valores[0] == ""):
            continue  # linha em branco no fim
        if len(valores) != len(cab):
            R.add("ERRO", "COLUNAS", f"{nome}:{n}", f"{len(valores)} colunas; o cabeçalho tem {len(cab)}")
            continue
        d = dict(zip(cab, valores))
        d["_linha"] = n
        dados.append(d)
    R.contagem_linhas[nome] = len(dados)
    return dados


def lista_ids(valor: str):
    return [x for x in valor.split("|")] if valor != "" else []


def data_valida(valor: str) -> bool:
    if not RE["data"].match(valor):
        return False
    try:
        datetime.fromisoformat(valor.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def furigana_valida(texto: str) -> bool:
    sem_grupos = FURIGANA_GRUPO.sub("", texto)
    return not any(c in sem_grupos for c in "{}|")


# ---------------------------------------------------------------------------
# Verificação
# ---------------------------------------------------------------------------
class Verificador:
    def __init__(self, pasta: Path, raiz_audio: Path | None = None):
        self.pasta = Path(pasta)
        self.raiz_audio = Path(raiz_audio) if raiz_audio else None
        self.R = Resultado()

    # -- utilidades ---------------------------------------------------------
    def _loc(self, tabela, linha, chave=""):
        return f"{tabela}:{linha['_linha']}" + (f" ({chave})" if chave else "")

    def _exige(self, cond, cod, local, msg, sev="ERRO"):
        if not cond:
            self.R.add(sev, cod, local, msg)
        return cond

    def _formato(self, tabela, linha, coluna, padrao=None, enum=None, obrigatorio=True, chave=""):
        v = linha[coluna]
        loc = self._loc(tabela, linha, chave)
        if v == "":
            if obrigatorio:
                self.R.add("ERRO", "CAMPO_VAZIO", loc, f"`{coluna}` é obrigatório")
            return False
        if padrao is not None and not RE[padrao].match(v):
            self.R.add("ERRO", "FORMATO", loc, f"`{coluna}`=`{v}` não segue o formato `{padrao}`")
            return False
        if enum is not None and v not in ENUM[enum]:
            self.R.add("ERRO", "VALOR_INVALIDO", loc, f"`{coluna}`=`{v}` não está em {sorted(ENUM[enum])}")
            return False
        return True

    def _unicos(self, tabela, linhas, chave_fn, rotulo):
        vistos = {}
        for l in linhas:
            k = chave_fn(l)
            if k in vistos:
                self.R.add("ERRO", "ID_DUPLICADO", self._loc(tabela, l),
                           f"{rotulo} `{k}` repetido (já na linha {vistos[k]})")
            else:
                vistos[k] = l["_linha"]

    # -- execução -----------------------------------------------------------
    def executar(self) -> Resultado:
        if not self.pasta.is_dir():
            raise FileNotFoundError(self.pasta)
        T = {n: ler_tabela(self.pasta, n, self.R) for n in CABECALHOS}
        if any(v is None for v in T.values()):
            return self.R  # sem estrutura válida, não há como seguir
        self.T = T
        self._validar_campos()
        self._indexar()
        self._validar_relacoes()
        self._calcular_impressoes()
        self._conferir_impressoes_gravadas()
        self._resolver_audios()
        self._conferir_instantaneos()
        self._conferir_arquivos_em_disco()
        self._avaliar_validacoes()
        self._avaliar_aprovacao()
        return self.R

    # -- 1. campos ----------------------------------------------------------
    def _validar_campos(self):
        T = self.T
        for l in T["frases.csv"]:
            t, k = "frases.csv", l["id_frase"]
            if self._formato(t, l, "id_frase", "frase", chave=k) and self._formato(t, l, "capitulo", "capitulo", chave=k):
                self._exige(int(RE["frase"].match(k).group(1)) == int(l["capitulo"]), "CAPITULO_ID",
                            self._loc(t, l, k), "o número do capítulo no ID não bate com `capitulo`")
            self._formato(t, l, "licao", "licao", obrigatorio=False, chave=k)
            self._formato(t, l, "forma_completa", chave=k)
            for c in ("forma_completa", "forma_reduzida"):
                self._exige(furigana_valida(l[c]), "FURIGANA", self._loc(t, l, k),
                            f"`{c}` tem marcação de furigana malformada; use {{kanji|leitura}}")
            self._formato(t, l, "registro", enum="registro", chave=k)
            self._formato(t, l, "traducao_ptbr", chave=k)
            for c in ("versao_japones", "versao_traducao", "versao_explicacao"):
                self._formato(t, l, c, "inteiro_pos", chave=k)
            for c in ("imp_japones", "imp_traducao", "imp_explicacao"):
                self._formato(t, l, c, "sha256", obrigatorio=False, chave=k)
            self._formato(t, l, "situacao", enum="situacao_item", chave=k)
        for l in T["exercicios.csv"]:
            t, k = "exercicios.csv", l["id_exercicio"]
            if self._formato(t, l, "id_exercicio", "exercicio", chave=k) and self._formato(t, l, "capitulo", "capitulo", chave=k):
                self._exige(int(RE["exercicio"].match(k).group(1)) == int(l["capitulo"]), "CAPITULO_ID",
                            self._loc(t, l, k), "o número do capítulo no ID não bate com `capitulo`")
            self._formato(t, l, "licao", "licao", obrigatorio=False, chave=k)
            self._formato(t, l, "degrau", enum="degrau", chave=k)
            self._formato(t, l, "tipo", enum="tipo_exercicio", chave=k)
            self._formato(t, l, "enunciado", chave=k)
            self._formato(t, l, "regra_comparacao", enum="regra_comparacao", chave=k)
            self._formato(t, l, "versao", "inteiro_pos", chave=k)
            self._formato(t, l, "imp_exercicio", "sha256", obrigatorio=False, chave=k)
            self._formato(t, l, "situacao", enum="situacao_item", chave=k)
            ids = lista_ids(l["frases_usadas"])
            self._exige(len(ids) > 0, "CAMPO_VAZIO", self._loc(t, l, k), "`frases_usadas` precisa de ao menos uma frase")
            for i in ids:
                self._exige(bool(RE["frase"].match(i)), "FORMATO", self._loc(t, l, k),
                            f"`frases_usadas` contém `{i}`, que não é ID de frase (listas usam `|`, sem espaços)")
            self._exige(len(ids) == len(set(ids)), "LISTA_REPETIDA", self._loc(t, l, k), "`frases_usadas` repete um ID")
        for l in T["respostas.csv"]:
            t, k = "respostas.csv", l["id_resposta"]
            if self._formato(t, l, "id_resposta", "resposta", chave=k):
                self._exige(RE["resposta"].match(k).group(1) == l["id_exercicio"], "ID_INCOERENTE",
                            self._loc(t, l, k), "o prefixo de `id_resposta` deve ser o `id_exercicio` da linha")
            self._formato(t, l, "id_exercicio", "exercicio", chave=k)
            self._formato(t, l, "texto", chave=k)
            self._formato(t, l, "tipo", enum="tipo_resposta", chave=k)
            self._formato(t, l, "versao", "inteiro_pos", chave=k)
            self._formato(t, l, "imp_resposta", "sha256", obrigatorio=False, chave=k)
            self._formato(t, l, "situacao", enum="situacao_item", chave=k)
        for l in T["audios.csv"]:
            t, k = "audios.csv", l["id_audio"]
            if self._formato(t, l, "id_audio", "faixa", chave=k) and self._formato(t, l, "capitulo", "capitulo", chave=k):
                self._exige(int(RE["faixa"].match(k).group(1)) == int(l["capitulo"]), "CAPITULO_ID",
                            self._loc(t, l, k), "o número do capítulo no ID não bate com `capitulo`")
            self._formato(t, l, "versao_roteiro", "inteiro_pos", chave=k)
            self._formato(t, l, "imp_roteiro", "sha256", obrigatorio=False, chave=k)
            self._formato(t, l, "situacao", enum="situacao_item", chave=k)
        for l in T["audio_segmentos.csv"]:
            t, k = "audio_segmentos.csv", f"{l['id_audio']}#{l['ordem']}"
            self._formato(t, l, "id_audio", "faixa", chave=k)
            self._formato(t, l, "ordem", "inteiro_pos", chave=k)
            self._formato(t, l, "id_frase", "frase", chave=k)
            self._formato(t, l, "forma_falada", enum="forma_falada", chave=k)
            self._formato(t, l, "personagem", chave=k)
            self._formato(t, l, "voz", chave=k)
            self._formato(t, l, "pausa_depois_ms", "inteiro_nn", chave=k)
            self._formato(t, l, "imp_japones_usada", "sha256", obrigatorio=False, chave=k)
        for l in T["arquivos_audio.csv"]:
            t, k = "arquivos_audio.csv", l["id_arquivo_audio"]
            ok = self._formato(t, l, "id_arquivo_audio", "arquivo", chave=k)
            ok &= self._formato(t, l, "id_audio", "faixa", chave=k)
            ok &= self._formato(t, l, "velocidade", "velocidade", chave=k)
            ok &= self._formato(t, l, "versao_roteiro", "inteiro_pos", chave=k)
            ok &= self._formato(t, l, "tomada", "inteiro_pos", chave=k)
            if ok:  # regra 6: o ID é exatamente a composição das quatro colunas
                esperado = f"{l['id_audio']}_v{l['velocidade']}_r{l['versao_roteiro']}_t{l['tomada']}"
                self._exige(k == esperado, "ID_ARQUIVO_INCOERENTE", self._loc(t, l, k),
                            f"`id_arquivo_audio` deveria ser `{esperado}` pelas colunas da linha")
            if l["velocidade"] and RE["velocidade"].match(l["velocidade"]):
                v = int(l["velocidade"])
                if not (10 <= v <= 200):
                    self.R.add("ERRO", "VELOCIDADE", self._loc(t, l, k), "velocidade fora de 010–200")
                elif l["velocidade"] not in VELOCIDADES_PILOTO:
                    self.R.add("AVISO", "VELOCIDADE_FORA_DO_PILOTO", self._loc(t, l, k),
                               f"velocidade {l['velocidade']} não é uma das previstas no piloto (100, 080)")
            self._formato(t, l, "imp_roteiro_gerado", "sha256", chave=k)
            self._formato(t, l, "arquivo", chave=k)
            self._formato(t, l, "sha256_arquivo", "sha256", chave=k)
            if self._formato(t, l, "gerado_em", chave=k):
                self._exige(data_valida(l["gerado_em"]), "FORMATO", self._loc(t, l, k),
                            "`gerado_em` deve ser ISO 8601 com fuso")
            self._formato(t, l, "servico_modelo_voz", chave=k)
            self._formato(t, l, "plano_licenca", chave=k)
            self._exige(l["transcricao_confere"] in ENUM["transcricao"], "VALOR_INVALIDO", self._loc(t, l, k),
                        "`transcricao_confere` deve ser SIM, NAO ou vazio")
            self._formato(t, l, "situacao", enum="situacao_arquivo", chave=k)
            arq = l["arquivo"]
            self._exige(not (arq.startswith("/") or ".." in Path(arq).parts or re.match(r"^[A-Za-z]:", arq)),
                        "CAMINHO", self._loc(t, l, k), "`arquivo` deve ser caminho relativo, sem `..`")
        for l in T["exercicio_audios.csv"]:
            t, k = "exercicio_audios.csv", f"{l['id_exercicio']}#{l['ordem']}"
            self._formato(t, l, "id_exercicio", "exercicio", chave=k)
            self._formato(t, l, "ordem", "inteiro_pos", chave=k)
            self._formato(t, l, "id_audio", "faixa", chave=k)
            if self._formato(t, l, "velocidade", "velocidade", chave=k) and l["velocidade"] not in VELOCIDADES_PILOTO:
                self.R.add("AVISO", "VELOCIDADE_FORA_DO_PILOTO", self._loc(t, l, k),
                           f"velocidade {l['velocidade']} não é uma das previstas no piloto (100, 080)")
            self._formato(t, l, "modo_selecao", enum="modo_selecao", chave=k)
            self._formato(t, l, "id_arquivo_audio", "arquivo", obrigatorio=False, chave=k)
            self._formato(t, l, "uso", enum="uso", chave=k)
        for l in T["validacoes.csv"]:
            t, k = "validacoes.csv", l["id_validacao"]
            self._formato(t, l, "id_validacao", "validacao", chave=k)
            if self._formato(t, l, "data", chave=k):
                self._exige(data_valida(l["data"]), "FORMATO", self._loc(t, l, k), "`data` deve ser ISO 8601 com fuso")
            self._formato(t, l, "id_item", chave=k)
            self._formato(t, l, "dimensao", enum="dimensao", chave=k)
            self._formato(t, l, "imp_validada", "sha256", chave=k)
            self._formato(t, l, "status", enum="status", chave=k)
            if self._formato(t, l, "revisor", enum="revisor", chave=k) and l["revisor"].startswith("HUMANO_"):
                self._exige(l["revisor_identificacao"].strip() != "", "REVISOR_SEM_IDENTIFICACAO",
                            self._loc(t, l, k), "validação humana precisa de `revisor_identificacao`")
            self._formato(t, l, "commit_revisado", "commit", chave=k)
            self._formato(t, l, "apontamento", "apontamento", obrigatorio=False, chave=k)
            for i in lista_ids(l["arquivos_audio_resolvidos"]):
                self._exige(bool(RE["arquivo"].match(i)), "FORMATO", self._loc(t, l, k),
                            f"`arquivos_audio_resolvidos` contém `{i}`, que não é ID de arquivo")

    # -- 2. índices, unicidade ---------------------------------------------
    def _indexar(self):
        T = self.T
        self._unicos("frases.csv", T["frases.csv"], lambda l: l["id_frase"], "id_frase")
        self._unicos("exercicios.csv", T["exercicios.csv"], lambda l: l["id_exercicio"], "id_exercicio")
        self._unicos("respostas.csv", T["respostas.csv"], lambda l: l["id_resposta"], "id_resposta")
        self._unicos("audios.csv", T["audios.csv"], lambda l: l["id_audio"], "id_audio")
        self._unicos("audio_segmentos.csv", T["audio_segmentos.csv"], lambda l: (l["id_audio"], l["ordem"]),
                     "(id_audio, ordem)")
        self._unicos("arquivos_audio.csv", T["arquivos_audio.csv"], lambda l: l["id_arquivo_audio"], "id_arquivo_audio")
        self._unicos("arquivos_audio.csv", T["arquivos_audio.csv"],
                     lambda l: (l["id_audio"], l["velocidade"], l["versao_roteiro"], l["tomada"]),
                     "(id_audio, velocidade, versao_roteiro, tomada)")
        self._unicos("exercicio_audios.csv", T["exercicio_audios.csv"], lambda l: (l["id_exercicio"], l["ordem"]),
                     "(id_exercicio, ordem)")
        self._unicos("validacoes.csv", T["validacoes.csv"], lambda l: l["id_validacao"], "id_validacao")
        # IDs globais não podem colidir entre tabelas (ex.: uma validação apontando para um ID ambíguo)
        self.F = {l["id_frase"]: l for l in T["frases.csv"]}
        self.X = {l["id_exercicio"]: l for l in T["exercicios.csv"]}
        self.RSP = defaultdict(list)
        for l in T["respostas.csv"]:
            self.RSP[l["id_exercicio"]].append(l)
        self.A = {l["id_audio"]: l for l in T["audios.csv"]}
        self.SEG = defaultdict(list)
        for l in T["audio_segmentos.csv"]:
            self.SEG[l["id_audio"]].append(l)
        for v in self.SEG.values():
            v.sort(key=lambda s: int(s["ordem"]) if RE["inteiro_pos"].match(s["ordem"]) else 0)
        self.ARQ = {l["id_arquivo_audio"]: l for l in T["arquivos_audio.csv"]}
        self.EA = defaultdict(list)
        for l in T["exercicio_audios.csv"]:
            self.EA[l["id_exercicio"]].append(l)
        for v in self.EA.values():
            v.sort(key=lambda s: int(s["ordem"]) if RE["inteiro_pos"].match(s["ordem"]) else 0)
        self.ATIVOS = defaultdict(list)
        for l in T["arquivos_audio.csv"]:
            if l["situacao"] == "ATIVO":
                self.ATIVOS[(l["id_audio"], l["velocidade"])].append(l)

    # -- 3. relações (regras 1 a 11 e derivadas) ----------------------------
    def _validar_relacoes(self):
        T = self.T
        ativa = lambda d, k: k in d and d[k]["situacao"] == "ATIVA"
        # exercícios -> frases (regras 1, 4, 5)
        for x in T["exercicios.csv"]:
            loc = self._loc("exercicios.csv", x, x["id_exercicio"])
            for i in lista_ids(x["frases_usadas"]):
                if i not in self.F:
                    self.R.add("ERRO", "REFERENCIA_INEXISTENTE", loc, f"frase `{i}` não existe em frases.csv")
                    continue
                if x["situacao"] == "ATIVA" and self.F[i]["situacao"] != "ATIVA":
                    self.R.add("ERRO", "REFERENCIA_RETIRADA", loc, f"exercício ativo usa a frase retirada `{i}`")
                fc, xc = self.F[i]["capitulo"], x["capitulo"]
                if fc.isdigit() and xc.isdigit() and int(fc) > int(xc):
                    self.R.add("ERRO", "CAPITULO_POSTERIOR", loc, f"usa `{i}`, de capítulo posterior ({fc} > {xc})")
            # regra 2
            if x["situacao"] == "ATIVA":
                corretas = [r for r in self.RSP.get(x["id_exercicio"], []) if r["tipo"] == "CORRETA" and r["situacao"] == "ATIVA"]
                self._exige(bool(corretas), "SEM_RESPOSTA_CORRETA", loc, "exercício ativo sem resposta CORRETA ativa")
            # ESCUTA precisa de áudio-estímulo
            eas = self.EA.get(x["id_exercicio"], [])
            if x["tipo"] == "ESCUTA":
                self._exige(any(e["uso"] == "ESTIMULO" for e in eas), "ESCUTA_SEM_AUDIO", loc,
                            "exercício de ESCUTA sem nenhum áudio com `uso=ESTIMULO` em exercicio_audios.csv")
        # respostas -> exercício
        for r in T["respostas.csv"]:
            loc = self._loc("respostas.csv", r, r["id_resposta"])
            if r["id_exercicio"] not in self.X:
                self.R.add("ERRO", "REFERENCIA_INEXISTENTE", loc, f"exercício `{r['id_exercicio']}` não existe")
        # regra 3: faixas e segmentos
        for a in T["audios.csv"]:
            loc = self._loc("audios.csv", a, a["id_audio"])
            segs = self.SEG.get(a["id_audio"], [])
            if a["situacao"] == "ATIVA":
                self._exige(bool(segs), "FAIXA_SEM_SEGMENTOS", loc, "faixa ativa sem segmentos em audio_segmentos.csv")
            ordens = [s["ordem"] for s in segs]
            if segs and ordens != [str(i) for i in range(1, len(segs) + 1)]:
                self.R.add("ERRO", "ORDEM_COM_BURACO", loc, f"`ordem` dos segmentos deve ser 1..{len(segs)}; é {ordens}")
        for s in T["audio_segmentos.csv"]:
            loc = self._loc("audio_segmentos.csv", s, f"{s['id_audio']}#{s['ordem']}")
            if s["id_audio"] not in self.A:
                self.R.add("ERRO", "REFERENCIA_INEXISTENTE", loc, f"faixa `{s['id_audio']}` não existe em audios.csv")
            if s["id_frase"] not in self.F:
                self.R.add("ERRO", "REFERENCIA_INEXISTENTE", loc, f"frase `{s['id_frase']}` não existe em frases.csv")
                continue
            f = self.F[s["id_frase"]]
            if ativa(self.A, s["id_audio"]) and f["situacao"] != "ATIVA":
                self.R.add("ERRO", "REFERENCIA_RETIRADA", loc, f"faixa ativa fala a frase retirada `{s['id_frase']}`")
            if s["forma_falada"] == "REDUZIDA" and f["forma_reduzida"] == "":
                self.R.add("ERRO", "FORMA_INEXISTENTE", loc, f"`forma_falada=REDUZIDA`, mas `{s['id_frase']}` não tem forma reduzida")
        # arquivos -> faixa (regras 1, 4, 7)
        for arq in T["arquivos_audio.csv"]:
            loc = self._loc("arquivos_audio.csv", arq, arq["id_arquivo_audio"])
            a = self.A.get(arq["id_audio"])
            if a is None:
                self.R.add("ERRO", "REFERENCIA_INEXISTENTE", loc, f"faixa `{arq['id_audio']}` não existe em audios.csv")
                continue
            if arq["situacao"] == "ATIVO" and a["situacao"] != "ATIVA":
                self.R.add("ERRO", "REFERENCIA_RETIRADA", loc, "arquivo ATIVO de faixa retirada")
            if arq["versao_roteiro"].isdigit() and a["versao_roteiro"].isdigit() and int(arq["versao_roteiro"]) > int(a["versao_roteiro"]):
                self.R.add("ERRO", "VERSAO_FUTURA", loc,
                           f"gravado do roteiro v{arq['versao_roteiro']}, mas a faixa está na v{a['versao_roteiro']}")
        for (faixa, vel), arqs in self.ATIVOS.items():
            if len(arqs) > 1:
                self.R.add("ERRO", "MAIS_DE_UM_ATIVO", f"arquivos_audio.csv ({faixa}, {vel})",
                           f"{len(arqs)} arquivos ATIVO: {[x['id_arquivo_audio'] for x in arqs]}")
        # exercicio_audios (regras 3, 9, 10, 11)
        for idx, eas in self.EA.items():
            ordens = [e["ordem"] for e in eas]
            if ordens != [str(i) for i in range(1, len(eas) + 1)]:
                self.R.add("ERRO", "ORDEM_COM_BURACO", f"exercicio_audios.csv ({idx})",
                           f"`ordem` deve ser 1..{len(eas)}; é {ordens}")
        for e in T["exercicio_audios.csv"]:
            loc = self._loc("exercicio_audios.csv", e, f"{e['id_exercicio']}#{e['ordem']}")
            x = self.X.get(e["id_exercicio"])
            if x is None:
                self.R.add("ERRO", "REFERENCIA_INEXISTENTE", loc, f"exercício `{e['id_exercicio']}` não existe")
            if e["id_audio"] not in self.A:
                self.R.add("ERRO", "REFERENCIA_INEXISTENTE", loc, f"faixa `{e['id_audio']}` não existe em audios.csv")
            elif x is not None and x["situacao"] == "ATIVA" and self.A[e["id_audio"]]["situacao"] != "ATIVA":
                self.R.add("ERRO", "REFERENCIA_RETIRADA", loc, f"exercício ativo usa a faixa retirada `{e['id_audio']}`")
            if e["modo_selecao"] == "FIXO":
                if e["id_arquivo_audio"] == "":
                    self.R.add("ERRO", "FIXO_SEM_ARQUIVO", loc, "modo FIXO exige `id_arquivo_audio`")
            elif e["modo_selecao"] == "ATIVO" and e["id_arquivo_audio"] != "":
                self.R.add("ERRO", "ATIVO_COM_ARQUIVO", loc, "modo ATIVO exige `id_arquivo_audio` vazio")

    # -- 4. impressões correntes -------------------------------------------
    def _calcular_impressoes(self):
        I = self.R.impressoes
        for k, f in self.F.items():
            I[("frase", k)] = {
                "imp_japones": impressao("japones", f["forma_completa"], f["forma_reduzida"]),
                "imp_traducao": impressao("traducao", f["traducao_ptbr"]),
                "imp_explicacao": impressao("explicacao", f["reducao"], f["registro"], f["explicacao_curta"]),
            }
        for k, r in ((r["id_resposta"], r) for v in self.RSP.values() for r in v):
            I[("resposta", k)] = {"imp_resposta": impressao("resposta", r["rotulo"], r["tipo"], r["texto"], r["explicacao"])}
        for k, x in self.X.items():
            ea = lista(registro(e["ordem"], e["id_audio"], e["velocidade"], e["modo_selecao"], e["id_arquivo_audio"], e["uso"])
                       for e in self.EA.get(k, []))
            I[("exercicio", k)] = {"imp_exercicio": impressao(
                "exercicio", x["degrau"], x["tipo"], x["enunciado"], "|".join(sorted(lista_ids(x["frases_usadas"]))),
                x["secao_que_ensina"], x["regra_comparacao"], ea)}
        for k in self.A:
            partes = []
            for s in self.SEG.get(k, []):
                imp_j = I.get(("frase", s["id_frase"]), {}).get("imp_japones", "")
                partes.append(registro(s["ordem"], s["id_frase"], s["forma_falada"], s["personagem"], s["voz"],
                                       s["pausa_depois_ms"], imp_j))
            I[("faixa", k)] = {"imp_roteiro": impressao("roteiro", lista(partes))}

    def _conferir_impressoes_gravadas(self):
        I = self.R.impressoes
        pares = [("frases.csv", "frase", "id_frase", ["imp_japones", "imp_traducao", "imp_explicacao"]),
                 ("exercicios.csv", "exercicio", "id_exercicio", ["imp_exercicio"]),
                 ("respostas.csv", "resposta", "id_resposta", ["imp_resposta"]),
                 ("audios.csv", "faixa", "id_audio", ["imp_roteiro"])]
        for tabela, tipo, chave, colunas in pares:
            for l in self.T[tabela]:
                calc = I.get((tipo, l[chave]))
                if not calc:
                    continue
                for c in colunas:
                    if l[c] == "":
                        self.R.add("ERRO", "IMPRESSAO_NAO_GRAVADA", self._loc(tabela, l, l[chave]),
                                   f"`{c}` vazia; rode `atualizar-impressoes`")
                    elif l[c] != calc[c]:
                        self.R.add("ERRO", "IMPRESSAO_GRAVADA_DIVERGENTE", self._loc(tabela, l, l[chave]),
                                   f"`{c}` gravada não corresponde ao conteúdo atual; o conteúdo mudou sem "
                                   f"`atualizar-impressoes` (que também sobe a versão)")

    # -- 5. resolução da gravação de cada exercício -------------------------
    def _resolver_audios(self):
        for idx, eas in self.EA.items():
            x = self.X.get(idx)
            ativo_ex = x is not None and x["situacao"] == "ATIVA"
            resolvidos = []
            for e in eas:
                loc = self._loc("exercicio_audios.csv", e, f"{idx}#{e['ordem']}")
                arq = None
                if e["modo_selecao"] == "FIXO" and e["id_arquivo_audio"]:
                    arq = self.ARQ.get(e["id_arquivo_audio"])
                    if arq is None:
                        self.R.add("ERRO", "ARQUIVO_INEXISTENTE", loc, f"gravação `{e['id_arquivo_audio']}` não existe em arquivos_audio.csv")
                    else:
                        if arq["id_audio"] != e["id_audio"] or arq["velocidade"] != e["velocidade"]:
                            self.R.add("ERRO", "FIXO_INCOERENTE", loc,
                                       f"`{arq['id_arquivo_audio']}` é da faixa {arq['id_audio']} a {arq['velocidade']}, "
                                       f"mas a linha pede {e['id_audio']} a {e['velocidade']}")
                            arq = None
                        elif arq["situacao"] == "RETIRADO":
                            self.R.add("ERRO", "FIXO_RETIRADO", loc, f"modo FIXO aponta para gravação RETIRADA `{arq['id_arquivo_audio']}`")
                            arq = None
                        elif arq["situacao"] == "SUBSTITUIDO":
                            self.R.add("AVISO", "FIXO_SUBSTITUIDO", loc,
                                       f"modo FIXO usa `{arq['id_arquivo_audio']}`, que não é mais a gravação ativa; "
                                       f"migrar ou justificar em `observacoes`")
                elif e["modo_selecao"] == "ATIVO":
                    ativos = self.ATIVOS.get((e["id_audio"], e["velocidade"]), [])
                    if len(ativos) == 1:
                        arq = ativos[0]
                    elif not ativos and ativo_ex:
                        self.R.add("ERRO", "SEM_GRAVACAO_ATIVA", loc,
                                   f"nenhuma gravação ATIVO para {e['id_audio']} a {e['velocidade']}; o exercício ficaria sem áudio")
                resolvidos.append(arq["id_arquivo_audio"] if arq else None)
            self.R.resolucao[idx] = resolvidos

    def _imp_selecao_audio(self, idx):
        res = self.R.resolucao.get(idx, [])
        if any(r is None for r in res):
            return None
        regs = []
        for e, r in zip(self.EA.get(idx, []), res):
            a = self.ARQ[r]
            regs.append(registro(e["ordem"], r, a["sha256_arquivo"], a["imp_roteiro_gerado"]))
        return impressao("selecao_audio", lista(regs))

    # -- 6. instantâneos: roteiro fechado e gravação vs roteiro atual -------
    def _conferir_instantaneos(self):
        I = self.R.impressoes
        for s in self.T["audio_segmentos.csv"]:
            if s["id_frase"] not in self.F:
                continue
            loc = self._loc("audio_segmentos.csv", s, f"{s['id_audio']}#{s['ordem']}")
            atual = I[("frase", s["id_frase"])]["imp_japones"]
            if s["imp_japones_usada"] == "":
                self.R.add("PENDENCIA", "ROTEIRO_NAO_FECHADO", loc, "segmento sem `imp_japones_usada`; rode `fechar-roteiro`")
            elif s["imp_japones_usada"] != atual:
                self.R.add("PENDENCIA", "ROTEIRO_DESATUALIZADO", loc,
                           f"o japonês de `{s['id_frase']}` mudou depois que o roteiro de `{s['id_audio']}` foi fechado")
        for arq in self.T["arquivos_audio.csv"]:
            if arq["situacao"] != "ATIVO" or arq["id_audio"] not in self.A:
                continue
            atual = I[("faixa", arq["id_audio"])]["imp_roteiro"]
            if arq["imp_roteiro_gerado"] and arq["imp_roteiro_gerado"] != atual:
                self.R.add("PENDENCIA", "GRAVACAO_DESATUALIZADA", self._loc("arquivos_audio.csv", arq, arq["id_arquivo_audio"]),
                           "o roteiro atual da faixa é diferente do roteiro usado na gravação; gravar de novo")

    def _conferir_arquivos_em_disco(self):
        arqs = self.T["arquivos_audio.csv"]
        if not arqs:
            return
        if self.raiz_audio is None:
            self.R.add("AVISO", "AUDIO_NAO_CONFERIDO", "arquivos_audio.csv",
                       "bytes dos arquivos de áudio não conferidos (sem --raiz-audio); áudios comerciais não ficam neste repositório")
            return
        for a in arqs:
            if a["situacao"] == "RETIRADO" or not a["arquivo"]:
                continue
            loc = self._loc("arquivos_audio.csv", a, a["id_arquivo_audio"])
            p = self.raiz_audio / a["arquivo"]
            if not p.is_file():
                self.R.add("AVISO", "AUDIO_AUSENTE", loc, f"arquivo `{a['arquivo']}` não encontrado em --raiz-audio; não conferido")
            elif sha256_arquivo_em_disco(p) != a["sha256_arquivo"]:
                self.R.add("ERRO", "AUDIO_SHA_DIVERGENTE", loc, "o arquivo em disco não corresponde a `sha256_arquivo` (troca sem registro)")

    # -- 7. validações ------------------------------------------------------
    def tipo_do_item(self, id_item):
        if id_item in self.F:
            return "frase"
        if id_item in self.X:
            return "exercicio"
        if id_item in self.A:
            return "faixa"
        if id_item in self.ARQ:
            return "arquivo"
        return None

    def impressao_dimensao(self, id_item, dimensao):
        """Impressão de dependência (imp_validada esperada) e gravações resolvidas, ou (None, motivo)."""
        I = self.R.impressoes
        tipo = self.tipo_do_item(id_item)
        permitidos = {"LINGUISTICA": {"frase"}, "TRADUCAO": {"frase"}, "PEDAGOGICA": {"frase", "exercicio"},
                      "ROTEIRO": {"faixa"}, "GRAVACAO": {"arquivo"}, "ESCUTA": {"exercicio"}}
        if tipo is None:
            return None, [], "item inexistente"
        if tipo not in permitidos[dimensao]:
            return None, [], f"dimensão {dimensao} não se aplica a {tipo}"
        nome = f"dim:{dimensao}"
        if tipo == "frase":
            f = I[("frase", id_item)]
            partes = {"LINGUISTICA": [f["imp_japones"]],
                      "TRADUCAO": [f["imp_japones"], f["imp_traducao"]],
                      "PEDAGOGICA": [f["imp_japones"], f["imp_traducao"], f["imp_explicacao"]]}[dimensao]
            return impressao(nome, *partes), [], None
        if tipo == "faixa":
            return impressao(nome, I[("faixa", id_item)]["imp_roteiro"]), [], None
        if tipo == "arquivo":
            a = self.ARQ[id_item]
            return impressao(nome, a["sha256_arquivo"], a["imp_roteiro_gerado"]), [], None
        # exercício
        x = self.X[id_item]
        eas = self.EA.get(id_item, [])
        if dimensao == "ESCUTA" and not eas:
            return None, [], "ESCUTA só se aplica a exercício com áudio"
        sel = self._imp_selecao_audio(id_item) if eas else impressao("selecao_audio", "")
        if sel is None:
            return None, [], "gravação não resolvida (ver erros de exercicio_audios)"
        resolvidos = [r for r in self.R.resolucao.get(id_item, [])]
        imp_x = I[("exercicio", id_item)]["imp_exercicio"]
        if dimensao == "ESCUTA":
            return impressao(nome, imp_x, sel), resolvidos, None
        resps = sorted((r for r in self.RSP.get(id_item, []) if r["situacao"] == "ATIVA"), key=lambda r: r["id_resposta"])
        reg_resp = lista(registro(r["id_resposta"], I[("resposta", r["id_resposta"])]["imp_resposta"]) for r in resps)
        reg_fr = []
        for i in sorted(lista_ids(x["frases_usadas"])):
            if ("frase", i) not in I:
                return None, [], f"frase `{i}` inexistente"
            f = I[("frase", i)]
            reg_fr.append(registro(i, f["imp_japones"], f["imp_traducao"], f["imp_explicacao"]))
        faixas = sorted({e["id_audio"] for e in eas})
        reg_fx = []
        for fx in faixas:
            if ("faixa", fx) not in I:
                return None, [], f"faixa `{fx}` inexistente"
            reg_fx.append(registro(fx, I[("faixa", fx)]["imp_roteiro"]))
        return impressao(nome, imp_x, reg_resp, lista(reg_fr), lista(reg_fx), sel), resolvidos, None

    def _avaliar_validacoes(self):
        grupos = defaultdict(list)
        for v in self.T["validacoes.csv"]:
            loc = self._loc("validacoes.csv", v, v["id_validacao"])
            tipo = self.tipo_do_item(v["id_item"])
            if tipo is None:
                self.R.add("ERRO", "REFERENCIA_INEXISTENTE", loc, f"`id_item` `{v['id_item']}` não existe")
                continue
            if v["dimensao"] not in ENUM["dimensao"]:
                continue
            imp, resolvidos, motivo = self.impressao_dimensao(v["id_item"], v["dimensao"])
            if motivo and ("não se aplica" in motivo or "só se aplica" in motivo):
                self.R.add("ERRO", "DIMENSAO_INCOMPATIVEL", loc, motivo)
                continue
            precisa_lista = tipo == "exercicio" and bool(self.EA.get(v["id_item"]))
            lst = lista_ids(v["arquivos_audio_resolvidos"])
            if precisa_lista and len(lst) != len(self.EA[v["id_item"]]):
                self.R.add("ERRO", "RESOLVIDOS_INCOMPLETO", loc,
                           f"`arquivos_audio_resolvidos` deve listar {len(self.EA[v['id_item']])} gravação(ões), na ordem de exercicio_audios")
            if not precisa_lista and lst:
                self.R.add("ERRO", "RESOLVIDOS_INDEVIDO", loc, "`arquivos_audio_resolvidos` deve ficar vazio para este item")
            m = RE["validacao"].match(v["id_validacao"])
            grupos[(v["id_item"], v["dimensao"])].append((int(m.group(1)) if m else 0, v, imp, resolvidos))
        for (item, dim), vs in grupos.items():
            vs.sort(key=lambda t: t[0])
            atuais = [t for t in vs if t[2] is not None and t[1]["imp_validada"] == t[2]
                      and lista_ids(t[1]["arquivos_audio_resolvidos"]) == [r or "" for r in t[3]]]
            mais_recente = vs[-1]
            info = {"item": item, "dimensao": dim, "validacoes": [t[1]["id_validacao"] for t in vs]}
            if atuais:
                vig = atuais[-1][1]
                info.update(vigente=vig["id_validacao"], status=vig["status"], revisor=vig["revisor"])
                if vig["status"] == "APROVADO" and vig["revisor"] not in APROVADORES_FINAIS[dim]:
                    info["status_efetivo"] = "APROVADO_AUXILIAR"
                else:
                    info["status_efetivo"] = vig["status"]
                if atuais[-1] is not mais_recente:
                    self.R.add("AVISO", "VALIDACAO_RECENTE_DE_OUTRA_VERSAO", f"validacoes ({item}, {dim})",
                               f"a mais recente ({mais_recente[1]['id_validacao']}) foi feita sobre outra versão; "
                               f"vale {vig['id_validacao']}, cujo conteúdo é igual ao atual")
            else:
                info.update(vigente=None, status_efetivo="DESATUALIZADA")
                motivo = "o conteúdo ou alguma dependência mudou depois dela"
                ult = mais_recente[1]
                atuais_res = [r or "" for r in mais_recente[3]]
                if lista_ids(ult["arquivos_audio_resolvidos"]) and lista_ids(ult["arquivos_audio_resolvidos"]) != atuais_res:
                    motivo = (f"a gravação usada mudou: validada com {lista_ids(ult['arquivos_audio_resolvidos'])}, "
                              f"hoje resolve para {atuais_res}")
                self.R.add("PENDENCIA", "VALIDACAO_DESATUALIZADA", f"validacoes ({item}, {dim})",
                           f"{ult['id_validacao']} ({ult['status']}) não vale mais: {motivo}")
            self.R.status_validacao[(item, dim)] = info

    # -- 8. aprovação efetiva ----------------------------------------------
    def _status(self, item, dim):
        return self.R.status_validacao.get((item, dim), {}).get("status_efetivo", "SEM_VALIDACAO")

    def _exigir_final(self, item, dim, motivos, rotulo):
        s = self._status(item, dim)
        if s != "APROVADO":
            motivos.append(f"{rotulo} {item} {dim}: {s}")
            return False
        return True

    def _avaliar_aprovacao(self):
        """Lista o que falta para cada item ativo ter aprovação final. Gera PENDENCIA por item."""
        for k, f in self.F.items():
            if f["situacao"] != "ATIVA":
                continue
            m = []
            for d in ("LINGUISTICA", "TRADUCAO", "PEDAGOGICA"):
                self._exigir_final(k, d, m, "frase")
            if m:
                self.R.add("PENDENCIA", "SEM_APROVACAO_FINAL", f"frase {k}", "; ".join(m))
        for k, a in self.A.items():
            if a["situacao"] != "ATIVA":
                continue
            m = []
            self._exigir_final(k, "ROTEIRO", m, "faixa")
            if m:
                self.R.add("PENDENCIA", "SEM_APROVACAO_FINAL", f"faixa {k}", "; ".join(m))
        for arq in self.T["arquivos_audio.csv"]:
            if arq["situacao"] != "ATIVO":
                continue
            m = []
            self._exigir_final(arq["id_arquivo_audio"], "GRAVACAO", m, "gravação")
            if m:
                self.R.add("PENDENCIA", "SEM_APROVACAO_FINAL", f"gravação {arq['id_arquivo_audio']}", "; ".join(m))
        for k, x in self.X.items():
            if x["situacao"] != "ATIVA":
                continue
            m = []
            self._exigir_final(k, "PEDAGOGICA", m, "exercício")
            eas = self.EA.get(k, [])
            if eas:
                self._exigir_final(k, "ESCUTA", m, "exercício")
            for i in lista_ids(x["frases_usadas"]):
                if i in self.F:
                    for d in ("LINGUISTICA", "TRADUCAO", "PEDAGOGICA"):
                        self._exigir_final(i, d, m, "frase usada")
            for fx in sorted({e["id_audio"] for e in eas}):
                if fx in self.A:
                    self._exigir_final(fx, "ROTEIRO", m, "faixa usada")
            for r in self.R.resolucao.get(k, []):
                if r is None:
                    m.append("gravação não resolvida")
                    continue
                self._exigir_final(r, "GRAVACAO", m, "gravação usada")
                arq = self.ARQ[r]
                if arq["id_audio"] in self.A and arq["imp_roteiro_gerado"] != self.R.impressoes[("faixa", arq["id_audio"])]["imp_roteiro"]:
                    m.append(f"gravação usada {r}: desatualizada em relação ao roteiro")
            self.R.aprovacao_exercicio[k] = {"aprovado": not m, "bloqueios": m}
            if m:
                self.R.add("PENDENCIA", "EXERCICIO_NAO_APROVADO", f"exercício {k}",
                           f"{len(m)} bloqueio(s): " + "; ".join(m))


# ---------------------------------------------------------------------------
# Registro de apontamentos (03_revisao/apontamentos.csv) — regras do PROTOCOLO.md
# ---------------------------------------------------------------------------
CAB_APONTAMENTOS = ["id_apontamento", "origem", "rodada", "data", "commit_revisado", "area", "gravidade", "descricao",
                    "status", "commit_correcao", "evidencia", "verificado_por", "commit_verificado", "documento",
                    "observacoes"]
ENUM_AP = {
    "origem": {"IA_CHATGPT", "IA_CLAUDE", "HUMANO_RESPONSAVEL", "HUMANO_JAPONES", "HUMANO_OUTRO"},
    "area": {"LING", "TRAD", "PED", "AUD", "DADOS", "TEST", "DOC", "EDIT", "INFRA"},
    "gravidade": {"ALTA", "MEDIA", "BAIXA"},
    "status": {"ABERTO", "EM_CORRECAO", "CORRIGIDO_AGUARDA_VERIFICACAO", "VERIFICADO", "REJEITADO_COM_JUSTIFICATIVA",
               "SUPERADO", "DIVERGENCIA_AGUARDA_HUMANO"},
    "verificador": {"IA_CHATGPT", "HUMANO_RESPONSAVEL", "HUMANO_JAPONES", "HUMANO_OUTRO"},
}


def verificar_apontamentos(caminho: Path) -> Resultado:
    R = Resultado()
    nome = caminho.name
    if not caminho.exists():
        R.add("ERRO", "ARQUIVO_AUSENTE", nome, "registro de apontamentos não encontrado")
        return R
    try:
        cab, linhas = ler_simples(caminho)
    except UnicodeDecodeError:
        R.add("ERRO", "CODIFICACAO", nome, "não é UTF-8")
        return R
    if cab != CAB_APONTAMENTOS:
        R.add("ERRO", "CABECALHO", nome, f"cabeçalho esperado: {CAB_APONTAMENTOS}")
        return R
    vistos = set()
    for n, l in enumerate(linhas, start=2):
        loc = f"{nome}:{n} ({l['id_apontamento']})"
        if not RE["apontamento"].match(l["id_apontamento"]):
            R.add("ERRO", "FORMATO", loc, "`id_apontamento` deve ser C<cap>-<ÁREA>-<nnn>, P<nn> ou CL-<nn>")
        if l["id_apontamento"] in vistos:
            R.add("ERRO", "ID_DUPLICADO", loc, "ID de apontamento repetido; IDs nunca são reutilizados")
        vistos.add(l["id_apontamento"])
        for col, en in (("origem", "origem"), ("area", "area"), ("gravidade", "gravidade"), ("status", "status")):
            if l[col] not in ENUM_AP[en]:
                R.add("ERRO", "VALOR_INVALIDO", loc, f"`{col}`=`{l[col]}` não está em {sorted(ENUM_AP[en])}")
        if not data_valida(l["data"]):
            R.add("ERRO", "FORMATO", loc, "`data` deve ser ISO 8601 com fuso")
        if not RE["commit"].match(l["commit_revisado"]):
            R.add("ERRO", "FORMATO", loc, "`commit_revisado` deve ter 40 caracteres")
        if not l["descricao"].strip():
            R.add("ERRO", "CAMPO_VAZIO", loc, "`descricao` é obrigatória")
        st = l["status"]
        if st in ("CORRIGIDO_AGUARDA_VERIFICACAO", "VERIFICADO"):
            if not RE["commit"].match(l["commit_correcao"]):
                R.add("ERRO", "SEM_EVIDENCIA", loc, f"status {st} exige `commit_correcao` (40 caracteres)")
            if not l["evidencia"].strip():
                R.add("ERRO", "SEM_EVIDENCIA", loc, f"status {st} exige `evidencia` (arquivo, linha, teste ou saída)")
        if st == "VERIFICADO":
            if l["verificado_por"] not in ENUM_AP["verificador"]:
                R.add("ERRO", "VERIFICACAO_INVALIDA", loc,
                      "VERIFICADO exige `verificado_por` independente do executor (IA_CHATGPT ou HUMANO_*); "
                      "o Claude não verifica a própria correção")
            if not RE["commit"].match(l["commit_verificado"]):
                R.add("ERRO", "VERIFICACAO_INVALIDA", loc, "VERIFICADO exige `commit_verificado` (40 caracteres)")
        elif l["verificado_por"] or l["commit_verificado"]:
            R.add("ERRO", "VERIFICACAO_INVALIDA", loc, "`verificado_por`/`commit_verificado` só se preenchem com status VERIFICADO")
        if st in ("REJEITADO_COM_JUSTIFICATIVA", "SUPERADO", "DIVERGENCIA_AGUARDA_HUMANO") and not l["observacoes"].strip():
            R.add("ERRO", "SEM_JUSTIFICATIVA", loc, f"status {st} exige justificativa em `observacoes`")
    R.contagem_linhas[nome] = len(linhas)
    return R


# ---------------------------------------------------------------------------
# Escrita (atualizar-impressoes, fechar-roteiro)
# ---------------------------------------------------------------------------
def ler_simples(caminho: Path):
    with open(caminho, encoding="utf-8", newline="") as f:
        r = list(csv.reader(f))
    return r[0], [dict(zip(r[0], v)) for v in r[1:] if v and v != [""]]


def gravar_simples(caminho: Path, cab, linhas):
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cab)
        for l in linhas:
            w.writerow([l[c] for c in cab])


def atualizar_impressoes(pasta: Path):
    """Grava impressões correntes; sobe a versão da faceta quando a impressão gravada existia e mudou."""
    v = Verificador(pasta)
    R = v.executar()
    if not hasattr(v, "T"):
        return R, []
    I = R.impressoes
    mudancas = []
    regras = [("frases.csv", "frase", "id_frase", [("imp_japones", "versao_japones"), ("imp_traducao", "versao_traducao"),
                                                   ("imp_explicacao", "versao_explicacao")]),
              ("exercicios.csv", "exercicio", "id_exercicio", [("imp_exercicio", "versao")]),
              ("respostas.csv", "resposta", "id_resposta", [("imp_resposta", "versao")]),
              ("audios.csv", "faixa", "id_audio", [("imp_roteiro", "versao_roteiro")])]
    for tabela, tipo, chave, cols in regras:
        cab, linhas = ler_simples(pasta / tabela)
        alterou = False
        for l in linhas:
            calc = I.get((tipo, l[chave]))
            if not calc:
                continue
            for c_imp, c_ver in cols:
                if l[c_imp] != calc[c_imp]:
                    antiga = l[c_imp]
                    l[c_imp] = calc[c_imp]
                    if antiga and l[c_ver].isdigit():
                        l[c_ver] = str(int(l[c_ver]) + 1)
                    mudancas.append(f"{tabela} {l[chave]}: {c_imp} {'atualizada' if antiga else 'preenchida'}"
                                    + (f", {c_ver} → {l[c_ver]}" if antiga else ""))
                    alterou = True
        if alterou:
            gravar_simples(pasta / tabela, cab, linhas)
    return R, mudancas


def fechar_roteiro(pasta: Path, id_audio: str):
    v = Verificador(pasta)
    R = v.executar()
    cab, linhas = ler_simples(pasta / "audio_segmentos.csv")
    n = 0
    for l in linhas:
        if l["id_audio"] == id_audio and ("frase", l["id_frase"]) in R.impressoes:
            l["imp_japones_usada"] = R.impressoes[("frase", l["id_frase"])]["imp_japones"]
            n += 1
    gravar_simples(pasta / "audio_segmentos.csv", cab, linhas)
    return n


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------
def relatorio_texto(R: Resultado, pasta: Path) -> str:
    sev = defaultdict(list)
    for a in R.achados:
        sev[a.severidade].append(a)
    out = [f"Verificação de dados (esquema v{VERSAO_ESQUEMA}) — {pasta}",
           "Linhas lidas: " + ", ".join(f"{k}={v}" for k, v in sorted(R.contagem_linhas.items())),
           f"ERRO: {len(sev['ERRO'])} · PENDENCIA: {len(sev['PENDENCIA'])} · AVISO: {len(sev['AVISO'])}",
           f"Código de saída: {R.codigo_saida}", ""]
    for s in ("ERRO", "PENDENCIA", "AVISO"):
        if sev[s]:
            out.append(f"== {s} ==")
            for a in sev[s]:
                out.append(f"[{a.codigo}] {a.local}: {a.mensagem}")
            out.append("")
    if R.aprovacao_exercicio:
        out.append("== Situação dos exercícios ==")
        for k, v in sorted(R.aprovacao_exercicio.items()):
            out.append(f"{k}: {'APROVADO (final)' if v['aprovado'] else 'NÃO APROVADO'}")
    return "\n".join(out).rstrip() + "\n"


def main(argv=None):
    base = Path(__file__).resolve().parent.parent / "01_dados"
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    pv = sub.add_parser("verificar")
    pv.add_argument("--dados", type=Path, default=base)
    pv.add_argument("--raiz-audio", type=Path)
    pv.add_argument("--json", type=Path, help="grava também o resultado em JSON")
    pa = sub.add_parser("atualizar-impressoes")
    pa.add_argument("--dados", type=Path, default=base)
    pf = sub.add_parser("fechar-roteiro")
    pf.add_argument("id_audio")
    pf.add_argument("--dados", type=Path, default=base)
    pi = sub.add_parser("impressao-validacao")
    pi.add_argument("id_item")
    pi.add_argument("dimensao", choices=sorted(ENUM["dimensao"]))
    pi.add_argument("--dados", type=Path, default=base)
    pap = sub.add_parser("verificar-apontamentos")
    pap.add_argument("--arquivo", type=Path, default=base.parent / "03_revisao" / "apontamentos.csv")
    a = p.parse_args(argv)
    if a.cmd == "verificar-apontamentos":
        R = verificar_apontamentos(a.arquivo)
        print(relatorio_texto(R, a.arquivo), end="")
        return R.codigo_saida
    if not a.dados.is_dir():
        print(f"pasta de dados inexistente: {a.dados}", file=sys.stderr)
        return 3
    if a.cmd == "verificar":
        R = Verificador(a.dados, a.raiz_audio).executar()
        print(relatorio_texto(R, a.dados), end="")
        if a.json:
            a.json.write_text(json.dumps({
                "esquema": VERSAO_ESQUEMA, "codigo_saida": R.codigo_saida, "linhas": R.contagem_linhas,
                "achados": [x.como_dict() for x in R.achados],
                "exercicios": R.aprovacao_exercicio}, ensure_ascii=False, indent=2), encoding="utf-8")
        return R.codigo_saida
    if a.cmd == "atualizar-impressoes":
        R, mud = atualizar_impressoes(a.dados)
        print("\n".join(mud) if mud else "nenhuma impressão alterada")
        return 0
    if a.cmd == "fechar-roteiro":
        print(f"{fechar_roteiro(a.dados, a.id_audio)} segmento(s) de {a.id_audio} fechados")
        return 0
    if a.cmd == "impressao-validacao":
        v = Verificador(a.dados)
        v.executar()
        if not hasattr(v, "T"):
            print("dados com erro de estrutura; corrija antes", file=sys.stderr)
            return 1
        imp, res, motivo = v.impressao_dimensao(a.id_item, a.dimensao)
        if imp is None:
            print(f"não é possível calcular: {motivo}", file=sys.stderr)
            return 1
        print(f"imp_validada={imp}")
        print(f"arquivos_audio_resolvidos={'|'.join(r or '' for r in res)}")
        return 0
    return 3


if __name__ == "__main__":
    sys.exit(main())
