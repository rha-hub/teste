# Esquema dos dados de rastreabilidade

Versão do esquema: **3** (2026-10-30).
- Versão 2: commit `b94d020516d1fb0e43620225622fb592ee133dcf`.
- Versão 1: commit `e822d76fb83aced40c840e5915780ef412c0cd35`.

Mudanças da versão 3:
- a faixa lógica de áudio foi separada do arquivo produzido (novo `arquivos_audio.csv`);
- a seção 5 agora separa dependências linguísticas, pedagógicas, de roteiro e de arquivo;
- a coluna `imp_dependencias` saiu de `exercicios.csv`.

Este documento define os arquivos de `01_dados/`, como eles se relacionam e como detectar material desatualizado. **As impressões (seção 5) são uma proposta: nenhum script as calcula ainda, e nenhuma deve ser preenchida à mão.** A implementação depende de aprovação do responsável humano.

## 1. Convenções gerais

| Item | Regra |
|---|---|
| Codificação | UTF-8 sem BOM, fim de linha LF |
| Separador de colunas | vírgula; campos com vírgula, aspas ou quebra de linha vão entre aspas duplas (RFC 4180) |
| Listas de IDs dentro de uma célula | separadas por `\|` (barra vertical), sem espaços: `J04-07\|J04-08`. Só IDs entram em listas; texto livre nunca é lista |
| Célula vazia | significa "não se aplica". Nunca escreva `n/a`, `-` ou `0` no lugar |
| Valores fixos | em MAIÚSCULAS e sem acento (`NAO_USAR`, `ACEITA`), para evitar erros de comparação |
| Datas | ISO 8601 com fuso: `2026-10-30T02:27:39-03:00` |
| Commits | SHA completo de 40 caracteres, nunca abreviado |
| IDs | nunca reutilizados; item removido fica com `situacao=RETIRADA` |

**Por que `|` e não `;`:** o Excel em português usa `;` como separador de colunas ao abrir CSV; `;` dentro da célula seria confundido com uma nova coluna.

**Furigana:** a leitura fica dentro do próprio texto japonês, no formato `{kanji|leitura}`: `ねえ、{昨日|きのう}のアニメ、もう{見|み}た？`. O texto sem furigana é obtido removendo as marcações. Assim, uma mudança de leitura (あした → あす) é uma mudança no texto japonês e aparece nas dependências.

## 2. Arquivos e chaves

| Arquivo | Uma linha por | Chave |
|---|---|---|
| `frases.csv` | frase ou exemplo japonês | `id_frase` |
| `exercicios.csv` | item de exercício | `id_exercicio` |
| `respostas.csv` | resposta possível de um exercício (certa, aceita ou errada) | `id_resposta` |
| `audios.csv` | **faixa lógica**: o que é falado, independente de velocidade e de quantas vezes foi gravado | `id_audio` |
| `audio_segmentos.csv` | fala de uma faixa lógica, na ordem do roteiro | `id_audio` + `ordem` |
| `arquivos_audio.csv` | **arquivo produzido**: uma gravação de uma faixa, numa velocidade, a partir de uma versão do roteiro | `id_arquivo_audio` |
| `validacoes.csv` | decisão de um revisor sobre um item, numa das dimensões da seção 5 (só acrescenta, nunca edita) | `id_validacao` |

### Faixa lógica e arquivo de áudio

- `id_audio` (ex.: `A04-03`) identifica **a faixa lógica**: o roteiro (quais frases, em que ordem, com que personagem, voz, forma falada e pausas). É o que o livro, os exercícios e a página do QR citam.
- O roteiro de uma faixa vive em `audio_segmentos.csv`, com chave `id_audio` + `ordem`. Como `id_audio` é a faixa lógica, cada segmento aponta para uma única faixa, sem ambiguidade. O roteiro é o mesmo para todas as velocidades.
- Cada gravação é uma linha de `arquivos_audio.csv`, com `id_arquivo_audio` no formato `<id_audio>_v<velocidade>_r<versao_roteiro>_t<tomada>`. Exemplo: `A04-03_v080_r2_t1` é a faixa A04-03, a 80% da velocidade normal, gravada do roteiro versão 2, primeira tomada.
- A velocidade é escrita como porcentagem da normal com três dígitos (`v100`, `v080`). Esse formato aceita qualquer conjunto de velocidades e não decide quais existirão; essa decisão é do responsável humano (seção 7).
- Para cada par (`id_audio`, `velocidade`), no máximo um arquivo tem `situacao=ATIVO`. Os anteriores ficam como `SUBSTITUIDO`: o histórico é preservado e não há dúvida sobre qual arquivo está em uso.

