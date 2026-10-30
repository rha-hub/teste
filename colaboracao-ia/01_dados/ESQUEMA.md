# Esquema dos dados de rastreabilidade

Versão do esquema: **4** (2026-10-30).
- Versão 3: commit `81c3479233768db7a5760d70790ca1f7096c071d`.
- Versão 2: commit `b94d020516d1fb0e43620225622fb592ee133dcf`.
- Versão 1: commit `e822d76fb83aced40c840e5915780ef412c0cd35`.

Mudanças da versão 4:
- novo `exercicio_audios.csv`: cada exercício de escuta diz qual faixa, em qual velocidade, e se usa uma gravação fixa ou a gravação ativa (P13);
- a coluna `audios` saiu de `exercicios.csv`;
- dimensões de validação separadas: `ROTEIRO`, `GRAVACAO` (antes `AUDIO`) e `ESCUTA` (nova);
- a validação pedagógica do exercício passa a depender da gravação efetivamente usada;
- nova seção 5.5, sobre a substituição de uma gravação ativa;
- conferência completa do identificador de arquivo, incluindo a tomada, e unicidade (P14);
- texto sobre CSV e Excel revisto, com instruções de importação (P15).

Mudanças da versão 3: faixa lógica separada do arquivo produzido; dependências por dimensão; `imp_dependencias` retirada de `exercicios.csv`.

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

**Por que `|` dentro das células:** o separador de colunas destes arquivos é a vírgula. Algumas ferramentas, porém, interpretam CSV com `;` como separador, dependendo da configuração regional e da forma de abertura. A barra vertical raramente aparece em texto e não costuma ser usada como separador de colunas, por isso fica segura dentro de uma célula em qualquer um dos casos.

### Abrir os CSVs em planilhas

O separador destes arquivos é **sempre a vírgula**, e a codificação é UTF-8. O comportamento ao abrir um CSV **varia**:

- No Excel, abrir o arquivo com duplo clique faz o programa escolher o separador e a codificação pelas configurações regionais do computador (no Windows, o "separador de lista"). Em algumas instalações configuradas para o português, esse separador é `;`, e o arquivo aparece numa coluna só ou com acentos e japonês corrompidos. Em outras instalações, abre corretamente. Não dá para presumir qual será o caso.
- O caminho que não depende dessa configuração é **importar**: no Excel, use a opção de obter dados de texto/CSV (em versões recentes, guia *Dados* → *De Texto/CSV*; o nome exato varia conforme a versão). Escolha a origem **65001: Unicode (UTF-8)** e o delimitador **Vírgula**.
- No LibreOffice Calc, a janela de importação aparece ao abrir o arquivo: marque **Vírgula** como separador e **Unicode (UTF-8)** como conjunto de caracteres.
- No Google Planilhas, use *Arquivo* → *Importar* e escolha **Vírgula** como separador, se ele não for detectado.
- Ao salvar de volta, mantenha **CSV UTF-8, separado por vírgula**. Se a planilha gravar com `;` ou com outra codificação, o arquivo deixa de seguir este esquema, e a mudança aparece no diff do commit.

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
| `exercicio_audios.csv` | áudio usado por um exercício: faixa, velocidade e modo de seleção da gravação | `id_exercicio` + `ordem` |
| `validacoes.csv` | decisão de um revisor sobre um item, numa das dimensões da seção 5 (só acrescenta, nunca edita) | `id_validacao` |

### Faixa lógica e arquivo de áudio

