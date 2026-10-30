# O Japonês por Trás das Palavras — produção do livro PDF

Este repositório organiza a produção editorial de um único produto: um **livro digital estático em PDF** para estudantes brasileiros de japonês.

## Escopo fechado

Incluído: conteúdo japonês, furigana, traduções, explicações, exemplos contextualizados, exercícios impressos, gabarito comentado, revisão linguística/pedagógica/editorial, diagramação e exportação/inspeção do PDF.

Excluído: áudio, narração, QR codes, vídeos, atividades digitais, links externos para exercícios, aplicativo, site, plataforma, assinatura, comunidade ou qualquer experiência interativa fora do PDF.

## Estrutura

- `01_dados/`: CSVs editoriais de frases, exercícios, respostas e validações.
- `02_testes/`: testes automatizados do verificador.
- `03_revisao/`: apontamentos e relatórios.
- `04_historico/`: decisões e changelog.
- `05_ferramentas/`: verificador de integridade editorial.
- `ESTADO.md`: estado real da implementação.

## Verificação

```sh
python3 -m unittest discover -s colaboracao-ia/02_testes -p 'test_*.py'
python3 colaboracao-ia/05_ferramentas/verificar_dados.py
``

O verificador não substitui revisão linguística, pedagógica ou visual. Antes de publicar, revisar o PDF exportado em tela e impressão, página a página.

## Materiais históricos no repositório\n\nOs arquivos originais `O Japonês que Encolhe.html`, `paginas-modelo.html`, `docs/index.html` e o PDF do Capítulo 4 foram preservados sem alteração como evidência histórica. Alguns contêm referências antigas a áudio/QR e não são especificações nem entregáveis aprovados do produto PDF-only.\n\n## Estado verificado em 2026-10-30

A suíte automatizada passou (7/7) após uma correção nos testes. O verificador estrutural também passou, mas os quatro CSVs oficiais permanecem vazios. Isso não valida conteúdo editorial.

O PDF disponível no repositório é uma prova de 8 páginas do Capítulo 4, com duas alternativas de layout e referências provisórias a áudio/QR. Não é o livro final. Consulte `ESTADO.md` e `03_revisao/RELATORIO_EXECUCAO.md` para resultados e limitações. O merge e a publicação seguem pendentes.
