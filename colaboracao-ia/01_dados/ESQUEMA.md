# Esquema dos dados de rastreabilidade

Versão do esquema: **2** (2026-10-30). Substitui a versão 1, que tinha três CSVs com colunas de status embutidas.

Este documento define os arquivos de `01_dados/`, como eles se relacionam e como detectar material desatualizado. **As impressões (seção 5) são uma proposta: nenhum script as calcula ainda, e nenhuma deve ser preenchida à mão.** A implementação só começa depois da aprovação do responsável humano.

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
| `audios.csv` | arquivo de áudio produzido (uma faixa em uma velocidade) | `id_audio` + `velocidade` |
| `audio_segmentos.csv` | fala de uma faixa, na ordem do roteiro | `id_audio` + `ordem` |
| `validacoes.csv` | decisão de um revisor sobre uma faceta de um item (só acrescenta, nunca edita) | `id_validacao` |

## 3. Relacionamentos

```
frases ──< exercicios.frases_usadas (lista)      um exercício usa 1+ frases; uma frase aparece em 0+ exercícios
exercicios ──< respostas                         cada exercício tem 1+ respostas CORRETA e 0+ ACEITA/ERRADA
exercicios.audios (lista) >── audios.id_audio    um exercício de escuta usa 1+ faixas
audios.id_audio ──< audio_segmentos              uma faixa tem 1+ segmentos ordenados
audio_segmentos.id_frase >── frases              cada segmento fala exatamente uma frase
validacoes.id_item → qualquer item acima         cada validação se refere a uma faceta de um item
```

Regras de integridade que o futuro script vai checar:

1. Todo ID citado em `frases_usadas`, `audios`, `audio_segmentos.id_frase` e `validacoes.id_item` existe no arquivo de origem.
2. Todo exercício ativo tem pelo menos uma resposta `CORRETA` ativa.
3. Toda faixa citada em `audios.csv` tem segmentos; `ordem` começa em 1, sem buracos.
4. Um item `RETIRADA` não é citado por nenhum item ativo.
5. Um exercício só usa frases cujo capítulo é igual ou anterior ao dele.

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
`id_exercicio` (`X04-R1`) · `capitulo` · `licao` · `degrau` (`RECONHECER`, `ESCREVER`, `ESCOLHER_TOM`) · `tipo` (`MULTIPLA_ESCOLHA`, `ESCRITA`, `ESCUTA`) · `enunciado` · `frases_usadas` (lista) · `audios` (lista, vazia se não há áudio) · `secao_que_ensina` · `regra_comparacao` · `versao` · `imp_exercicio` · `imp_dependencias` · `situacao` · `observacoes`

### respostas.csv
`id_resposta` (`X04-R1-a`) · `id_exercicio` · `rotulo` (letra exibida, vazia em escrita) · `texto` · `tipo` (`CORRETA`, `ACEITA`, `ERRADA`) · `explicacao` · `versao` · `imp_resposta` · `situacao` · `observacoes`

### audios.csv
`id_audio` (`A04-03`) · `velocidade` (valores ainda não decididos; ver seção 7) · `capitulo` · `descricao` · `versao_roteiro` · `imp_roteiro` · `imp_roteiro_gerado` · `arquivo` (caminho relativo) · `sha256_arquivo` · `gerado_em` · `servico_modelo_voz` · `plano_licenca` · `transcricao_confere` (`SIM`, `NAO`, vazio = não verificado) · `qr_pagina` · `situacao` · `observacoes`

### audio_segmentos.csv
`id_audio` · `ordem` (1, 2, 3…) · `id_frase` · `forma_falada` (`COMPLETA` ou `REDUZIDA`) · `personagem` · `voz` · `pausa_depois_ms` · `imp_japones_usada` (a `imp_japones` da frase no momento em que o roteiro foi fechado)

### validacoes.csv
`id_validacao` (`V-0001`, sequencial) · `data` · `id_item` · `faceta` · `imp_validada` · `status` (`APROVADO`, `AJUSTAR`, `NAO_USAR`, `PENDENTE_DE_VALIDACAO`) · `revisor` (`CHATGPT`, `REVISOR_NATIVO`, `CLAUDE`, `RESPONSAVEL_HUMANO`) · `commit_revisado` (40 caracteres) · `apontamento` (ex. `C04-LING-001`) · `observacoes`

O status de um item **não** fica guardado na linha do item: ele é a validação mais recente daquela faceta **cuja impressão ainda bate com a atual**. Se o texto mudou depois da validação, a validação perde efeito sozinha e o item volta a ficar sem status válido. Isso impede que uma aprovação antiga "cubra" um texto novo.

