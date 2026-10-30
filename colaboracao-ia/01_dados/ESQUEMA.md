# Esquema dos dados de rastreabilidade

Versão do esquema: **5** (2026-10-30). **Implementado** em `05_ferramentas/verificar_dados.py` (`VERSAO_ESQUEMA = 5`) e **testado** em `02_testes/test_verificar_dados.py`. Toda regra deste documento existe no código. O que fica fora está listado na seção 8 e em `ESTADO.md`.

Histórico: v1 `e822d76fb83aced40c840e5915780ef412c0cd35` · v2 `b94d020516d1fb0e43620225622fb592ee133dcf` · v3 `81c3479233768db7a5760d70790ca1f7096c071d` · v4 `be6875222fa16a17fee460dcb8c80168cf828354`.

Mudanças da versão 5:
- `validacoes.csv` ganhou `revisor_identificacao`, e os valores de `revisor` agora distinguem competência (`HUMANO_JAPONES`, `HUMANO_RESPONSAVEL`, `HUMANO_OUTRO`, `IA_CHATGPT`, `IA_CLAUDE`);
- aprovação final por dimensão (seção 5.2);
- entradas exatas de cada impressão (seção 5.3), incluindo `rotulo` da resposta e `degrau`/`secao_que_ensina` do exercício;
- velocidades do piloto `100` e `080`;
- regras derivadas: 12 a 17 da seção 3;
- impressões correntes passam a ser obrigatórias e mantidas pelo comando `atualizar-impressoes`.

## 1. Convenções gerais

| Item | Regra | Verificação (código do achado) |
|---|---|---|
| Fonte oficial | estes CSVs, versionados no GitHub (decisão D-001) | — |
| Codificação | UTF-8 sem BOM | `CODIFICACAO` |
| Fim de linha | LF | `FIM_DE_LINHA` |
| Separador de colunas | vírgula; aspas duplas quando o campo tem vírgula, aspas ou quebra de linha (RFC 4180) | `COLUNAS` |
| Cabeçalho | exatamente as colunas da seção 4, na ordem | `CABECALHO` |
| Listas de IDs numa célula | separadas por `\|`, sem espaços; só IDs entram em listas | `FORMATO`, `LISTA_REPETIDA` |
| Célula vazia | "não se aplica"; nunca `n/a`, `-` ou `0` | `CAMPO_VAZIO` nos campos obrigatórios |
| Valores fixos | maiúsculas, sem acento (`NAO_USAR`) | `VALOR_INVALIDO` |
| Datas | ISO 8601 com fuso (`2026-10-30T02:27:39-03:00`) | `FORMATO` |
| Commits | SHA completo, 40 caracteres hexadecimais minúsculos | `FORMATO` |
| IDs | únicos e nunca reutilizados; item removido fica `RETIRADA`/`RETIRADO` | `ID_DUPLICADO` |

**Por que `|` dentro das células:** o separador de colunas é a vírgula, mas algumas ferramentas interpretam CSV com `;`, dependendo da configuração regional e da forma de abertura. A barra vertical raramente aparece em texto e não costuma ser separador de colunas.

### Abrir os CSVs em planilhas

O comportamento ao abrir um CSV **varia**:

- No Excel, abrir por duplo clique usa as configurações regionais do computador (no Windows, o "separador de lista"). Em algumas instalações em português esse separador é `;`, e o arquivo aparece numa coluna só ou com caracteres corrompidos. Em outras, abre corretamente.
- O caminho que não depende dessa configuração é **importar**: no Excel, use a opção de obter dados de texto/CSV (em versões recentes, *Dados* → *De Texto/CSV*; o nome varia por versão), com origem **65001: Unicode (UTF-8)** e delimitador **Vírgula**. No LibreOffice Calc, marque **Vírgula** e **Unicode (UTF-8)** na janela de importação. No Google Planilhas, use *Arquivo* → *Importar* com separador **Vírgula**.
- Ao salvar, mantenha **CSV UTF-8 separado por vírgula**. Se a planilha gravar com BOM, `;` ou CRLF, o verificador acusa `CODIFICACAO`, `CABECALHO` ou `FIM_DE_LINHA`.

