# Histórico de mudanças · colaboracao-ia

Formato: data · versão (commit) · autor · o que mudou · por quê. Entradas mais recentes primeiro. Commits sempre com SHA completo; o SHA de um commit é registrado na entrada seguinte, porque um arquivo não pode conter o SHA do commit que o cria.

## Sequência de commits do PR #1 (branch `colaboracao-ia/infraestrutura`)

| Ordem | Commit (SHA completo) | O que contém | Papel na revisão |
|---|---|---|---|
| 0 | `ae55c1ae9afcaa2f438ef6639d63f565500d3fae` | base: os quatro arquivos originais (`main`, do responsável humano) | base de comparação; não alterado |
| 1 | `e822d76fb83aced40c840e5915780ef412c0cd35` | primeira versão da pasta `colaboracao-ia/` (7 arquivos) | examinado na **1ª revisão** do ChatGPT (presumido: era o único commit da branch) |
| 2 | `b94d020516d1fb0e43620225622fb592ee133dcf` | correções dos pontos P01–P06 e CL-01 | material examinado na **2ª revisão** |
| 3 | `cd08f0da92f994157fb1a55f2fb9080924dd427f` | só acrescenta `03_revisao/NOVA_REVISAO_SOLICITADA.md`, que cita o commit 2 | head da branch durante a 2ª revisão (presumido); não altera material |
| 4 | `81c3479233768db7a5760d70790ca1f7096c071d` | correções dos pontos P07–P12 | material examinado na **3ª revisão** (P07, P09–P12 aprovados; P08 com ajuste pedido) |
| 5 | `31cccb55fae8d17e0ef902826c13c4d3c08ad1bb` | só acrescenta `03_revisao/NOVA_REVISAO_SOLICITADA_2.md`, que cita o commit 4 | head da branch durante a 3ª revisão (presumido); não altera material |
| 6 | registrado em `03_revisao/NOVA_REVISAO_SOLICITADA_3.md` | correções dos pontos P13–P15 (fecha o ajuste de P08) | material a examinar na **4ª revisão** |
| 7 | registrado no comentário do PR #1 | só acrescenta `03_revisao/NOVA_REVISAO_SOLICITADA_3.md` | não altera material |

Os SHAs históricos acima não mudam: nenhum commit foi reescrito (sem rebase, sem force push).

## 2026-10-30 · correções da 3ª revisão (P13–P15) · Claude (com autorização do responsável humano)

Commit anterior: `31cccb55fae8d17e0ef902826c13c4d3c08ad1bb`. Resposta em `03_revisao/RESPOSTA_CLAUDE_3.md`.

**Criado**
- `01_dados/exercicio_audios.csv`: qual faixa, em qual velocidade e com qual modo de seleção (`ATIVO` ou `FIXO`) cada exercício usa (só cabeçalho).
- `03_revisao/RESPOSTA_CLAUDE_3.md`.

**Alterado**
- `01_dados/ESQUEMA.md`: esquema v4. Inclui a seleção de áudio por exercício; as dimensões `ROTEIRO`, `GRAVACAO` (antes `AUDIO`) e `ESCUTA`; `imp_selecao_audio`; a seção 5.5 (substituição de gravação ativa); as regras 6 a 11 (identificador completo com tomada, unicidade, modos de seleção); e a importação de CSV em planilhas.
- `01_dados/exercicios.csv`: sem a coluna `audios` (substituída por `exercicio_audios.csv`).
- `01_dados/validacoes.csv`: nova coluna `arquivos_audio_resolvidos`.
- `README.md`: `exercicio_audios.csv` na estrutura.
- `04_historico/CHANGELOG.md`: sequência de commits (linhas 4 e 5 com SHA; 6 e 7 previstas).

**Preservado sem alteração:** os quatro arquivos originais; todos os documentos de revisão anteriores em `03_revisao/`; `02_testes/` (P09 e P10 aprovados).

**Aprovação humana:** pendente.

## 2026-10-30 · correções da 2ª revisão (P07–P12) · Claude (com autorização do responsável humano)

Commit anterior: `cd08f0da92f994157fb1a55f2fb9080924dd427f`. Resposta em `03_revisao/RESPOSTA_CLAUDE_2.md`.

