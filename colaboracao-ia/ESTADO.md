# Estado do projeto — livro PDF

Atualizado em 2026-10-30.

## Escopo oficial

O Volume 1 será um livro estático em PDF. Não terá áudio, QR codes, vídeo, links para atividade externa, aplicativo, site, plataforma ou interação fora do próprio PDF.

## Verificações reproduzidas nesta rodada

- Testes Python: 7 de 7 passaram localmente após corrigir o caminho de importação e a escrita de LF no teste. A correção foi registrada nesta branch.
- Verificador editorial: passou sobre os quatro CSVs oficiais, que seguem vazios. Isso comprova apenas estrutura vazia válida; não há dados editoriais preenchidos para validar.
- Comparador de originais: não executável no pacote ZIP, pois requer histórico Git e o ambiente não tem Git instalado.
- Smoke test HTML: não executável; Playwright não está instalado.
- PDF existente: 8 páginas inspecionadas visualmente. É uma prova de páginas do Capítulo 4 composta por duas alternativas de diagramação. Inclui conteúdo e instruções de áudio/QR e notas técnicas de edição; não é o livro final PDF-only.

## Lacunas que impedem concluir o livro

- Não há manuscrito completo. Os CSVs estão vazios; os HTMLs são protótipos e o PDF é apenas uma amostra de páginas do Capítulo 4.
- Faltam estrutura completa do Volume 1, exemplos editados, traduções PT-BR, exercícios e gabarito do livro todo.
- A amostra visual tem conteúdo provisório e referências incompatíveis com o escopo PDF-only.
- Não foi possível executar os verificadores HTML e de comparação de originais neste ambiente.
- Não existe revisão humana independente de japonês e pedagogia.

## Situação

A infraestrutura teve uma correção de teste verificada. O livro e o PDF final ainda não estão prontos. Não aprovar, publicar ou fazer merge com base neste estado.