**Furigana:** a leitura fica dentro do texto japonês, no formato `{kanji|leitura}`: `ねえ、{昨日|きのう}のアニメ、もう{見|み}た？`. Chaves ou barras fora desse padrão dão `FURIGANA`. Uma mudança de leitura (あした → あす) é uma mudança no texto japonês.

## 2. Arquivos e chaves

| Arquivo | Uma linha por | Chave |
|---|---|---|
| `frases.csv` | frase ou exemplo japonês | `id_frase` |
| `exercicios.csv` | item de exercício | `id_exercicio` |
| `respostas.csv` | resposta possível de um exercício | `id_resposta` |
| `audios.csv` | **faixa lógica** (o que é falado) | `id_audio` |
| `audio_segmentos.csv` | fala de uma faixa, na ordem do roteiro | `id_audio` + `ordem` |
| `arquivos_audio.csv` | **gravação produzida** (faixa × velocidade × versão do roteiro × tomada) | `id_arquivo_audio` |
| `exercicio_audios.csv` | áudio usado por um exercício | `id_exercicio` + `ordem` |
| `validacoes.csv` | decisão de um revisor sobre um item numa dimensão (só acrescenta) | `id_validacao` |

### Formatos de ID

| Tipo | Formato | Exemplo | Regra extra |
|---|---|---|---|
| Frase | `J<cap>-<nº>` | `J04-14` | `<cap>` = `capitulo` da linha (`CAPITULO_ID`) |
| Exercício | `X<cap>-<rótulo>` | `X04-R1` | idem |
| Resposta | `<id_exercicio>-<letra ou nº>` | `X04-R1-a` | prefixo = `id_exercicio` da linha (`ID_INCOERENTE`) |
| Faixa | `A<cap>-<nº>` | `A04-03` | `<cap>` = `capitulo` |
| Gravação | `<id_audio>_v<velocidade>_r<versao_roteiro>_t<tomada>` | `A04-03_v080_r2_t1` | regra 6 |
| Validação | `V-<nº, 4+ dígitos>` | `V-0001` | a ordem numérica define "mais recente" |

### Faixa lógica, gravação e velocidade

- `id_audio` é sempre a faixa lógica. O roteiro dela vive em `audio_segmentos.csv` e é o mesmo para todas as velocidades.
- Cada gravação é uma linha de `arquivos_audio.csv`. `velocidade` é a porcentagem da normal com exatamente três dígitos, entre `010` e `200`. **Velocidades do piloto: `100` (normal) e `080` (reduzida)** (decisão D-002). Qualquer outra gera `VELOCIDADE_FORA_DO_PILOTO` (aviso).
- `versao_roteiro` e `tomada` são inteiros ≥ 1, sem zeros à esquerda.
- Para cada par (`id_audio`, `velocidade`), no máximo uma gravação `ATIVO`. As anteriores ficam `SUBSTITUIDO` e não são apagadas.
- `arquivo` é um caminho **relativo** (sem `..`), resolvido a partir da pasta passada em `--raiz-audio`. Áudios comerciais não ficam no repositório (D-004, D-007).

### Áudio usado por um exercício

| `modo_selecao` | O exercício usa | `id_arquivo_audio` |
|---|---|---|
| `ATIVO` (padrão, D-003) | a gravação `ATIVO` de (`id_audio`, `velocidade`) | vazio |
| `FIXO` | sempre a gravação indicada | obrigatório, da mesma faixa e velocidade |

A gravação que o aluno efetivamente ouve é a **gravação resolvida**. `uso` diz se o áudio é necessário para responder (`ESTIMULO`) ou opcional (`APOIO`).

## 3. Regras de integridade

Severidade: **ERRO** (dados inválidos; código de saída 1), **PENDENCIA** (falta validação, gravação ou roteiro atualizado; código 2), **AVISO** (não bloqueia; código 0).

