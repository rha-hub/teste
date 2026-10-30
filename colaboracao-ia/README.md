# Colaboração entre IAs · O Japonês por Trás das Palavras

Esta pasta é o canal de trabalho entre **Claude** (produção e organização), **ChatGPT** (revisão independente) e o **responsável humano** (decisão final). Tudo o que uma IA analisou, corrigiu ou deixou pendente fica registrado aqui, com data, versão e arquivos examinados.

> Esta pasta fica fora de `docs/` de propósito: se o GitHub Pages estiver publicando `docs/`, nada daqui é publicado como página.
>
> **Atenção:** este repositório é **público**. Tudo o que for colocado aqui pode ser lido por qualquer pessoa. Não suba senhas, tokens, chaves de API, dados pessoais nem material que ainda não pode ser divulgado.

## Estrutura

```
colaboracao-ia/
├── README.md                     ← este protocolo
├── 01_dados/                     ← registro de rastreabilidade (CSV, UTF-8)
│   ├── frases.csv
│   ├── exercicios.csv
│   └── audios.csv
├── 02_testes/
│   └── teste-html-smoke.js       ← teste Playwright para materiais HTML
├── 03_revisao/                   ← pedidos de revisão, relatórios e respostas
│   └── REVISAO_SOLICITADA.md
└── 04_historico/
    └── CHANGELOG.md              ← o que mudou, quando e por quê
```

## Papéis

| Quem | Faz | Não faz |
|---|---|---|
| Claude | Produz e organiza materiais, prepara roteiros, roda testes, pede revisão, responde aos apontamentos | Não autovalida naturalidade do japonês; não considera nada aprovado sem revisão externa |
| ChatGPT | Revisão independente: japonês, tradução, pedagogia, coerência, CSVs, testes | Não reescreve os materiais por conta própria; não aprova o produto final |
| Revisor nativo | Palavra final sobre naturalidade e registro | — |
| Responsável humano | Decide divergências e aprova cada versão | — |

A aprovação do ChatGPT é uma revisão técnica auxiliar, não uma garantia de correção linguística nem de sucesso comercial.

## Fluxo de uma rodada

**Fase A · Produção.** Claude prepara ou atualiza os materiais e os coloca no repositório. Arquivos originais não são sobrescritos: uma nova versão leva um sufixo (`_v2`) ou entra em nova pasta, e a mudança é registrada no `CHANGELOG.md`.

**Fase B · Pedido de revisão.** Claude cria `03_revisao/REVISAO_SOLICITADA.md` com: objetivo, arquivos a examinar (caminho e commit), contexto, mudanças desde a versão anterior, dúvidas que pedem decisão editorial e pontos que não devem ser alterados.

**Fase C · Revisão do ChatGPT.** O ChatGPT lê os arquivos indicados e produz `03_revisao/RELATORIO_CHATGPT.md`. Se ele não tiver acesso de escrita ao repositório, o relatório é entregue ao responsável humano, que o coloca no repositório **sem editar o conteúdo**, indicando no topo "inserido por <nome> em <data>".

A revisão avalia: gramática do japonês; naturalidade e adequação ao contexto; formal, casual e rude; tradução para o português do Brasil; qualidade pedagógica; coerência entre frases, exercícios e áudios; integridade e estrutura dos CSVs; funcionamento e cobertura dos testes; inconsistências entre documentos; pontos que exigem falante nativo.

**Fase D · Resposta do Claude.** Claude cria `03_revisao/RESPOSTA_CLAUDE.md`. Para cada apontamento: ID, decisão (aceitar, rejeitar ou investigar), justificativa, alteração feita, arquivo e local modificados, dúvidas abertas. Claude pode discordar, sempre explicando por quê, e nunca muda o sentido de um exemplo só para que ele pareça aprovado.

**Fase E · Nova revisão.** Depois das correções, Claude registra a nova versão e cria `03_revisao/NOVA_REVISAO_SOLICITADA.md`, listando apontamentos corrigidos e pendentes. O ChatGPT verifica cada correção e procura problemas novos.

**Fase F · Aprovação.** Uma versão só fica pronta para publicação quando os apontamentos relevantes estão resolvidos e o responsável humano aprova por escrito no `CHANGELOG.md`.

Ao fim de cada rodada, os arquivos de `03_revisao/` são movidos para `03_revisao/rodada-NN/` (NN = 01, 02…), para que a rodada seguinte comece limpa e o histórico fique completo.

## Formato dos apontamentos