- `id_audio` (ex.: `A04-03`) identifica **a faixa lógica**: o roteiro (quais frases, em que ordem, com que personagem, voz, forma falada e pausas). É o que o livro, os exercícios e a página do QR citam.
- O roteiro de uma faixa vive em `audio_segmentos.csv`, com chave `id_audio` + `ordem`. Como `id_audio` é a faixa lógica, cada segmento aponta para uma única faixa, sem ambiguidade. O roteiro é o mesmo para todas as velocidades.
- Cada gravação é uma linha de `arquivos_audio.csv`, com `id_arquivo_audio` no formato `<id_audio>_v<velocidade>_r<versao_roteiro>_t<tomada>`. Exemplo: `A04-03_v080_r2_t1` é a faixa A04-03, a 80% da velocidade normal, gravada do roteiro versão 2, primeira tomada.
- Formato de cada parte:
  - `velocidade`: porcentagem da normal com exatamente três dígitos (`100`, `080`). Esse formato aceita qualquer conjunto de velocidades; quais existirão é decisão do responsável humano (seção 7).
  - `versao_roteiro`: inteiro ≥ 1, sem zeros à esquerda.
  - `tomada`: inteiro ≥ 1, sem zeros à esquerda; numera gravações da mesma faixa, velocidade e versão de roteiro.
- `id_arquivo_audio` é **único** em `arquivos_audio.csv` e nunca é reutilizado, nem depois de `RETIRADO`. A combinação (`id_audio`, `velocidade`, `versao_roteiro`, `tomada`) também é única. Uma nova gravação com roteiro igual recebe a próxima `tomada`.
- Para cada par (`id_audio`, `velocidade`), no máximo um arquivo tem `situacao=ATIVO`. Os anteriores ficam como `SUBSTITUIDO`: o histórico é preservado e não há dúvida sobre qual arquivo está em uso. O que acontece com os exercícios quando a gravação ativa muda está na seção 5.5.

### Áudio usado por um exercício

`exercicio_audios.csv` diz, para cada exercício de escuta, qual áudio o aluno ouve. Uma linha por áudio, na ordem em que aparece no exercício. A linha indica a faixa, a velocidade e o modo de seleção:

| `modo_selecao` | O exercício usa | `id_arquivo_audio` | Quando usar |
|---|---|---|---|
| `ATIVO` | a gravação que estiver `ATIVO` para (`id_audio`, `velocidade`) no momento | vazio | caso normal: o exercício acompanha a gravação em uso na página do QR |
| `FIXO` | sempre a gravação indicada, mesmo que outra se torne ativa | obrigatório | quando o exercício depende de uma tomada específica (ex.: uma hesitação ou entonação que a explicação comenta) |

O arquivo que o aluno efetivamente ouve é chamado de **gravação resolvida**: a indicada, no modo `FIXO`, ou a `ATIVO` do momento, no modo `ATIVO`. É ela que entra nas validações do exercício (seção 5.2).

## 3. Relacionamentos

```
frases ──< exercicios.frases_usadas (lista)        um exercício usa 1+ frases; uma frase aparece em 0+ exercícios
exercicios ──< respostas                           cada exercício tem 1+ respostas CORRETA e 0+ ACEITA/ERRADA
exercicios ──< exercicio_audios                    um exercício de escuta usa 1+ áudios, em ordem
exercicio_audios.id_audio >── audios               cada linha aponta para uma faixa lógica, numa velocidade
exercicio_audios.id_arquivo_audio >── arquivos_audio   só no modo FIXO
audios ──< audio_segmentos                         uma faixa lógica tem 1+ segmentos ordenados
audio_segmentos.id_frase >── frases                cada segmento fala exatamente uma frase
audios ──< arquivos_audio                          uma faixa lógica tem 0+ arquivos (velocidades, versões, tomadas)
validacoes.id_item → frase, exercício, faixa ou arquivo
```

Regras de integridade que o futuro script vai checar:

