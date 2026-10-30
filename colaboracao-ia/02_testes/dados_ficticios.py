"""Gerador do conjunto de dados FICTÍCIO usado nos testes do verificador.

Tudo aqui é fictício e serve só para exercitar o verificador: capítulo 99, frases de
teste sem valor didático, "áudios" que são pequenos arquivos de texto. Nada disto é
conteúdo do livro e nada disto vai para os CSVs oficiais de `01_dados/`.

`gerar_aprovado(pasta)` cria um estado completo em que todos os itens têm validação humana
final vigente. O verificador deve devolver código 0 para esse estado. Os testes partem dele
e mudam uma coisa de cada vez.
"""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "05_ferramentas"))
import verificar_dados as vd  # noqa: E402

COMMIT_FICTICIO = "0" * 39 + "1"
DATA = "2026-10-30T12:00:00-03:00"
OBS = "FICTICIO: dado de teste"


def _gravar(pasta: Path, nome: str, linhas: list[dict]):
    cab = vd.CABECALHOS[nome]
    with open(pasta / nome, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cab)
        for l in linhas:
            w.writerow([l.get(c, "") for c in cab])


def _arquivo_audio(raiz: Path, nome: str, conteudo: str) -> str:
    (raiz / "audio").mkdir(parents=True, exist_ok=True)
    p = raiz / "audio" / nome
    p.write_bytes(conteudo.encode("utf-8"))
    return hashlib.sha256(p.read_bytes()).hexdigest()


def gerar_base(pasta: Path) -> Path:
    """Dados estruturalmente válidos, ainda sem impressões, roteiro fechado ou validações."""
    pasta = Path(pasta)
    dados = pasta / "dados"
    dados.mkdir(parents=True, exist_ok=True)
    _gravar(dados, "frases.csv", [
        dict(id_frase="J99-01", capitulo="99", licao="99.1", forma_completa="{試験|しけん}の{文|ぶん}を{読|よ}んでしまった",
             forma_reduzida="{試験|しけん}の{文|ぶん}を{読|よ}んじゃった", reducao="でしまう→じゃう", registro="CASUAL",
             traducao_ptbr="[fictício] li a frase de teste", explicacao_curta="[fictício] explicação de teste",
             versao_japones="1", versao_traducao="1", versao_explicacao="1", situacao="ATIVA", observacoes=OBS),
        dict(id_frase="J99-02", capitulo="99", licao="99.1", forma_completa="{試験|しけん}です", forma_reduzida="",
             reducao="", registro="NEUTRO_POLIDO", traducao_ptbr="[fictício] é um teste",
             explicacao_curta="[fictício] sem redução", versao_japones="1", versao_traducao="1", versao_explicacao="1",
             situacao="ATIVA", observacoes=OBS),
    ])
    _gravar(dados, "exercicios.csv", [
        dict(id_exercicio="X99-E1", capitulo="99", licao="99.1", degrau="RECONHECER", tipo="ESCUTA",
             enunciado="[fictício] ouça e marque", frases_usadas="J99-01", secao_que_ensina="99.1",
             regra_comparacao="MANUAL", versao="1", situacao="ATIVA", observacoes=OBS),
        dict(id_exercicio="X99-E2", capitulo="99", licao="99.1", degrau="RECONHECER", tipo="ESCUTA",
             enunciado="[fictício] ouça a tomada comentada", frases_usadas="J99-02", secao_que_ensina="99.1",
             regra_comparacao="MANUAL", versao="1", situacao="ATIVA", observacoes=OBS),
        dict(id_exercicio="X99-M1", capitulo="99", licao="99.1", degrau="ESCREVER", tipo="MULTIPLA_ESCOLHA",
             enunciado="[fictício] escolha a forma", frases_usadas="J99-01|J99-02", secao_que_ensina="99.1",
             regra_comparacao="EXATA", versao="1", situacao="ATIVA", observacoes=OBS),
    ])
    _gravar(dados, "respostas.csv", [
        dict(id_resposta="X99-E1-a", id_exercicio="X99-E1", rotulo="a", texto="[fictício] じゃう", tipo="CORRETA",
             explicacao="[fictício]", versao="1", situacao="ATIVA"),
        dict(id_resposta="X99-E1-b", id_exercicio="X99-E1", rotulo="b", texto="[fictício] ちゃう", tipo="ERRADA",
             explicacao="[fictício]", versao="1", situacao="ATIVA"),
        dict(id_resposta="X99-E2-a", id_exercicio="X99-E2", rotulo="a", texto="[fictício] です", tipo="CORRETA",
             explicacao="[fictício]", versao="1", situacao="ATIVA"),
        dict(id_resposta="X99-M1-a", id_exercicio="X99-M1", rotulo="", texto="読んじゃった", tipo="CORRETA",
             explicacao="[fictício]", versao="1", situacao="ATIVA"),
        dict(id_resposta="X99-M1-b", id_exercicio="X99-M1", rotulo="", texto="読んでしまった", tipo="ACEITA",
             explicacao="[fictício] forma completa também aceita", versao="1", situacao="ATIVA"),
    ])
    _gravar(dados, "audios.csv", [
        dict(id_audio="A99-01", capitulo="99", descricao="[fictício] faixa de teste", versao_roteiro="1",
             qr_pagina="", situacao="ATIVA", observacoes=OBS),
    ])
    _gravar(dados, "audio_segmentos.csv", [
        dict(id_audio="A99-01", ordem="1", id_frase="J99-01", forma_falada="REDUZIDA", personagem="Pessoa A",
             voz="voz-ficticia-1", pausa_depois_ms="600"),
        dict(id_audio="A99-01", ordem="2", id_frase="J99-02", forma_falada="COMPLETA", personagem="Pessoa B",
             voz="voz-ficticia-2", pausa_depois_ms="0"),
    ])
    _gravar(dados, "exercicio_audios.csv", [
        dict(id_exercicio="X99-E1", ordem="1", id_audio="A99-01", velocidade="100", modo_selecao="ATIVO",
             id_arquivo_audio="", uso="ESTIMULO"),
        dict(id_exercicio="X99-E2", ordem="1", id_audio="A99-01", velocidade="080", modo_selecao="FIXO",
             id_arquivo_audio="A99-01_v080_r1_t1", uso="ESTIMULO"),
    ])
    _gravar(dados, "arquivos_audio.csv", [])
    _gravar(dados, "validacoes.csv", [])
    return dados