| Nº | Regra | Código | Severidade |
|---|---|---|---|
| 1 | Todo ID citado existe na tabela de origem (`frases_usadas`, `respostas.id_exercicio`, `audio_segmentos.id_audio/id_frase`, `arquivos_audio.id_audio`, `exercicio_audios.*`, `validacoes.id_item`) | `REFERENCIA_INEXISTENTE`, `ARQUIVO_INEXISTENTE` | ERRO |
| 2 | Todo exercício ativo tem ao menos uma resposta `CORRETA` ativa | `SEM_RESPOSTA_CORRETA` | ERRO |
| 3 | Toda faixa ativa tem segmentos; `ordem` de segmentos e de `exercicio_audios` é 1..n sem buracos | `FAIXA_SEM_SEGMENTOS`, `ORDEM_COM_BURACO` | ERRO |
| 4 | Item ativo não cita item retirado (frase, faixa, gravação ativa de faixa retirada) | `REFERENCIA_RETIRADA` | ERRO |
| 5 | Exercício só usa frases de capítulo igual ou anterior | `CAPITULO_POSTERIOR` | ERRO |
| 6 | `id_arquivo_audio` = `<id_audio>_v<velocidade>_r<versao_roteiro>_t<tomada>` com as colunas da mesma linha, inclusive a tomada | `ID_ARQUIVO_INCOERENTE` | ERRO |
| 7 | No máximo uma gravação `ATIVO` por (`id_audio`, `velocidade`) | `MAIS_DE_UM_ATIVO` | ERRO |
| 8 | `id_arquivo_audio` único; (`id_audio`, `velocidade`, `versao_roteiro`, `tomada`) único; demais chaves únicas | `ID_DUPLICADO` | ERRO |
| 9 | `FIXO` exige `id_arquivo_audio` da mesma faixa e velocidade; `ATIVO` exige vazio | `FIXO_SEM_ARQUIVO`, `FIXO_INCOERENTE`, `ATIVO_COM_ARQUIVO` | ERRO |
| 10 | Linha `ATIVO` de exercício ativo encontra uma gravação `ATIVO` | `SEM_GRAVACAO_ATIVA` | ERRO |
| 11 | `FIXO` apontando para gravação `SUBSTITUIDO` → aviso; para `RETIRADO` → erro | `FIXO_SUBSTITUIDO` / `FIXO_RETIRADO` | AVISO / ERRO |
| 12 | Exercício `ESCUTA` tem ao menos um áudio `ESTIMULO` | `ESCUTA_SEM_AUDIO` | ERRO |
| 13 | Segmento `REDUZIDA` só para frase com `forma_reduzida` | `FORMA_INEXISTENTE` | ERRO |
| 14 | Gravação não pode ter `versao_roteiro` maior que a da faixa | `VERSAO_FUTURA` | ERRO |
| 15 | Capítulo no ID = `capitulo`; prefixo da resposta = `id_exercicio` | `CAPITULO_ID`, `ID_INCOERENTE` | ERRO |
| 16 | Furigana bem formada | `FURIGANA` | ERRO |
| 17 | Validação humana tem `revisor_identificacao`; dimensão compatível com o item; `arquivos_audio_resolvidos` presente e completo só quando o item é exercício com áudio | `REVISOR_SEM_IDENTIFICACAO`, `DIMENSAO_INCOMPATIVEL`, `RESOLVIDOS_INCOMPLETO`, `RESOLVIDOS_INDEVIDO` | ERRO |

## 4. Colunas

### frases.csv
`id_frase` · `capitulo` · `licao` (opcional, `4` ou `4.3`) · `forma_completa` (obrigatória, com furigana) · `forma_reduzida` (vazia se não há redução) · `reducao` (ex. `てしまう→ちゃう`) · `registro` (`FORMAL`, `NEUTRO_POLIDO`, `CASUAL`, `RUDE`, `REGIONAL`) · `traducao_ptbr` (obrigatória) · `explicacao_curta` · `versao_japones` · `versao_traducao` · `versao_explicacao` (inteiros ≥ 1) · `imp_japones` · `imp_traducao` · `imp_explicacao` · `situacao` (`ATIVA`, `RETIRADA`) · `observacoes`