## 3. Relacionamentos

```
frases ──< exercicios.frases_usadas (lista)        um exercício usa 1+ frases; uma frase aparece em 0+ exercícios
exercicios ──< respostas                           cada exercício tem 1+ respostas CORRETA e 0+ ACEITA/ERRADA
exercicios.audios (lista) >── audios.id_audio      um exercício de escuta cita 1+ faixas lógicas
audios ──< audio_segmentos                         uma faixa lógica tem 1+ segmentos ordenados
audio_segmentos.id_frase >── frases                cada segmento fala exatamente uma frase
audios ──< arquivos_audio                          uma faixa lógica tem 0+ arquivos (velocidades, versões, tomadas)
validacoes.id_item → frase, exercício, faixa ou arquivo
```

Regras de integridade que o futuro script vai checar:

1. Todo ID citado em `frases_usadas`, `audios`, `audio_segmentos.id_frase`, `arquivos_audio.id_audio` e `validacoes.id_item` existe no arquivo de origem.
2. Todo exercício ativo tem pelo menos uma resposta `CORRETA` ativa.
3. Toda faixa lógica ativa tem segmentos; `ordem` começa em 1, sem buracos.
4. Um item `RETIRADA` não é citado por nenhum item ativo.
5. Um exercício só usa frases cujo capítulo é igual ou anterior ao dele.
6. `id_arquivo_audio` é coerente com as colunas `id_audio`, `velocidade` e `versao_roteiro` da mesma linha.
7. No máximo um arquivo `ATIVO` por (`id_audio`, `velocidade`).

### Respostas alternativas

`respostas.csv` tem uma linha por resposta, com `tipo`:

- `CORRETA`: a resposta de referência. Pode haver mais de uma (ex.: 見てる e 見ている são ambas certas num exercício que pede "qualquer forma natural").
- `ACEITA`: legítima, mas não a esperada; o feedback explica a diferença (ex.: 見ておかなきゃ aceita onde se esperava 見とかなきゃ).
- `ERRADA`: alternativa de múltipla escolha ou erro comum previsto, com a explicação de por que não serve.

Em exercícios de escrita, `exercicios.regra_comparacao` diz como a resposta do aluno é comparada:

| Valor | Significado |
|---|---|
| `EXATA` | igual ao texto, depois de normalização Unicode NFC |
| `IGNORA_PONTUACAO_FINAL` | ignora 。、！？.,!? e espaços no fim |
| `MANUAL` | não há correção automática; o aluno compara com o gabarito comentado |

## 4. Colunas

### frases.csv
| Coluna | Faceta | Conteúdo |
|---|---|---|
| `id_frase` | — | `J<cap>-<nº>`, ex. `J04-14` |
| `capitulo`, `licao` | — | `4`, `4.3` |
| `forma_completa` | japonês | com furigana `{kanji\|leitura}` |
| `forma_reduzida` | japonês | com furigana; vazia se a frase não tem redução |
| `reducao` | explicação | ex. `てしまう→ちゃう` |
| `registro` | explicação | `FORMAL`, `NEUTRO_POLIDO`, `CASUAL`, `RUDE`, `REGIONAL` |
| `traducao_ptbr` | tradução | |
| `explicacao_curta` | explicação | |
| `versao_japones`, `versao_traducao`, `versao_explicacao` | — | inteiros; sobem quando a faceta muda |
| `imp_japones`, `imp_traducao`, `imp_explicacao` | — | impressões (seção 5); vazias até haver script |
| `situacao` | — | `ATIVA` ou `RETIRADA` |
| `observacoes` | — | texto livre |

### exercicios.csv
`id_exercicio` (`X04-R1`) · `capitulo` · `licao` · `degrau` (`RECONHECER`, `ESCREVER`, `ESCOLHER_TOM`) · `tipo` (`MULTIPLA_ESCOLHA`, `ESCRITA`, `ESCUTA`) · `enunciado` · `frases_usadas` (lista) · `audios` (lista de faixas lógicas, vazia se não há áudio) · `secao_que_ensina` · `regra_comparacao` · `versao` · `imp_exercicio` · `situacao` · `observacoes`

### respostas.csv
`id_resposta` (`X04-R1-a`) · `id_exercicio` · `rotulo` (letra exibida, vazia em escrita) · `texto` · `tipo` (`CORRETA`, `ACEITA`, `ERRADA`) · `explicacao` · `versao` · `imp_resposta` · `situacao` · `observacoes`

