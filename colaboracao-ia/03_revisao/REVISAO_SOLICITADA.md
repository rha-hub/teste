> **HISTÓRICO — SUPERADO.** Este documento registra uma rodada anterior e pode conter requisitos de áudio ou arquitetura que não se aplicam mais. A decisão vigente é exclusivamente um livro estático em PDF. Preservado como evidência; não usar como instrução atual.

# Revisão solicitada · Rodada 01

- **Data do pedido:** 2026-10-30
- **Pedido por:** Claude
- **Revisor:** ChatGPT
- **Versão:** o commit que adicionou esta pasta (ver histórico do repositório)

## Objetivo

Revisar a **infraestrutura** de colaboração antes de qualquer conteúdo de capítulo passar por ela: o protocolo, a estrutura dos três CSVs de rastreabilidade e o teste automatizado de HTML. Esta rodada **não** revisa o japonês do Capítulo 4.

## Arquivos a examinar

| Arquivo | O que é |
|---|---|
| `colaboracao-ia/README.md` | Protocolo de trabalho, formato dos apontamentos, regras de rastreabilidade, definição das impressões |
| `colaboracao-ia/01_dados/frases.csv` | Cabeçalho do registro de frases (sem linhas ainda) |
| `colaboracao-ia/01_dados/exercicios.csv` | Cabeçalho do registro de exercícios (sem linhas ainda) |
| `colaboracao-ia/01_dados/audios.csv` | Cabeçalho do registro de áudios (sem linhas ainda) |
| `colaboracao-ia/02_testes/teste-html-smoke.js` | Teste Playwright para materiais HTML |

## Contexto

- Produto: material digital em PDF para brasileiros autodidatas entre N5 e N4, focado em reduções da fala, registro e escuta. Volume 1 = capítulos 0 a 5; o Capítulo 4 é o piloto.
- Os três CSVs ficam separados porque uma faixa de áudio cobre várias frases e um exercício usa várias frases; numa tabela única, o mesmo áudio se repetiria em várias linhas.
- As colunas `impressao_texto` e `impressao_roteiro` existem para detectar áudio e exercícios desatualizados quando uma frase muda. A definição do cálculo está no README; **o script que calcula ainda não existe**.
- Existem no repositório, fora desta pasta, quatro arquivos anteriores: `O Japonês que Encolhe.html`, `paginas-modelo.html`, `docs/index.html` e o PDF das páginas-modelo em `docs/`. Eles não fazem parte desta revisão e não foram alterados.

## Mudanças desde a versão anterior

É a primeira versão desta pasta. Nada existia antes dela.

## Resultado de teste já executado

O teste `teste-html-smoke.js` foi executado **uma vez**, em 2026-10-30, pelo Claude, sobre uma **cópia local** do demo do Capítulo 4 (não sobre o arquivo `O Japonês que Encolhe.html` deste repositório, que tem conteúdo diferente da cópia testada). Resultados:

- Sem rolagem horizontal em 1280 px e 390 px.
- 60 botões, todos com nome acessível; nenhuma imagem sem texto alternativo; nenhum campo sem rótulo.
- Nenhum trecho com `lang="ja"`; a cópia local também não declarava idioma da página.
- Os 5 arquivos MP3 referenciados não existiam na cópia local; os botões de ouvir ficaram inativos.
- 29 dos 37 botões clicados alteraram a página; 3 botões de velocidade não tiveram efeito visível (inconclusivo) e 5 de áudio estavam inativos.
- As opções dos exercícios estavam ocultas no momento do teste; os exercícios **não** foram testados.
- A fonte do Google Fonts não carregou por bloqueio de rede do ambiente de teste, não por erro da página.

O teste ainda **não** foi executado sobre os arquivos HTML deste repositório.

## Perguntas para o revisor

1. A estrutura dos três CSVs cobre o que é preciso para ligar frase, exercício, gabarito e áudio? Falta alguma coluna? Alguma sobra?
2. A definição da impressão (SHA-256 de `forma_completa`, `forma_reduzida` e `furigana`, normalizados em NFC) é suficiente? A tradução deveria entrar no cálculo?
3. O formato de ID dos apontamentos (`C04-LING-001`) e as áreas propostas atendem às revisões linguística e pedagógica?
4. O que o teste de HTML deixa de cobrir que deveria cobrir primeiro?
5. O protocolo tem alguma brecha que permita marcar como resolvido algo que não foi verificado?

## Dúvidas que pedem decisão editorial (do responsável humano)

1. Registro em CSV no GitHub, com cópia de leitura no Google Sheets no futuro, ou planilha no Sheets como fonte?
2. Velocidades de áudio: hoje há três especificações diferentes (demo: 1×, 0,85×, 0,7×; roteiro do Cap. 4 v2: normal e 0,8×; páginas-modelo: "3 velocidades"). Qual vale?
3. O repositório é público. Os capítulos e os áudios devem ficar nele ou num repositório privado?

## Observação sobre arquivo existente (não alterado)

`docs/index.html` aponta o `iframe` para `../Páginas-modelo · Cap. 4 · A tinta e carimbo  B educacional limpo.pdf` (na raiz, sem "(1)"), mas o PDF está em `docs/` com "(1)" no nome. Pela leitura do código, o PDF não deve aparecer nessa página. Não corrigi porque não houve autorização para alterar arquivos existentes.

## Pontos que não devem ser alterados nesta rodada

- Os quatro arquivos que já estavam no repositório.
- O conteúdo do Capítulo 4.
- A decisão de não gerar áudios finais antes da aprovação dos roteiros.

## Como entregar o relatório

Criar `colaboracao-ia/03_revisao/RELATORIO_CHATGPT.md` com: data, commit examinado, lista dos arquivos lidos e uma tabela de apontamentos (ID, descrição, justificativa, gravidade, sugestão, status). Se o ChatGPT não puder escrever no repositório, o responsável humano insere o arquivo sem editar o conteúdo.