### exercicios.csv
`id_exercicio` · `capitulo` · `licao` · `degrau` (`RECONHECER`, `ESCREVER`, `ESCOLHER_TOM`) · `tipo` (`MULTIPLA_ESCOLHA`, `ESCRITA`, `ESCUTA`) · `enunciado` · `frases_usadas` (lista, ≥ 1) · `secao_que_ensina` · `regra_comparacao` (`EXATA`, `IGNORA_PONTUACAO_FINAL`, `MANUAL`) · `versao` · `imp_exercicio` · `situacao` · `observacoes`

### respostas.csv
`id_resposta` · `id_exercicio` · `rotulo` (letra exibida; vazia em escrita) · `texto` · `tipo` (`CORRETA`, `ACEITA`, `ERRADA`) · `explicacao` · `versao` · `imp_resposta` · `situacao` · `observacoes`

`CORRETA` é a resposta de referência (pode haver mais de uma). `ACEITA` é legítima, mas não a esperada. `ERRADA` é uma alternativa errada ou um erro comum previsto.

### audios.csv (faixa lógica)
`id_audio` · `capitulo` · `descricao` · `versao_roteiro` · `imp_roteiro` · `qr_pagina` · `situacao` (`ATIVA`, `RETIRADA`) · `observacoes`

### audio_segmentos.csv (roteiro)
`id_audio` · `ordem` · `id_frase` · `forma_falada` (`COMPLETA`, `REDUZIDA`) · `personagem` · `voz` · `pausa_depois_ms` (inteiro ≥ 0) · `imp_japones_usada` (instantâneo: a `imp_japones` da frase quando o roteiro foi fechado)

### arquivos_audio.csv (gravação)
`id_arquivo_audio` · `id_audio` · `velocidade` · `versao_roteiro` · `tomada` · `imp_roteiro_gerado` (instantâneo: a `imp_roteiro` da faixa no momento da gravação) · `arquivo` · `sha256_arquivo` · `gerado_em` · `servico_modelo_voz` · `plano_licenca` · `transcricao_confere` (`SIM`, `NAO`, vazio) · `situacao` (`ATIVO`, `SUBSTITUIDO`, `RETIRADO`) · `observacoes`

### exercicio_audios.csv
`id_exercicio` · `ordem` · `id_audio` · `velocidade` · `modo_selecao` (`ATIVO`, `FIXO`) · `id_arquivo_audio` · `uso` (`ESTIMULO`, `APOIO`) · `observacoes`

### validacoes.csv
`id_validacao` · `data` · `id_item` · `dimensao` (`LINGUISTICA`, `TRADUCAO`, `PEDAGOGICA`, `ROTEIRO`, `GRAVACAO`, `ESCUTA`) · `imp_validada` · `arquivos_audio_resolvidos` (lista, na ordem de `exercicio_audios`) · `status` (`APROVADO`, `AJUSTAR`, `NAO_USAR`, `PENDENTE_DE_VALIDACAO`) · `revisor` (`HUMANO_JAPONES`, `HUMANO_RESPONSAVEL`, `HUMANO_OUTRO`, `IA_CHATGPT`, `IA_CLAUDE`) · `revisor_identificacao` (obrigatória para `HUMANO_*`) · `commit_revisado` · `apontamento` · `observacoes`

### Colunas correntes e instantâneos

| Tipo | Colunas | Quem preenche |
|---|---|---|
| **Correntes**: descrevem o conteúdo atual | `imp_japones`, `imp_traducao`, `imp_explicacao`, `imp_exercicio`, `imp_resposta`, `imp_roteiro` e as versões correspondentes | `verificar_dados.py atualizar-impressoes`. Vazias → `IMPRESSAO_NAO_GRAVADA`; diferentes do conteúdo → `IMPRESSAO_GRAVADA_DIVERGENTE` (ERRO) |
| **Instantâneos**: registram um momento | `imp_japones_usada`, `imp_roteiro_gerado`, `sha256_arquivo`, `imp_validada`, `arquivos_audio_resolvidos` | `fechar-roteiro`, quem grava o áudio, `impressao-validacao`; o `atualizar-impressoes` **nunca** os altera |