1. Todo ID citado em `frases_usadas`, `exercicio_audios`, `audio_segmentos.id_frase`, `arquivos_audio.id_audio` e `validacoes.id_item` existe no arquivo de origem.
2. Todo exercício ativo tem pelo menos uma resposta `CORRETA` ativa.
3. Toda faixa lógica ativa tem segmentos; `ordem` começa em 1, sem buracos (vale também para `exercicio_audios.ordem`).
4. Um item `RETIRADA` não é citado por nenhum item ativo.
5. Um exercício só usa frases cujo capítulo é igual ou anterior ao dele.
6. `id_arquivo_audio` é exatamente `<id_audio>_v<velocidade>_r<versao_roteiro>_t<tomada>`, montado com as colunas `id_audio`, `velocidade`, `versao_roteiro` e `tomada` **da mesma linha**, no formato da seção 2. Qualquer divergência, inclusive só na tomada, é erro.
7. No máximo um arquivo `ATIVO` por (`id_audio`, `velocidade`).
8. `id_arquivo_audio` é único em `arquivos_audio.csv`; a combinação (`id_audio`, `velocidade`, `versao_roteiro`, `tomada`) também.
9. Em `exercicio_audios.csv`: com `modo_selecao=FIXO`, `id_arquivo_audio` é obrigatório e pertence à mesma faixa e velocidade da linha; com `ATIVO`, é vazio.
10. Toda linha `ATIVO` de `exercicio_audios.csv` encontra uma gravação `ATIVO` para sua faixa e velocidade. Se não encontrar, é erro: o exercício ficaria sem áudio.
11. Uma linha `FIXO` que aponta para um arquivo `SUBSTITUIDO` gera **aviso** (o exercício usa uma gravação que não é mais a da página do QR). Se o arquivo estiver `RETIRADO`, é **erro**.

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
`id_exercicio` (`X04-R1`) · `capitulo` · `licao` · `degrau` (`RECONHECER`, `ESCREVER`, `ESCOLHER_TOM`) · `tipo` (`MULTIPLA_ESCOLHA`, `ESCRITA`, `ESCUTA`) · `enunciado` · `frases_usadas` (lista) · `secao_que_ensina` · `regra_comparacao` · `versao` · `imp_exercicio` · `situacao` · `observacoes`

Os áudios do exercício não ficam mais numa lista dentro de `exercicios.csv`; ficam em `exercicio_audios.csv`, que guarda também a velocidade e o modo de seleção.

### exercicio_audios.csv (áudio usado por exercício)
`id_exercicio` · `ordem` (1, 2, 3…) · `id_audio` (faixa lógica) · `velocidade` (mesmo formato de `arquivos_audio.velocidade`) · `modo_selecao` (`ATIVO` ou `FIXO`) · `id_arquivo_audio` (obrigatório se `FIXO`; vazio se `ATIVO`) · `uso` (`ESTIMULO`: o aluno precisa ouvir para responder; `APOIO`: áudio opcional, ex. ouvir de novo no gabarito) · `observacoes`

### respostas.csv
`id_resposta` (`X04-R1-a`) · `id_exercicio` · `rotulo` (letra exibida, vazia em escrita) · `texto` · `tipo` (`CORRETA`, `ACEITA`, `ERRADA`) · `explicacao` · `versao` · `imp_resposta` · `situacao` · `observacoes`

### audios.csv (faixa lógica)
`id_audio` (`A04-03`) · `capitulo` · `descricao` · `versao_roteiro` · `imp_roteiro` · `qr_pagina` · `situacao` (`ATIVA`, `RETIRADA`) · `observacoes`

### audio_segmentos.csv (roteiro da faixa lógica)
`id_audio` · `ordem` (1, 2, 3…) · `id_frase` · `forma_falada` (`COMPLETA` ou `REDUZIDA`) · `personagem` · `voz` · `pausa_depois_ms` · `imp_japones_usada` (a `imp_japones` da frase no momento em que o roteiro foi fechado)

### arquivos_audio.csv (arquivo produzido)
`id_arquivo_audio` (`A04-03_v080_r2_t1`) · `id_audio` · `velocidade` (`100`, `080`…) · `versao_roteiro` (versão usada na gravação) · `tomada` · `imp_roteiro_gerado` (a `imp_roteiro` da faixa no momento da gravação) · `arquivo` (caminho relativo) · `sha256_arquivo` · `gerado_em` · `servico_modelo_voz` · `plano_licenca` · `transcricao_confere` (`SIM`, `NAO`, vazio = não verificado) · `situacao` (`ATIVO`, `SUBSTITUIDO`, `RETIRADO`) · `observacoes`