## 5. Impressões SHA-256 (proposta, não implementada)

### Facetas: o que muda e o que isso afeta

| Faceta | Campos que entram no cálculo | Quando muda, fica desatualizado |
|---|---|---|
| `japones` (frase) | `forma_completa`, `forma_reduzida` | roteiro e áudio das faixas que falam a frase; exercícios que usam a frase; validações linguísticas da frase |
| `traducao` (frase) | `traducao_ptbr` | validação de tradução da frase; exercícios que usam a frase (revisão pedagógica, não áudio) |
| `explicacao` (frase) | `reducao`, `registro`, `explicacao_curta` | validação pedagógica da frase; exercícios `ESCOLHER_TOM` que usam a frase |
| `exercicio` | `tipo`, `enunciado`, `frases_usadas`, `audios`, `regra_comparacao` | respostas do exercício; validação pedagógica do exercício |
| `resposta` | `tipo`, `texto`, `explicacao` | validação da resposta |
| `roteiro` (faixa) | segmentos em ordem: `ordem`, `id_frase`, `forma_falada`, `personagem`, `voz`, `pausa_depois_ms` + a `imp_japones` atual de cada frase | todos os arquivos produzidos dessa faixa |
| `audio` (arquivo) | os bytes do MP3 | transcrição e validação daquele arquivo |

A tradução fica fora do cálculo do áudio de propósito: corrigir uma tradução não deve exigir regravar o áudio.

### Cálculo

1. Cada campo de texto é normalizado: Unicode NFC, quebras de linha CRLF → LF, espaços removidos no início e no fim.
2. Listas de IDs sem ordem (`frases_usadas`, `audios`) são ordenadas; segmentos de áudio seguem `ordem`.
3. A entrada do hash é: `imp-v1`, o nome da faceta e os campos, nessa ordem, separados pelo caractere U+001F (separador de unidade), que não aparece em texto comum. Isso evita que `ab` + `c` e `a` + `bc` deem o mesmo resultado.
4. Aplica-se SHA-256 e guarda-se o hexadecimal completo (64 caracteres). Relatórios podem mostrar só os 12 primeiros.
5. `imp_dependencias` de um exercício = SHA-256 de `imp-v1` + `dep` + a lista ordenada `id:imp_japones` das frases usadas + a lista `id:imp_roteiro` das faixas usadas.
6. `sha256_arquivo` = SHA-256 dos bytes do arquivo de áudio.

Se a regra de cálculo mudar, o prefixo muda para `imp-v2`, e todas as impressões são recalculadas no mesmo commit.

### Verificações que o script fará

| Situação detectada | Diagnóstico |
|---|---|
| `imp_japones` atual de uma frase ≠ `imp_japones_usada` em um segmento | o roteiro daquela faixa está desatualizado e diz qual frase mudou |
| `imp_roteiro` atual ≠ `imp_roteiro_gerado` de um arquivo | o áudio precisa ser gerado de novo |
| SHA-256 do arquivo em disco ≠ `sha256_arquivo` | o arquivo foi trocado sem registro |
| `imp_dependencias` recalculada ≠ a gravada | o exercício e suas respostas precisam de nova revisão |
| `imp_validada` ≠ impressão atual da faceta | a validação não vale mais para o texto atual |

O script só **relata**. Ele não altera textos, não gera áudio e não muda status.

## 6. O que distingue cada tipo de alteração

| Alteração | Como fica registrada |
|---|---|
| Texto japonês | sobe `versao_japones`; muda `imp_japones`; dispara a revisão de roteiro, áudio e exercícios dependentes |
| Tradução | sobe `versao_traducao`; muda `imp_traducao`; não dispara áudio |
| Explicação pedagógica | sobe `versao_explicacao`; muda `imp_explicacao`; não dispara áudio |
| Roteiro (ordem, voz, pausa, forma falada) | sobe `versao_roteiro`; muda `imp_roteiro`; todos os arquivos da faixa ficam desatualizados |
| Áudio produzido | nova linha ou novo `sha256_arquivo` + `imp_roteiro_gerado` + `gerado_em` |

Toda alteração entra num commit cuja mensagem cita os IDs afetados, e as importantes também entram no `04_historico/CHANGELOG.md`.

## 7. Decisões pendentes do responsável humano

- Valores de `velocidade` (hoje há três especificações diferentes no projeto).
- Se estes CSVs são a fonte oficial ou uma cópia de outra fonte (por exemplo, Google Sheets).
- Se os dados dos capítulos podem ficar neste repositório, que é público.