`atualizar-impressoes` sobe a versão da faceta (`versao_japones`, `versao_traducao`, `versao_explicacao`, `versao` ou `versao_roteiro`) quando a impressão gravada existia e mudou.

## 5. Impressões e dependências

### 5.1 Impressões de conteúdo

| Impressão | Item | Entradas, na ordem |
|---|---|---|
| `imp_japones` | frase | `forma_completa`, `forma_reduzida` |
| `imp_traducao` | frase | `traducao_ptbr` |
| `imp_explicacao` | frase | `reducao`, `registro`, `explicacao_curta` |
| `imp_resposta` | resposta | `rotulo`, `tipo`, `texto`, `explicacao` |
| `imp_exercicio` | exercício | `degrau`, `tipo`, `enunciado`, `frases_usadas` (IDs ordenados, unidos por `\|`), `secao_que_ensina`, `regra_comparacao`, lista das linhas de `exercicio_audios` por `ordem`: (`ordem`, `id_audio`, `velocidade`, `modo_selecao`, `id_arquivo_audio`, `uso`) |
| `imp_roteiro` | faixa | lista dos segmentos por `ordem`: (`ordem`, `id_frase`, `forma_falada`, `personagem`, `voz`, `pausa_depois_ms`, `imp_japones` **atual** da frase) |
| `imp_selecao_audio` | exercício (calculada, não é coluna) | lista por `ordem` das gravações resolvidas: (`ordem`, `id_arquivo_audio`, `sha256_arquivo`, `imp_roteiro_gerado`) |
| `sha256_arquivo` | gravação | SHA-256 dos bytes do arquivo |

`imp_japones` cobre as duas formas da frase. Por escolha conservadora, mudar a forma completa também desatualiza o roteiro de uma faixa que fala só a forma reduzida.

`imp_roteiro` inclui o japonês das frases, mas **não** inclui tradução nem explicação. Tradução e explicação nunca desatualizam gravações.

### 5.2 Dimensões de validação

| Dimensão | Item | `imp_validada` = impressão de (na ordem) | Aprovação final por |
|---|---|---|---|
| `LINGUISTICA` | frase | `imp_japones` | `HUMANO_JAPONES` |
| `TRADUCAO` | frase | `imp_japones`, `imp_traducao` | `HUMANO_JAPONES` |
| `PEDAGOGICA` | frase | `imp_japones`, `imp_traducao`, `imp_explicacao` | `HUMANO_JAPONES`, `HUMANO_RESPONSAVEL` |
| `PEDAGOGICA` | exercício | `imp_exercicio`; lista (id, `imp_resposta`) das respostas ativas por ID; lista (id, `imp_japones`, `imp_traducao`, `imp_explicacao`) das frases usadas por ID; lista (id, `imp_roteiro`) das faixas usadas por ID; `imp_selecao_audio` | `HUMANO_JAPONES`, `HUMANO_RESPONSAVEL` |
| `ESCUTA` | exercício com áudio | `imp_exercicio`, `imp_selecao_audio` | `HUMANO_JAPONES`, `HUMANO_RESPONSAVEL` |
| `ROTEIRO` | faixa | `imp_roteiro` | `HUMANO_JAPONES`, `HUMANO_RESPONSAVEL` |
| `GRAVACAO` | gravação | `sha256_arquivo`, `imp_roteiro_gerado` | `HUMANO_JAPONES` |

O que cada dimensão julga (decisão D-005): linguística, a correção do japonês; tradução, a fidelidade e a naturalidade em português; pedagógica, nível, clareza e coerência; roteiro, o texto e a sequência falada; gravação, a fidelidade, a pronúncia e a qualidade técnica do arquivo; escuta, a adequação da gravação ao exercício e à velocidade.

