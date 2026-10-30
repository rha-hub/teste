# Colaboração entre IAs · O Japonês por Trás das Palavras

Esta pasta é o canal de trabalho entre **Claude** (produção e organização), **ChatGPT** (revisão independente) e o **responsável humano** (decisão final). Tudo o que uma IA analisou, corrigiu ou deixou pendente fica registrado aqui, com data, versão e arquivos examinados.

> Esta pasta fica fora de `docs/` de propósito: se o GitHub Pages estiver publicando `docs/`, nada daqui é publicado como página.
>
> **Atenção:** este repositório é **público**. Tudo o que for colocado aqui pode ser lido por qualquer pessoa. Não suba senhas, tokens, chaves de API, dados pessoais nem material que ainda não pode ser divulgado.

## Estrutura

```
colaboracao-ia/
├── README.md                     ← este protocolo
├── .gitignore                    ← impede versionar resultados locais de teste
├── 01_dados/                     ← registro de rastreabilidade (CSV, UTF-8)
│   ├── ESQUEMA.md                ← colunas, relacionamentos, impressões
│   ├── frases.csv
│   ├── exercicios.csv
│   ├── respostas.csv
│   ├── audios.csv                ← faixas lógicas de áudio
│   ├── audio_segmentos.csv       ← roteiro de cada faixa lógica
│   ├── arquivos_audio.csv        ← gravações produzidas (velocidade, versão, tomada)
│   ├── exercicio_audios.csv      ← qual áudio cada exercício usa (gravação fixa ou ativa)
│   └── validacoes.csv
├── 02_testes/
│   ├── teste-html-smoke.js       ← teste Playwright para materiais HTML
│   └── COBERTURA.md              ← o que o teste cobre e o que não cobre
├── 03_revisao/                   ← pedidos de revisão, relatórios e respostas
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

Dentro de uma rodada, as fases D e E podem se repetir. Cada repetição ganha um sufixo numérico (`RESPOSTA_CLAUDE_2.md`, `NOVA_REVISAO_SOLICITADA_2.md`, `RELATORIO_CHATGPT_2.md`…), e os arquivos anteriores nunca são sobrescritos.

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
3. Todo pedido de revisão, relatório e resposta começa com o **cabeçalho de versão** (abaixo), com SHAs completos de 40 caracteres, nunca abreviados.
4. Mudanças importantes entram em `04_historico/CHANGELOG.md`, com o SHA completo do commit.
5. Arquivos originais são preservados sempre que possível; correções geram uma nova versão.
6. Quando uma frase muda, quem muda lista o que depende dela: exercícios (`exercicios.csv` → `frases_usadas`), segmentos de áudio (`audio_segmentos.csv` → `id_frase`) e páginas diagramadas. O tipo de alteração (japonês, tradução, explicação, roteiro, áudio) é registrado como define `01_dados/ESQUEMA.md`, seção 6.
7. Resultados de testes só são registrados se o teste foi de fato executado; o registro diz quando, sobre qual arquivo (com SHA-256 e commit) e com qual saída.

### Cabeçalho de versão

```
Repositório: rha-hub/teste
Branch revisada: <nome>
Commit revisado: <SHA completo, 40 caracteres>
Commit base (main): <SHA completo, 40 caracteres>
Data e hora: <ISO 8601 com fuso>
Arquivos examinados (blob SHA de cada um, obtido com `git ls-tree <commit> <caminho>`):
| Arquivo | Blob SHA |
```

Um documento não pode conter o SHA do commit que o cria. Por isso, o pedido de revisão cita o commit que contém o material a revisar, e o próprio pedido entra num commit separado, logo depois.

## IDs dos materiais

| Tipo | Formato | Exemplo |
|---|---|---|
| Frase ou exemplo | `J<cap>-<nº>` | `J04-14` |
| Faixa de áudio | `A<cap>-<nº>` | `A04-03` |
| Exercício | `X<cap>-<rótulo>` | `X04-R1` |
| Resposta de exercício | `X<cap>-<rótulo>-<letra ou nº>` | `X04-R1-a` |
| Cartão de revisão | `K<cap>-<nº>` | `K04-07` |
| Validação | `V-<nº>` | `V-0001` |

Cartões usam `K` (e não `C`) para não serem confundidos com os IDs de apontamento, que começam com `C<capítulo>`.

IDs de materiais também nunca são reutilizados. Um item removido fica no CSV com `situacao=RETIRADA`.

## Dados e impressões

Colunas, relacionamentos entre frases, exercícios, respostas e áudios, listas de IDs, respostas alternativas e a proposta de impressões SHA-256 estão em [`01_dados/ESQUEMA.md`](01_dados/ESQUEMA.md).

**Estado atual:** os CSVs só têm cabeçalhos, e o script que calcula e compara as impressões **ainda não existe**. Nenhuma impressão foi calculada. A implementação depende de aprovação.

## Testes

`02_testes/teste-html-smoke.js` abre um arquivo HTML no Chromium (Playwright) em 1280 px e 390 px. O que ele cobre e o que fica de fora está em [`02_testes/COBERTURA.md`](02_testes/COBERTURA.md), junto com as execuções já feitas.

```
npm install playwright
npx playwright install chromium
node 02_testes/teste-html-smoke.js "caminho/do/arquivo.html" [--saida pasta]
```

Cada execução cria uma pasta nova em `02_testes/resultados/` (ou na pasta de `--saida`), nomeada com data, hora e arquivo testado; nada é sobrescrito. O relatório inclui o SHA-256 do arquivo testado e, se ele estiver num repositório git, o SHA completo do commit. Essa pasta não é versionada (`.gitignore`); quando um resultado é citado numa revisão, o `relatorio.json` correspondente é copiado para `03_revisao/`.

## Limites deste primeiro teste

Nenhum conteúdo de capítulo foi alterado, nenhum áudio novo foi gerado e nada foi publicado como produto.