### validacoes.csv
`id_validacao` (`V-0001`, sequencial) · `data` · `id_item` · `dimensao` (`LINGUISTICA`, `TRADUCAO`, `PEDAGOGICA`, `ROTEIRO`, `GRAVACAO`, `ESCUTA`; seção 5.2) · `imp_validada` (a impressão de dependência da dimensão, no momento da decisão) · `arquivos_audio_resolvidos` (lista de `id_arquivo_audio` das gravações resolvidas no momento da decisão, na ordem de `exercicio_audios`; vazia quando não há áudio) · `status` (`APROVADO`, `AJUSTAR`, `NAO_USAR`, `PENDENTE_DE_VALIDACAO`) · `revisor` (`CHATGPT`, `REVISOR_NATIVO`, `CLAUDE`, `RESPONSAVEL_HUMANO`) · `commit_revisado` (40 caracteres) · `apontamento` (ex. `C04-LING-001`) · `observacoes`

`arquivos_audio_resolvidos` é redundante com `imp_validada` de propósito: a impressão diz **se** algo mudou, e a lista diz **qual gravação** foi aprovada, sem precisar recalcular nada.

O status de um item **não** fica guardado na linha do item. Ele é a validação mais recente daquela dimensão **cuja impressão ainda bate com a atual**. Se alguma dependência mudou depois da validação, ela perde efeito sozinha. Assim, uma aprovação antiga não cobre material novo.

## 5. Impressões SHA-256 e dependências (proposta, não implementada)

### 5.1 Impressões de conteúdo (uma por faceta)

Cada impressão cobre só os campos da própria faceta:

| Impressão | Item | Campos |
|---|---|---|
| `imp_japones` | frase | `forma_completa`, `forma_reduzida` (com furigana) |
| `imp_traducao` | frase | `traducao_ptbr` |
| `imp_explicacao` | frase | `reducao`, `registro`, `explicacao_curta` |
| `imp_exercicio` | exercício | `tipo`, `enunciado`, `frases_usadas`, `regra_comparacao` + as linhas do exercício em `exercicio_audios.csv` como declaradas (`ordem`, `id_audio`, `velocidade`, `modo_selecao`, `id_arquivo_audio`, `uso`) |
| `imp_resposta` | resposta | `tipo`, `texto`, `explicacao` |
| `imp_roteiro` | faixa lógica | segmentos em ordem (`ordem`, `id_frase`, `forma_falada`, `personagem`, `voz`, `pausa_depois_ms`) + a `imp_japones` atual de cada frase falada |
| `sha256_arquivo` | arquivo de áudio | os bytes do arquivo |
| `imp_selecao_audio` | exercício | para cada linha de `exercicio_audios`, em ordem: `ordem`, a **gravação resolvida** (`id_arquivo_audio`), o `sha256_arquivo` e o `imp_roteiro_gerado` dela; calculada no momento da verificação, não é coluna |

`imp_roteiro` inclui o japonês das frases, mas **não** inclui tradução nem explicação. Por isso, uma mudança de tradução ou explicação nunca torna uma gravação desatualizada.

`imp_exercicio` registra o que o exercício **declara** (por exemplo, "faixa A04-03, 80%, gravação ativa"). `imp_selecao_audio` registra **qual arquivo** isso resolve hoje. No modo `ATIVO`, a declaração pode continuar igual enquanto o arquivo resolvido muda; por isso as duas impressões existem.

### 5.2 Dependências por dimensão de validação

Cada validação é feita numa **dimensão**. A dimensão define de quais impressões a decisão depende. A `imp_validada` é o SHA-256 dessas impressões, na ordem da tabela.

Os áudios são avaliados em três dimensões separadas, porque são decisões diferentes, tomadas por pessoas diferentes:

- `ROTEIRO`: o texto a ser falado está certo (frases, ordem, personagem, forma completa ou reduzida).
- `GRAVACAO`: este arquivo fala o roteiro com fidelidade, pronúncia correta e qualidade técnica. Não depende de nenhum exercício.
- `ESCUTA`: esta gravação, nesta velocidade, funciona para **este** exercício (a redução pedida é perceptível, a velocidade é adequada ao degrau, não há ambiguidade de áudio). Depende do exercício e da gravação resolvida.