Para um exercício sem áudio, `imp_selecao_audio` é a impressão de uma lista vazia.

### 5.3 Cálculo

1. Cada valor de texto é normalizado: Unicode NFC, CRLF/CR → LF e espaços removidos nas pontas.
2. Um **registro** (os campos de uma linha) une os valores com U+001E. Uma **lista** de registros une os registros com U+001D. Listas sem ordem própria (frases, respostas, faixas) são ordenadas por ID; segmentos e linhas de `exercicio_audios` seguem `ordem`, e nunca a posição da linha no CSV.
3. A entrada do hash une com U+001F: `imp-v1`, o nome (`japones`, `traducao`, `explicacao`, `resposta`, `exercicio`, `roteiro`, `selecao_audio` ou `dim:<DIMENSAO>`) e as entradas da tabela.
4. Aplica-se SHA-256 sobre os bytes UTF-8 e guarda-se o hexadecimal completo (64 caracteres).
5. Se a regra mudar, o prefixo passa a `imp-v2` e todas as impressões são recalculadas no mesmo commit.

### 5.4 Situação de uma validação e aprovação efetiva

Para cada (item, dimensão):

1. Uma validação está **vigente** quando `imp_validada` = impressão atual da dimensão **e** `arquivos_audio_resolvidos` = gravações resolvidas hoje.
2. Vale a validação vigente mais recente (maior `V-nnnn`). Se nenhuma está vigente e existe alguma, a situação é `DESATUALIZADA` e o verificador gera `VALIDACAO_DESATUALIZADA` (PENDENCIA), dizendo a gravação antiga e a atual quando foi o áudio que mudou. Se a mais recente não é a vigente (o conteúdo voltou ao de uma validação anterior), há `VALIDACAO_RECENTE_DE_OUTRA_VERSAO` (AVISO).
3. Se a validação vigente é `APROVADO` por revisor que não está na coluna "Aprovação final por", a situação é `APROVADO_AUXILIAR`.
4. Itens ativos que não têm `APROVADO` final em cada dimensão exigida geram `SEM_APROVACAO_FINAL` (PENDENCIA). As dimensões exigidas são: frase (`LINGUISTICA`, `TRADUCAO`, `PEDAGOGICA`), faixa (`ROTEIRO`), gravação `ATIVO` (`GRAVACAO`) e exercício (`PEDAGOGICA` e, se tem áudio, `ESCUTA`).
5. Um **exercício** só fica aprovado quando estão com `APROVADO` final: as dimensões dele; as das frases que usa; o `ROTEIRO` das faixas que usa; a `GRAVACAO` de cada gravação resolvida. Além disso, nenhuma gravação resolvida pode estar desatualizada em relação ao roteiro. Caso contrário, `EXERCICIO_NAO_APROVADO` lista os bloqueios.

Outras verificações:

| Situação | Código | Severidade |
|---|---|---|
| Segmento sem `imp_japones_usada` | `ROTEIRO_NAO_FECHADO` | PENDENCIA |
| `imp_japones` atual ≠ `imp_japones_usada` | `ROTEIRO_DESATUALIZADO` | PENDENCIA |
| Gravação `ATIVO` com `imp_roteiro_gerado` ≠ `imp_roteiro` atual | `GRAVACAO_DESATUALIZADA` | PENDENCIA |
| Bytes em `--raiz-audio` ≠ `sha256_arquivo` | `AUDIO_SHA_DIVERGENTE` | ERRO |
| Arquivo ausente em `--raiz-audio` | `AUDIO_AUSENTE` | AVISO |
| Verificação sem `--raiz-audio` e com gravações | `AUDIO_NAO_CONFERIDO` | AVISO |

### 5.5 Substituição de uma gravação ativa