def nova_gravacao(raiz: Path, dados: Path, id_audio: str, velocidade: str, tomada: str, situacao="ATIVO",
                  conteudo: str | None = None) -> dict:
    """Linha de arquivos_audio para uma gravação feita a partir do roteiro ATUAL da faixa."""
    v = vd.Verificador(dados)
    R = v.executar()
    faixa = v.A[id_audio]
    ver = faixa["versao_roteiro"]
    ida = f"{id_audio}_v{velocidade}_r{ver}_t{tomada}"
    sha = _arquivo_audio(raiz, f"{ida}.ficticio", conteudo or f"FICTICIO {ida}")
    return dict(id_arquivo_audio=ida, id_audio=id_audio, velocidade=velocidade, versao_roteiro=ver, tomada=tomada,
                imp_roteiro_gerado=R.impressoes[("faixa", id_audio)]["imp_roteiro"], arquivo=f"{ida}.ficticio",
                sha256_arquivo=sha, gerado_em=DATA, servico_modelo_voz="servico-ficticio", plano_licenca="ficticio",
                transcricao_confere="SIM", situacao=situacao, observacoes=OBS)


def ler(dados: Path, nome: str):
    return vd.ler_simples(Path(dados) / nome)[1]


def gravar(dados: Path, nome: str, linhas):
    _gravar(Path(dados), nome, linhas)


def validar_tudo(dados: Path, revisor="HUMANO_JAPONES", ident="Revisora Fictícia", status="APROVADO", so=None):
    """Acrescenta (sem apagar as anteriores) uma validação para cada item/dimensão exigido,
    com a impressão ATUAL. `so` restringe a uma lista de (item, dimensao)."""
    v = vd.Verificador(dados)
    v.executar()
    alvos = []
    for k in v.F:
        alvos += [(k, d) for d in ("LINGUISTICA", "TRADUCAO", "PEDAGOGICA")]
    alvos += [(k, "ROTEIRO") for k in v.A]
    alvos += [(a["id_arquivo_audio"], "GRAVACAO") for a in v.T["arquivos_audio.csv"] if a["situacao"] == "ATIVO"]
    for k in v.X:
        alvos.append((k, "PEDAGOGICA"))
        if v.EA.get(k):
            alvos.append((k, "ESCUTA"))
    # gravações FIXO ainda usadas por exercícios também precisam de GRAVACAO
    for res in v.R.resolucao.values():
        for r in res:
            if r and (r, "GRAVACAO") not in alvos:
                alvos.append((r, "GRAVACAO"))
    if so is not None:
        alvos = [a for a in alvos if a in so]
    linhas = ler(dados, "validacoes.csv")
    n = max([int(l["id_validacao"][2:]) for l in linhas] + [0])
    for item, dim in alvos:
        imp, res, motivo = v.impressao_dimensao(item, dim)
        assert imp is not None, (item, dim, motivo)
        n += 1
        linhas.append(dict(id_validacao=f"V-{n:04d}", data=DATA, id_item=item, dimensao=dim, imp_validada=imp,
                           arquivos_audio_resolvidos="|".join(r or "" for r in res), status=status, revisor=revisor,
                           revisor_identificacao=ident if revisor.startswith("HUMANO_") else "",
                           commit_revisado=COMMIT_FICTICIO, apontamento="", observacoes=OBS))
    gravar(dados, "validacoes.csv", linhas)
    return len(alvos)


def gerar_aprovado(pasta: Path) -> tuple[Path, Path]:
    """Estado completo e aprovado. Devolve (pasta_dados, raiz_audio)."""
    raiz = Path(pasta)
    dados = gerar_base(raiz)
    vd.atualizar_impressoes(dados)
    vd.fechar_roteiro(dados, "A99-01")
    gravar(dados, "arquivos_audio.csv", [
        nova_gravacao(raiz, dados, "A99-01", "100", "1"),
        nova_gravacao(raiz, dados, "A99-01", "080", "1"),
    ])
    validar_tudo(dados)
    return dados, raiz / "audio"