| Dimensão | Item | Depende de | Invalidada por mudança em |
|---|---|---|---|
| `LINGUISTICA` | frase | `imp_japones` | japonês da frase |
| `TRADUCAO` | frase | `imp_japones`, `imp_traducao` | japonês ou tradução da frase |
| `PEDAGOGICA` | frase | `imp_japones`, `imp_traducao`, `imp_explicacao` | japonês, tradução ou explicação da frase |
| `PEDAGOGICA` | exercício | `imp_exercicio` + `imp_resposta` de todas as respostas ativas + `imp_japones`, `imp_traducao`, `imp_explicacao` de cada frase usada + `imp_roteiro` de cada faixa usada + `imp_selecao_audio` | exercício (inclusive a seleção de áudio declarada), respostas, qualquer faceta das frases usadas, roteiro das faixas usadas, **gravação efetivamente usada** |
| `ESCUTA` | exercício com áudio | `imp_exercicio` + `imp_selecao_audio` | exercício ou gravação efetivamente usada; **não** tradução nem explicação |
| `ROTEIRO` | faixa lógica | `imp_roteiro` | segmentos ou japonês das frases faladas |
| `GRAVACAO` | arquivo | `sha256_arquivo`, `imp_roteiro_gerado` | os bytes do arquivo (troca não registrada) |

Separadamente da validação, um **arquivo de áudio está desatualizado** quando o `imp_roteiro` atual da faixa é diferente do `imp_roteiro_gerado` do arquivo. Isso só acontece por mudança no roteiro ou no japonês das frases faladas.

**Regra preservada:** tradução e explicação não entram em `imp_roteiro`, `sha256_arquivo` nem `imp_selecao_audio`. Mudá-las invalida só validações `TRADUCAO` e `PEDAGOGICA`; nunca torna uma gravação desatualizada e nunca invalida `ROTEIRO`, `GRAVACAO` ou `ESCUTA`.

Exemplos:

| Mudança | Validações invalidadas | Gravação desatualizada? |
|---|---|---|
| Tradução de `J04-07` | `TRADUCAO` e `PEDAGOGICA` de `J04-07`; `PEDAGOGICA` dos exercícios que usam `J04-07` | **não** |
| Explicação de `J04-07` | `PEDAGOGICA` de `J04-07` e dos exercícios que a usam | **não** |
| Japonês de `J04-07` (incluindo leitura do furigana) | todas as de `J04-07`; `ROTEIRO` das faixas que a falam; `PEDAGOGICA` dos exercícios que a usam ou que usam essas faixas | **sim**, nas faixas que falam `J04-07` |
| Voz de um segmento de `A04-03` | `ROTEIRO` de `A04-03`; `PEDAGOGICA` dos exercícios que usam `A04-03` | **sim**, todos os arquivos de `A04-03` |
| Nova tomada de `A04-03` a 80% passa a `ATIVO`, roteiro igual | `PEDAGOGICA` e `ESCUTA` dos exercícios com `A04-03`, `080`, modo `ATIVO`; a nova gravação precisa de `GRAVACAO` | não (roteiro igual); ver 5.5 |
| Exercício troca a velocidade de `100` para `080` | `PEDAGOGICA` e `ESCUTA` do exercício | não se aplica |
| Uma resposta aceita nova em `X04-R1` | `PEDAGOGICA` de `X04-R1` | não se aplica |

### 5.3 Cálculo

1. Cada campo de texto é normalizado: Unicode NFC, quebras de linha CRLF → LF, espaços removidos no início e no fim.
2. Listas de IDs sem ordem (`frases_usadas`, respostas de um exercício) são ordenadas por ID. Segmentos de áudio e linhas de `exercicio_audios` seguem `ordem`.
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
| gravação resolvida hoje ≠ `arquivos_audio_resolvidos` da validação | a validação foi feita com outra gravação; o relatório diz qual era e qual é |
| linha `ATIVO` sem gravação ativa; linha `FIXO` apontando para arquivo substituído ou retirado | regras 10 e 11 da seção 3 |
| Regra de integridade da seção 3 violada | erro de dados |