### audios.csv (faixa lógica)
`id_audio` (`A04-03`) · `capitulo` · `descricao` · `versao_roteiro` · `imp_roteiro` · `qr_pagina` · `situacao` (`ATIVA`, `RETIRADA`) · `observacoes`

### audio_segmentos.csv (roteiro da faixa lógica)
`id_audio` · `ordem` (1, 2, 3…) · `id_frase` · `forma_falada` (`COMPLETA` ou `REDUZIDA`) · `personagem` · `voz` · `pausa_depois_ms` · `imp_japones_usada` (a `imp_japones` da frase no momento em que o roteiro foi fechado)

### arquivos_audio.csv (arquivo produzido)
`id_arquivo_audio` (`A04-03_v080_r2_t1`) · `id_audio` · `velocidade` (`100`, `080`…) · `versao_roteiro` (versão usada na gravação) · `tomada` · `imp_roteiro_gerado` (a `imp_roteiro` da faixa no momento da gravação) · `arquivo` (caminho relativo) · `sha256_arquivo` · `gerado_em` · `servico_modelo_voz` · `plano_licenca` · `transcricao_confere` (`SIM`, `NAO`, vazio = não verificado) · `situacao` (`ATIVO`, `SUBSTITUIDO`, `RETIRADO`) · `observacoes`

### validacoes.csv
`id_validacao` (`V-0001`, sequencial) · `data` · `id_item` · `dimensao` (seção 5) · `imp_validada` (a impressão de dependência da dimensão, no momento da decisão) · `status` (`APROVADO`, `AJUSTAR`, `NAO_USAR`, `PENDENTE_DE_VALIDACAO`) · `revisor` (`CHATGPT`, `REVISOR_NATIVO`, `CLAUDE`, `RESPONSAVEL_HUMANO`) · `commit_revisado` (40 caracteres) · `apontamento` (ex. `C04-LING-001`) · `observacoes`

O status de um item **não** fica guardado na linha do item. Ele é a validação mais recente daquela dimensão **cuja impressão ainda bate com a atual**. Se alguma dependência mudou depois da validação, ela perde efeito sozinha. Assim, uma aprovação antiga não cobre material novo.

## 5. Impressões SHA-256 e dependências (proposta, não implementada)

### 5.1 Impressões de conteúdo (uma por faceta)

Cada impressão cobre só os campos da própria faceta:

| Impressão | Item | Campos |
|---|---|---|
| `imp_japones` | frase | `forma_completa`, `forma_reduzida` (com furigana) |
| `imp_traducao` | frase | `traducao_ptbr` |
| `imp_explicacao` | frase | `reducao`, `registro`, `explicacao_curta` |
| `imp_exercicio` | exercício | `tipo`, `enunciado`, `frases_usadas`, `audios`, `regra_comparacao` |
| `imp_resposta` | resposta | `tipo`, `texto`, `explicacao` |
| `imp_roteiro` | faixa lógica | segmentos em ordem (`ordem`, `id_frase`, `forma_falada`, `personagem`, `voz`, `pausa_depois_ms`) + a `imp_japones` atual de cada frase falada |
| `sha256_arquivo` | arquivo de áudio | os bytes do arquivo |

`imp_roteiro` inclui o japonês das frases, mas **não** inclui tradução nem explicação. Por isso, uma mudança de tradução ou explicação nunca torna uma gravação desatualizada.

### 5.2 Dependências por dimensão de validação

Cada validação é feita numa **dimensão**. A dimensão define de quais impressões a decisão depende. A `imp_validada` é o SHA-256 dessas impressões, na ordem da tabela.

| Dimensão | Item | Depende de | Invalidada por mudança em |
|---|---|---|---|
| `LINGUISTICA` | frase | `imp_japones` | japonês da frase |
| `TRADUCAO` | frase | `imp_japones`, `imp_traducao` | japonês ou tradução da frase |
| `PEDAGOGICA` | frase | `imp_japones`, `imp_traducao`, `imp_explicacao` | japonês, tradução ou explicação da frase |
| `PEDAGOGICA` | exercício | `imp_exercicio` + `imp_resposta` de todas as respostas ativas + `imp_japones`, `imp_traducao`, `imp_explicacao` de cada frase usada + `imp_roteiro` de cada faixa citada | exercício, respostas, qualquer faceta das frases usadas, roteiro das faixas citadas |
| `ROTEIRO` | faixa lógica | `imp_roteiro` | segmentos ou japonês das frases faladas |
| `AUDIO` | arquivo | `sha256_arquivo`, `imp_roteiro_gerado` | os bytes do arquivo (troca não registrada) |