1. A gravação nova entra como linha nova e `ATIVO`. A anterior passa a `SUBSTITUIDO` **no mesmo commit** (regra 7). Nada é apagado.
2. A gravação nova não herda validação: precisa da sua `GRAVACAO` (`SEM_APROVACAO_FINAL` até lá).
3. Exercícios `ATIVO` daquela faixa e velocidade passam a resolver para a gravação nova. As validações `PEDAGOGICA` e `ESCUTA` deles deixam de estar vigentes, e o relatório indica qual gravação foi validada e qual é a atual.
4. Exercícios `FIXO` na gravação antiga continuam com ela e com as validações vigentes, mas recebem `FIXO_SUBSTITUIDO` (AVISO). A equipe migra o exercício (o que muda `imp_exercicio`) ou registra o motivo em `observacoes`. Retirar a gravação antiga enquanto um `FIXO` a usa gera `FIXO_RETIRADO` (ERRO).
5. A validação `ROTEIRO` não é afetada, salvo quando a substituição vem de mudança de roteiro. Nesse caso, também deixam de estar vigentes `ROTEIRO` e as `PEDAGOGICA` dos exercícios que usam a faixa.

Uma regravação registrada **com o mesmo ID**, mas com bytes diferentes (`sha256_arquivo` novo), também tira a vigência de `GRAVACAO`, `PEDAGOGICA` e `ESCUTA`. Isso acontece pela impressão, não pelo ID.

## 6. Efeito de cada tipo de alteração

| Alteração | Versão que sobe | Validações que deixam de estar vigentes | Gravação desatualizada? |
|---|---|---|---|
| Japonês (texto ou furigana) | `versao_japones`; `versao_roteiro` das faixas que falam a frase | todas da frase; `ROTEIRO` das faixas; `PEDAGOGICA` dos exercícios que usam a frase ou as faixas | **sim** |
| Tradução | `versao_traducao` | `TRADUCAO` e `PEDAGOGICA` da frase; `PEDAGOGICA` dos exercícios que a usam | não |
| Explicação | `versao_explicacao` | `PEDAGOGICA` da frase e dos exercícios que a usam | não |
| Roteiro (ordem, voz, personagem, pausa, forma falada) | `versao_roteiro` | `ROTEIRO`; `PEDAGOGICA` dos exercícios que usam a faixa | **sim** |
| Seleção de áudio do exercício (faixa, velocidade, modo, gravação fixa, uso) | `versao` do exercício | `PEDAGOGICA` e `ESCUTA` do exercício | não |
| Nova gravação ativa | — | `PEDAGOGICA` e `ESCUTA` dos exercícios `ATIVO`; a nova precisa de `GRAVACAO` | — |
| Resposta (texto, tipo, rótulo, explicação) | `versao` da resposta | `PEDAGOGICA` do exercício | não |

Cada linha desta tabela tem um teste correspondente em `02_testes/test_verificar_dados.py` (ver `02_testes/COBERTURA.md`).

## 7. Comandos

```
python3 colaboracao-ia/05_ferramentas/verificar_dados.py verificar [--dados PASTA] [--raiz-audio PASTA] [--json SAIDA]
python3 colaboracao-ia/05_ferramentas/verificar_dados.py atualizar-impressoes [--dados PASTA]
python3 colaboracao-ia/05_ferramentas/verificar_dados.py fechar-roteiro A04-03 [--dados PASTA]
python3 colaboracao-ia/05_ferramentas/verificar_dados.py impressao-validacao X04-R1 PEDAGOGICA [--dados PASTA]
python3 colaboracao-ia/05_ferramentas/verificar_dados.py verificar-apontamentos [--arquivo CSV]
```

Códigos de saída de `verificar`: 0 (sem ERRO nem PENDENCIA), 1 (há ERRO), 2 (há só PENDENCIA), 3 (erro de uso). Requer Python 3.9 ou superior, só com a biblioteca padrão.

## 8. Fora deste esquema

- O verificador não julga a qualidade linguística ou pedagógica. Ele só confere se existe uma validação humana vigente e se as dependências não mudaram.
- Não há interface de edição (Google Sheets ou outra); os CSVs são editados diretamente (D-001).
- Não há verificação de PDF, diagramação ou páginas HTML contra os CSVs (ver `ESTADO.md`).
