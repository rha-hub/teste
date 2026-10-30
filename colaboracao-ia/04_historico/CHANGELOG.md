# Histórico de mudanças · colaboracao-ia

Formato: data · versão (commit) · autor · o que mudou · por quê. Entradas mais recentes primeiro. Commits sempre com SHA completo; o SHA de um commit é registrado na entrada seguinte, porque um arquivo não pode conter o SHA do commit que o cria.

## 2026-10-30 · correções da rodada 01 · Claude (com autorização do responsável humano)

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