Separadamente da validação, um **arquivo de áudio está desatualizado** quando o `imp_roteiro` atual da faixa é diferente do `imp_roteiro_gerado` do arquivo. Isso só acontece por mudança no roteiro ou no japonês das frases faladas.

Exemplos:

| Mudança | Validações invalidadas | Gravação desatualizada? |
|---|---|---|
| Tradução de `J04-07` | `TRADUCAO` e `PEDAGOGICA` de `J04-07`; `PEDAGOGICA` dos exercícios que usam `J04-07` | **não** |
| Explicação de `J04-07` | `PEDAGOGICA` de `J04-07` e dos exercícios que a usam | **não** |
| Japonês de `J04-07` (incluindo leitura do furigana) | todas as de `J04-07`; `ROTEIRO` das faixas que a falam; `PEDAGOGICA` dos exercícios que a usam ou que citam essas faixas | **sim**, nas faixas que falam `J04-07` |
| Voz de um segmento de `A04-03` | `ROTEIRO` de `A04-03`; `PEDAGOGICA` dos exercícios que citam `A04-03` | **sim**, todos os arquivos de `A04-03` |
| Uma resposta aceita nova em `X04-R1` | `PEDAGOGICA` de `X04-R1` | não se aplica |

### 5.3 Cálculo

1. Cada campo de texto é normalizado: Unicode NFC, quebras de linha CRLF → LF, espaços removidos no início e no fim.
2. Listas de IDs sem ordem (`frases_usadas`, `audios`, respostas de um exercício) são ordenadas por ID. Segmentos de áudio seguem `ordem`.
3. A entrada do hash é: `imp-v1`, o nome da impressão ou dimensão e os valores, nessa ordem, separados pelo caractere U+001F (separador de unidade). Esse caractere não aparece em texto comum, e assim `ab` + `c` e `a` + `bc` não dão o mesmo resultado. Itens dependentes entram como `id:impressão`.
4. Aplica-se SHA-256 e guarda-se o hexadecimal completo (64 caracteres). Relatórios podem mostrar só os 12 primeiros.
5. Se a regra mudar, o prefixo vira `imp-v2` e todas as impressões são recalculadas no mesmo commit.

### 5.4 Verificações que o script fará

| Situação | Diagnóstico |
|---|---|
| `imp_japones` atual de uma frase ≠ `imp_japones_usada` num segmento | roteiro da faixa desatualizado; o relatório diz qual frase mudou |
| `imp_roteiro` atual ≠ `imp_roteiro_gerado` de um arquivo `ATIVO` | a gravação precisa ser refeita |
| SHA-256 do arquivo em disco ≠ `sha256_arquivo` | o arquivo foi trocado sem registro |
| `imp_validada` ≠ impressão de dependência recalculada | a validação não vale mais; o relatório lista as dependências que mudaram |
| Regra de integridade da seção 3 violada | erro de dados |

O script só **relata**. Ele não altera textos, não gera áudio e não muda status.

## 6. O que distingue cada tipo de alteração

| Alteração | Como fica registrada | Efeito |
|---|---|---|
| Texto japonês | sobe `versao_japones`; muda `imp_japones` | invalida validações linguísticas, de tradução e pedagógicas; desatualiza roteiro e gravações das faixas que falam a frase |
| Tradução | sobe `versao_traducao`; muda `imp_traducao` | invalida validações de tradução e pedagógicas; **não** afeta gravação |
| Explicação pedagógica | sobe `versao_explicacao`; muda `imp_explicacao` | invalida validações pedagógicas; **não** afeta gravação |
| Roteiro (ordem, voz, pausa, forma falada) | sobe `versao_roteiro`; muda `imp_roteiro` | invalida validação de roteiro e pedagógica dos exercícios que citam a faixa; desatualiza todos os arquivos da faixa |
| Áudio produzido | nova linha em `arquivos_audio.csv`; a anterior vira `SUBSTITUIDO` | nova validação `AUDIO` necessária para o arquivo novo |

Toda alteração entra num commit cuja mensagem cita os IDs afetados, e as importantes também entram no `04_historico/CHANGELOG.md`.

## 7. Decisões pendentes do responsável humano

- Quais velocidades existirão (o formato `v<porcentagem>` aceita qualquer escolha).
- Se estes CSVs são a fonte oficial ou uma cópia de outra fonte (por exemplo, Google Sheets).
- Se os dados dos capítulos podem ficar neste repositório, que é público.