**Criado**
- `01_dados/arquivos_audio.csv`: gravações produzidas, separadas da faixa lógica (só cabeçalho).
- `03_revisao/RESPOSTA_CLAUDE_2.md`.
- `03_revisao/teste-html_20261030-023635_O-Japones-que-Encolhe.json` e `03_revisao/teste-html_20261030-023652_docs-index.json`: relatórios citados das execuções v3.

**Alterado**
- `01_dados/ESQUEMA.md`: esquema v3 (faixa lógica × arquivo; dependências por dimensão; exemplos).
- `01_dados/audios.csv`: agora só faixa lógica.
- `01_dados/exercicios.csv`: sem `imp_dependencias`.
- `01_dados/validacoes.csv`: `faceta` → `dimensao`.
- `02_testes/teste-html-smoke.js`: v3 (caminho relativo à raiz do git; reação observável × funcionamento; desabilitado desde o carregamento × após interações).
- `02_testes/COBERTURA.md`: texto sobre reação observável; execuções v3.
- `README.md`: `arquivos_audio.csv` na estrutura; sufixos `_2`, `_3` dentro de uma rodada.
- `04_historico/CHANGELOG.md`: sequência de commits.

**Preservado sem alteração:** os quatro arquivos originais; `03_revisao/REVISAO_SOLICITADA.md`, `RESPOSTA_CLAUDE.md` e `NOVA_REVISAO_SOLICITADA.md`, como registro das etapas anteriores.

**Aprovação humana:** pendente.

## 2026-10-30 · correções da rodada 01 · Claude (com autorização do responsável humano)

Commit desta entrada: `b94d020516d1fb0e43620225622fb592ee133dcf`.

Resposta aos 6 pontos da auditoria do ChatGPT (ver `03_revisao/RESPOSTA_CLAUDE.md`). Commit anterior: `e822d76fb83aced40c840e5915780ef412c0cd35`.

**Criado**
- `01_dados/ESQUEMA.md`: esquema v2, com relacionamentos, listas de IDs, respostas alternativas, facetas de alteração e proposta de impressões (não implementada).
- `01_dados/respostas.csv`, `audio_segmentos.csv`, `validacoes.csv`: só cabeçalhos.
- `02_testes/COBERTURA.md`: o que o teste cobre e o que não cobre; execuções registradas.
- `.gitignore`: exclui `02_testes/resultados/`.
- `03_revisao/RESPOSTA_CLAUDE.md` e `03_revisao/teste-html_20261030-022739_O-Japones-que-Encolhe.json`.

**Alterado**
- `01_dados/frases.csv`, `exercicios.csv`, `audios.csv`: cabeçalhos do esquema v2 (antes: v1).
- `02_testes/teste-html-smoke.js`: versão 2 (`pathToFileURL`, sinais de interação, pastas de resultado sem sobrescrita, SHA do arquivo testado).
- `README.md`: estrutura, cabeçalho de versão com SHA completo, IDs (cartões `K`), referências a `ESQUEMA.md` e `COBERTURA.md`.

**Preservado sem alteração:** os quatro arquivos originais do projeto e `03_revisao/REVISAO_SOLICITADA.md`.

**Aprovação humana:** pendente.

## 2026-10-30 · primeira versão · Claude (preparado e enviado em pull request, com autorização do responsável humano)

Commit desta entrada: `e822d76fb83aced40c840e5915780ef412c0cd35` (acrescentado depois; o texto original da entrada não mudou).

**Criado**
- `colaboracao-ia/README.md`: protocolo de colaboração entre Claude e ChatGPT, formato dos apontamentos, regras de rastreabilidade e definição das impressões.
- `colaboracao-ia/01_dados/frases.csv`, `exercicios.csv`, `audios.csv`: só os cabeçalhos; nenhuma linha de dados.
- `colaboracao-ia/02_testes/teste-html-smoke.js`: teste Playwright de materiais HTML.
- `colaboracao-ia/03_revisao/REVISAO_SOLICITADA.md`: pedido da rodada 01 (revisão da infraestrutura).
- `colaboracao-ia/04_historico/CHANGELOG.md`: este arquivo.

**Preservado sem alteração**
- `O Japonês que Encolhe.html`
- `paginas-modelo.html`
- `docs/index.html`
- `docs/Páginas-modelo · Cap. 4 · A tinta e carimbo  B educacional limpo (1).pdf`

**Não feito nesta versão**
- Nenhum conteúdo de capítulo alterado, nenhum áudio gerado, nada publicado como produto.
- O script que calcula as impressões ainda não existe.

**Aprovação humana:** pendente.