O script só **relata**. Ele não altera textos, não gera áudio e não muda status.

### 5.5 Quando uma gravação ativa é substituída

Exemplo: `A04-03_v080_r2_t1` está `ATIVO`, e uma nova tomada `A04-03_v080_r2_t2` (mesmo roteiro) vai substituí-la.

1. A nova gravação entra como linha nova em `arquivos_audio.csv` e recebe `ATIVO`. A antiga passa a `SUBSTITUIDO` no **mesmo commit**, para nunca haver duas ativas (regra 7). Nada é apagado: a linha, o arquivo e as validações da gravação antiga ficam como histórico.
2. A gravação nova não herda nenhuma validação. Ela precisa da sua própria validação `GRAVACAO`.
3. **Exercícios em modo `ATIVO`** para (`A04-03`, `080`) passam a resolver para `t2`. A declaração do exercício não muda (`imp_exercicio` igual), mas `imp_selecao_audio` muda. Por isso, as validações `PEDAGOGICA` e `ESCUTA` desses exercícios deixam de valer até nova revisão. O relatório indica a troca de `t1` por `t2` a partir de `arquivos_audio_resolvidos`.
4. **Exercícios em modo `FIXO`** que apontam para `t1` continuam usando `t1`. As validações deles continuam válidas, porque o arquivo é o mesmo, mas o script emite aviso (regra 11): o exercício usa uma gravação que já não é a da página do QR. A equipe decide entre:
   - **passar o exercício para `t2` ou para o modo `ATIVO`**: a linha de `exercicio_audios` muda, `imp_exercicio` muda e o exercício volta para revisão;
   - **manter `t1` de propósito**: registra o motivo em `observacoes`, e `t1` não pode ser `RETIRADO` enquanto houver exercício `FIXO` usando o arquivo (regra 11).
5. A validação `ROTEIRO` da faixa não é afetada, porque o roteiro não mudou.
6. Se a substituição vier de **mudança de roteiro** (nova `versao_roteiro`), vale tudo acima, e além disso a validação `ROTEIRO` e as `PEDAGOGICA` que dependem de `imp_roteiro` também deixam de valer.

## 6. O que distingue cada tipo de alteração

| Alteração | Como fica registrada | Efeito |
|---|---|---|
| Texto japonês | sobe `versao_japones`; muda `imp_japones` | invalida validações linguísticas, de tradução e pedagógicas; desatualiza roteiro e gravações das faixas que falam a frase |
| Tradução | sobe `versao_traducao`; muda `imp_traducao` | invalida validações de tradução e pedagógicas; **não** afeta gravação |
| Explicação pedagógica | sobe `versao_explicacao`; muda `imp_explicacao` | invalida validações pedagógicas; **não** afeta gravação |
| Roteiro (ordem, voz, pausa, forma falada) | sobe `versao_roteiro`; muda `imp_roteiro` | invalida validação de roteiro e pedagógica dos exercícios que citam a faixa; desatualiza todos os arquivos da faixa |
| Áudio produzido (nova gravação ativa) | nova linha em `arquivos_audio.csv`; a anterior vira `SUBSTITUIDO` no mesmo commit | nova validação `GRAVACAO` para o arquivo novo; invalida `PEDAGOGICA` e `ESCUTA` dos exercícios em modo `ATIVO` daquela faixa e velocidade (seção 5.5) |
| Seleção de áudio de um exercício (faixa, velocidade, modo, gravação fixa) | linha alterada em `exercicio_audios.csv`; muda `imp_exercicio` | invalida `PEDAGOGICA` e `ESCUTA` do exercício; não afeta gravações |

Toda alteração entra num commit cuja mensagem cita os IDs afetados, e as importantes também entram no `04_historico/CHANGELOG.md`.

## 7. Decisões pendentes do responsável humano

- Quais velocidades existirão (o formato `v<porcentagem>` aceita qualquer escolha).
- Se estes CSVs são a fonte oficial ou uma cópia de outra fonte (por exemplo, Google Sheets).
- Se os dados dos capítulos podem ficar neste repositório, que é público.