Cada apontamento tem um ID estável no formato `C<capítulo>-<ÁREA>-<nnn>`:

| Área | Uso | Exemplo |
|---|---|---|
| `LING` | gramática, naturalidade, registro, furigana | `C04-LING-001` |
| `TRAD` | tradução para o português | `C04-TRAD-001` |
| `PED` | pedagogia, exercícios, gabarito | `C04-PED-001` |
| `AUD` | roteiro e arquivos de áudio | `C04-AUD-001` |
| `DADOS` | estrutura e integridade dos CSVs | `C00-DADOS-001` |
| `TEST` | testes automatizados | `C00-TEST-001` |
| `DOC` | inconsistência entre documentos | `C04-DOC-001` |
| `EDIT` | diagramação e visual | `C04-EDIT-001` |

`C00` é usado para o que não pertence a um capítulo (infraestrutura, dados, testes).

Cada apontamento traz: **ID · descrição · justificativa · gravidade (alta, média, baixa) · sugestão de correção · status**.

Status possíveis:

- **APROVADO**: nenhum problema identificado nesta revisão.
- **AJUSTAR**: correção recomendada.
- **NÃO USAR**: problema importante que impede o uso na versão atual.
- **PENDENTE DE VALIDAÇÃO**: não dá para confirmar com segurança sem uma fonte ou um falante nativo.

Uma frase não é dada como validada só porque parece plausível.

## Regras de rastreabilidade

1. Um ID de apontamento nunca é reutilizado, nem depois de resolvido.
2. Um apontamento só é marcado como resolvido depois que a alteração correspondente é conferida no arquivo, com o commit indicado.
3. Toda rodada registra: data, versão (commit) e lista exata de arquivos examinados.
4. Mudanças importantes entram em `04_historico/CHANGELOG.md`.
5. Arquivos originais são preservados sempre que possível; correções geram uma nova versão.
6. Quando uma frase muda, quem muda lista o que depende dela: exercícios (`exercicios.csv` → `frases_usadas`), áudios (`audios.csv` → `frases`) e páginas diagramadas.
7. Resultados de testes só são registrados se o teste foi de fato executado; o registro diz quando, sobre qual arquivo e com qual saída.

## IDs dos materiais

| Tipo | Formato | Exemplo |
|---|---|---|
| Frase ou exemplo | `J<cap>-<nº>` | `J04-14` |
| Faixa de áudio | `A<cap>-<nº>` | `A04-03` |
| Exercício | `X<cap>-<rótulo>` | `X04-R1` |
| Cartão de revisão | `C<cap>-<nº>` | `C04-07` |

IDs de materiais também nunca são reutilizados. Uma frase removida fica no CSV com status `RETIRADA`.

## Marcas de integridade (impressões)

As colunas `impressao_texto` (em `frases.csv`) e `impressao_roteiro` (em `audios.csv`) servem para descobrir material desatualizado.

**Como é calculada (definição proposta):**

1. Juntar, nesta ordem e separados por uma quebra de linha (`\n`), os campos `forma_completa`, `forma_reduzida` e `furigana` da frase.
2. Normalizar o texto em Unicode NFC e codificar em UTF-8.
3. Calcular SHA-256 e guardar os 12 primeiros caracteres hexadecimais.

**Como é usada:** quando um áudio é gerado, a impressão de cada frase falada é copiada para `impressao_roteiro` (lista na mesma ordem de `frases`). Se depois a impressão atual da frase for diferente da guardada, o áudio está desatualizado.

**Estado atual:** os CSVs ainda só têm cabeçalhos, e o script que calcula e compara as impressões **ainda não existe**. Nenhuma impressão foi calculada até agora.

## Testes

`02_testes/teste-html-smoke.js` abre um arquivo HTML no Chromium (Playwright) em 1280 px e 390 px e verifica erros de carregamento, rolagem lateral, nomes acessíveis, imagens sem texto alternativo, links internos e reação dos botões ao clique. Ele não altera o arquivo testado. Grava `report.json` e capturas de tela na pasta de onde é executado.

```
npm install playwright
npx playwright install chromium
node teste-html-smoke.js caminho/do/arquivo.html
```

Limitação conhecida: o script não sabe as respostas certas dos exercícios, então não testa se o feedback de acerto e erro está correto. Isso exige uma versão guiada por `exercicios.csv`.

## Limites deste primeiro teste

Nenhum conteúdo de capítulo foi alterado, nenhum áudio novo foi gerado e nada foi publicado como produto.
