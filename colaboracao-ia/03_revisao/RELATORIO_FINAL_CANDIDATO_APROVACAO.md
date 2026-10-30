# Relatório final · versão candidata à aprovação

```
Repositório: rha-hub/teste
Branch: colaboracao-ia/infraestrutura (PR #1)
Commit candidato: 9f4101f1a4e85648561f99924a4c79db5d3664bf
Commit base (main): ae55c1ae9afcaa2f438ef6639d63f565500d3fae
Commit anterior a esta rodada: 2623de6e378cce909161af4c3cad6c1a6cdca78e
Data e hora das execuções: 2026-10-30T03:22:31-03:00
Ambiente: Python 3.13.17 · Node v22.23.4 · clone limpo do GitHub, checkout do commit candidato
Autor: Claude (executor)
```

Este relatório entra num commit posterior ao candidato. Ele não altera código, dados nem testes. Todos os resultados abaixo foram obtidos no commit `9f4101f…`.

## 1. Declaração

**Os 12 critérios de aceitação foram atendidos** (tabela da seção 10), com as limitações da seção 7, que não escondem nenhuma falha conhecida. Esta é uma versão **candidata**: ela ainda depende da revisão independente do ChatGPT e da decisão do responsável humano. Nenhum merge foi feito.

## 2. O que foi implementado e onde

| Implementação | Arquivo | Detalhe |
|---|---|---|
| Verificador de integridade e dependências | `05_ferramentas/verificar_dados.py` | lê os 8 CSVs; confere codificação, cabeçalho, colunas, formatos, IDs, unicidade e regras 1–17; calcula as impressões SHA-256 (NFC, separadores U+001F/1E/1D, ordenação, `imp-v1`); resolve as gravações `ATIVO`/`FIXO`; detecta roteiro e gravação desatualizados, bytes trocados, validações sem vigência; aplica aprovação final por competência; calcula a aprovação efetiva de cada exercício; gera relatório em texto e JSON com códigos de saída 0/1/2/3 |
| Comandos de manutenção | o mesmo arquivo | `atualizar-impressoes` (grava impressões correntes e sobe versões), `fechar-roteiro`, `impressao-validacao` (para registrar validações corretas), `verificar-apontamentos` |
| Integridade dos originais | `05_ferramentas/verificar_originais.py` | blob de cada um dos 4 originais = blob em `main`; nenhuma alteração não commitada; o diff só toca `colaboracao-ia/` |
| Testes automatizados | `02_testes/test_verificar_dados.py` | 75 testes em 10 classes |
| Dados fictícios isolados | `02_testes/dados_ficticios.py` | capítulo 99, gerado em pasta temporária; nada vai para `01_dados/` |
| Teste de mutação | `02_testes/mutacoes.py` | 15 defeitos introduzidos, um de cada vez, com execução de controle |
| Protocolo central | `PROTOCOLO.md` | papéis, onde cada coisa fica, apontamentos e ciclo de vida, evidência obrigatória, critérios de aprovação, SHA, divergências, integridade dos registros, encerramento, privacidade |
| Instruções por papel | `instrucoes/CHATGPT_REVISOR.md`, `instrucoes/CLAUDE_EXECUTOR.md` | sem dependência de plataforma; utilizáveis como base de skills |
| Registro de apontamentos | `03_revisao/apontamentos.csv` | P01–P15, CL-01 a CL-13, validado pelo verificador |
| Decisões | `04_historico/DECISOES.md` | D-001 a D-007 |
| Estado | `ESTADO.md` | fonte única: implementado e testado / sem teste / documentado e não implementado / depende de humano / fora do escopo |
| Esquema v5 | `01_dados/ESQUEMA.md` | alinhado ao código; teste de sincronia garante isso |

## 3. O que foi corrigido nesta rodada

Achados da auditoria completa, registrados em `apontamentos.csv` como `CORRIGIDO_AGUARDA_VERIFICACAO` (commit da correção `6c24abc8e3d654e696d06297796cf10215b98ef8`):

| ID | Gravidade | Problema | Correção |
|---|---|---|---|
| CL-02 | ALTA | impressões, dependências e regras só existiam na documentação | `verificar_dados.py` |
| CL-03 | ALTA | sem testes automatizados das regras e invalidações | suíte, dados fictícios, mutação, sincronia |
| CL-04 | ALTA | validações não identificavam o revisor humano nem sua competência; aprovação de IA podia parecer final | `revisor` por competência, `revisor_identificacao`, `APROVADORES_FINAIS`, `APROVADO_AUXILIAR` |
| CL-05 | MEDIA | cálculo das impressões ambíguo; rótulo da resposta, degrau e seção ficavam fora | `ESQUEMA.md` 5.1–5.3 com entradas exatas |
| CL-06 | MEDIA | sem regra para gravar impressões e subir versões; sem "fechar roteiro" | `atualizar-impressoes`, `fechar-roteiro` |
| CL-07 | MEDIA | regras derivadas ausentes | regras 12–16 |
| CL-08 | MEDIA | decisões não registradas; velocidades do piloto não documentadas | `DECISOES.md`; `100` e `080` |
| CL-09 | MEDIA | README dizia que o verificador não existia e mandava mover o histórico | README virou índice; nada é movido |
| CL-10 | BAIXA | CHANGELOG sem o commit `2623de6…` | linha 8 da sequência |
| CL-11 | MEDIA | protocolo disperso, sem instruções por IA nem registro central | `PROTOCOLO.md`, `instrucoes/`, `apontamentos.csv` |
| CL-12 | MEDIA | integridade dos originais não verificada automaticamente | `verificar_originais.py` + teste |
| CL-13 | MEDIA | áudio comercial não pode ficar no repositório público | conferência de bytes por `--raiz-audio` |

Também foram implementados os pontos que antes só estavam especificados: P13 (gravação efetivamente usada), P14 (tomada e unicidade) e P03/P08 (impressões e dependências).

Problemas encontrados **durante** a construção dos testes e corrigidos antes do commit:
- O teste de mutação dava falsos positivos: ele não copiava `03_revisao/`, e um teste falhava em toda mutação. Foi acrescentada uma execução de controle que aborta se a suíte não passar sem mutação.
- Duas mutações sobreviveram na primeira versão. Uma era equivalente (o campo `ordem` dentro do registro) e foi trocada. A outra mostrou que faltava um teste para bytes regravados com o mesmo ID (`test_06b`), que foi criado. Uma terceira revelou a falta do teste de ordem das linhas no CSV (`test_05b`).
- Um teste novo de cobertura de códigos acusou um falso positivo (a severidade `PENDENCIA` lida como código), corrigido no próprio teste.

## 4. Resultados

| # | Comando | Saída | Resultado |
|---|---|---|---|
| 1 | `python3 -m unittest discover -s colaboracao-ia/02_testes -p 'test_*.py' -v` | `Ran 75 tests` · `OK` | 75 aprovados, 0 falhas, 0 erros, 0 pulados (o teste dos originais rodou, porque o clone tem a base) |
| 2 | `python3 colaboracao-ia/02_testes/mutacoes.py` | `controle: suíte passa na cópia sem mutação` · `15 de 15 mutações detectadas` | código 0 |
| 3 | `python3 colaboracao-ia/05_ferramentas/verificar_dados.py verificar` (CSVs oficiais, só cabeçalhos) | `ERRO: 0 · PENDENCIA: 0 · AVISO: 0` | código 0 |
| 4 | `… verificar_dados.py verificar-apontamentos` | 28 linhas · `ERRO: 0 · PENDENCIA: 0 · AVISO: 0` | código 0 |
| 5 | `python3 colaboracao-ia/05_ferramentas/verificar_originais.py` | 4 × `OK` · 35 arquivos alterados, 0 fora de `colaboracao-ia/` · `ÍNTEGRO` | código 0 |
| 6 | `git diff --name-status ae55c1a… 9f4101f…` | 35 arquivos, todos `A` (adicionados), todos em `colaboracao-ia/` | — |

Testes por classe:

| Classe | Testes | Conteúdo |
|---|---|---|
| `CenariosObrigatorios` | 28 | os 15 cenários obrigatórios e variações |
| `EstruturaEArquivos` | 14 | cabeçalho, BOM, CRLF, listas, capítulos, retiradas, velocidades, bytes, roteiro |
| `CodigosRestantes` | 9 | demais códigos de achado |
| `RevisoresEValidacoes` | 7 | IA auxiliar, competência, identificação, dimensões |
| `Apontamentos` | 5 | regras do protocolo e registro oficial |
| `EstadoValido` | 4 | estado aprovado, CSVs oficiais, impressões |
| `LinhaDeComando` | 3 | códigos de saída, `impressao-validacao`, JSON |
| `SincroniaEsquemaCodigo` | 3 | esquema × CSVs × código |
| `CoberturaDosCodigos` | 1 | todo código de achado tem teste |
| `Originais` | 1 | integridade dos 4 originais |

Mutações detectadas (defeito → primeiro teste que falhou):

| Defeito introduzido | Detectado por |
|---|---|
| tradução entra no roteiro | `test_01_traducao_nao_invalida_audio` |
| seleção de áudio ignora os bytes do arquivo | `test_06b_bytes_regravados_no_mesmo_id_invalidam_validacoes` |
| pedagógica da frase ignora a explicação | `test_02_explicacao_nao_invalida_audio_nem_traducao` |
| pedagógica do exercício ignora a gravação usada | `test_06b_bytes_regravados_no_mesmo_id_invalidam_validacoes` |
| não detecta gravação com roteiro desatualizado | `test_03_texto_japones_invalida_roteiro_e_gravacoes` |
| sem a regra 2 | `test_14_exercicio_sem_resposta_correta` |
| `atualizar-impressoes` não sobe a versão | `test_01_traducao_nao_invalida_audio` |
| permite duas gravações ativas | `test_12_duas_gravacoes_ativas_mesma_faixa_e_velocidade` |
| aprovação de IA conta como final | `test_aprovacao_de_ia_e_apenas_auxiliar` |
| regra 6 não confere a tomada | `test_11b_identificador_de_arquivo_com_tomada_incoerente` |
| modo `ATIVO` não resolve a gravação | `test_01_traducao_nao_invalida_audio` |
| `FIXO` aceita outra velocidade | `test_08c_fixo_com_velocidade_diferente_e_erro` |
| validação desatualizada continua valendo | `test_01_traducao_nao_invalida_audio` |
| japonês ignora a forma reduzida | `test_03_texto_japones_invalida_roteiro_e_gravacoes` |
| segmentos não ordenados por `ordem` | `test_05b_ordem_das_linhas_no_csv_nao_importa` |

## 5. Evidência das invalidações (linha de comando, dados fictícios)

Gerada com o verificador do commit `6c24abc…`, cujo `verificar_dados.py` é idêntico ao do candidato (blob `1ea59316533e44525b45a662b973cc8f1fe8c1a5` nos dois). Abaixo, um trecho representativo das saídas.

**Estado aprovado:** código 0; `X99-E1`, `X99-E2` e `X99-M1` com `APROVADO (final)`.

**Só a tradução de `J99-01` muda** → `atualizar-impressoes`: `versao_traducao → 2`. `verificar`: código 2, 7 pendências.
```
[VALIDACAO_DESATUALIZADA] validacoes (J99-01, TRADUCAO): V-0002 (APROVADO) não vale mais
[VALIDACAO_DESATUALIZADA] validacoes (J99-01, PEDAGOGICA): V-0003 (APROVADO) não vale mais
[VALIDACAO_DESATUALIZADA] validacoes (X99-E1, PEDAGOGICA): V-0010 (APROVADO) não vale mais
[VALIDACAO_DESATUALIZADA] validacoes (X99-M1, PEDAGOGICA): V-0014 (APROVADO) não vale mais
X99-E1: NÃO APROVADO · X99-E2: APROVADO (final) · X99-M1: NÃO APROVADO
```
Nenhuma linha `GRAVACAO_DESATUALIZADA`, `ROTEIRO_DESATUALIZADO`, `LINGUISTICA` ou `ESCUTA`: a tradução não afetou o áudio.

**Gravação ativa substituída** (`A99-01` a 100%, t1 → t2): código 2, 4 pendências.
```
[VALIDACAO_DESATUALIZADA] validacoes (X99-E1, PEDAGOGICA): V-0010 (APROVADO) não vale mais: a gravação usada mudou: validada com ['A99-01_v100_r1_t1'], hoje resolve para ['A99-01_v100_r1_t2']
[VALIDACAO_DESATUALIZADA] validacoes (X99-E1, ESCUTA): V-0011 (APROVADO) não vale mais: a gravação usada mudou: …
[SEM_APROVACAO_FINAL] gravação A99-01_v100_r1_t2: GRAVACAO: SEM_VALIDACAO
X99-E1: NÃO APROVADO · X99-E2 (FIXO, 80%): APROVADO (final) · X99-M1: APROVADO (final)
```

**Japonês (forma reduzida) de `J99-01` muda** → `atualizar-impressoes`: `versao_japones → 2`, `versao_roteiro → 2`. `verificar`: código 2, 15 pendências, entre elas:
```
[ROTEIRO_DESATUALIZADO] audio_segmentos.csv:2 (A99-01#1): o japonês de `J99-01` mudou depois que o roteiro de `A99-01` foi fechado
[GRAVACAO_DESATUALIZADA] arquivos_audio.csv:2 (A99-01_v100_r1_t1): … gravar de novo
[GRAVACAO_DESATUALIZADA] arquivos_audio.csv:3 (A99-01_v080_r1_t1): … gravar de novo
[VALIDACAO_DESATUALIZADA] validacoes (A99-01, ROTEIRO): V-0007 (APROVADO) não vale mais
[EXERCICIO_NAO_APROVADO] exercício X99-E2: … gravação usada A99-01_v080_r1_t1: desatualizada em relação ao roteiro
X99-E1: NÃO APROVADO · X99-E2: NÃO APROVADO · X99-M1: NÃO APROVADO
```
A validação `GRAVACAO` dos arquivos continua vigente (os bytes não mudaram), mas os exercícios ficam bloqueados porque a gravação está desatualizada em relação ao roteiro. Esse é o comportamento especificado em `ESQUEMA.md` 5.4.

## 6. O que permanece pendente

Detalhado em `ESTADO.md`, seções 3 e 4:

- **Verificação independente** de CL-02 a CL-13, P01–P06, CL-01 e P13–P15 (todos `CORRIGIDO_AGUARDA_VERIFICACAO`). Só P07, P09, P10, P11 e P12 estão `VERIFICADO`.
- **Confirmação de D-006** pelo responsável humano (quem dá aprovação final em cada dimensão).
- **Decisões humanas:** merge do PR; indicação do revisor de japonês; correção do link de `docs/index.html` (arquivo original); licenças do serviço de voz e dos elementos do Canva.
- **Não implementados** (documentados como tal): teste HTML guiado por `respostas.csv`; comparação de HTML/PDF com `frases.csv`; testes de PDF; comparação automática entre transcrição e roteiro; exigir que `SUPERADO` cite o ID substituto.

## 7. Limitações reais

1. O verificador **não julga** a qualidade do japonês, da tradução nem da pedagogia. Ele só garante que existe validação humana vigente e que nada mudou depois dela.
2. Os testes usam **dados e áudios fictícios**. Nenhum MP3 real foi conferido, e os CSVs oficiais estão vazios: o comportamento com conteúdo real ainda não foi exercitado.
3. `teste-html-smoke.js` **não foi reexecutado** nesta rodada (o script não mudou) e não tem teste automatizado próprio. Suas execuções registradas estão em `COBERTURA.md`, parte B.
4. O caminho de **falha** de `verificar_originais.py` não é testado; só o de sucesso.
5. `imp_japones` cobre as duas formas da frase. Mudar a forma completa também desatualiza o roteiro de uma faixa que fala só a reduzida. É uma escolha conservadora e documentada, que pode gerar regravações desnecessárias.
6. Os commits revisados nas revisões 1 a 3 são **presumidos** (head da branch na ocasião), porque os relatórios do ChatGPT nunca foram gravados no repositório. Isso está anotado em `apontamentos.csv`.
7. D-006 é uma **proposta do executor** a partir de D-005, ainda não confirmada pelo responsável humano.
8. O teste dos originais é pulado fora de um repositório git com a base disponível. No clone usado aqui, ele rodou.

## 8. Arquivos e commits

Commits desta rodada (SHA completo):

| Commit | Conteúdo |
|---|---|
| `6c24abc8e3d654e696d06297796cf10215b98ef8` | verificador, testes, mutação, protocolo, instruções, decisões, estado, esquema v5, README, COBERTURA, CHANGELOG |
| `9f4101f1a4e85648561f99924a4c79db5d3664bf` | **candidato**: testes de sincronia esquema × código, tabela regra × teste, apontamentos CL-02 a CL-13 atualizados |
| (este relatório) | registrado no comentário do PR #1 |

**Adicionados nesta rodada** (blob no candidato):

| Arquivo | Blob |
|---|---|
| `colaboracao-ia/05_ferramentas/verificar_dados.py` | `1ea59316533e44525b45a662b973cc8f1fe8c1a5` |
| `colaboracao-ia/05_ferramentas/verificar_originais.py` | `f654b947d8d44ccb8b6d5cfb9c60ff1dc4157f85` |
| `colaboracao-ia/02_testes/test_verificar_dados.py` | `d8f7a36a244854d805200286047c07e7276a7d5a` |
| `colaboracao-ia/02_testes/dados_ficticios.py` | `a6dd5d9b9120f98d670ef911a2c024a7fba2d621` |
| `colaboracao-ia/02_testes/mutacoes.py` | `a2c49b43686ad90138f7ae353304062c4226a4c2` |
| `colaboracao-ia/PROTOCOLO.md` | `b443c89acce3be14e71b33c5b170f302650936b3` |
| `colaboracao-ia/ESTADO.md` | `40903c7fc694cbc84a5a3da6c9c5cc47a1d32d29` |
| `colaboracao-ia/instrucoes/CHATGPT_REVISOR.md` | `82d096880b1b45847461dc678763b0c7c33fd59f` |
| `colaboracao-ia/instrucoes/CLAUDE_EXECUTOR.md` | `0b0d62822eb605c927434fd68415d9eddd9878e0` |
| `colaboracao-ia/03_revisao/apontamentos.csv` | `86aae6ab44386be7d9f1c5e2db8b7185dece344a` |
| `colaboracao-ia/04_historico/DECISOES.md` | `a39ffe90681790549689c4c04636658a0e263a11` |

**Alterados nesta rodada:**

| Arquivo | Blob |
|---|---|
| `colaboracao-ia/01_dados/ESQUEMA.md` | `f0089d9ca6d11ea8a2eb3df5ca1524f8474c6789` |
| `colaboracao-ia/01_dados/validacoes.csv` | `4a35d98c8b54b5648f8c551901d3bcf3dbd39344` |
| `colaboracao-ia/02_testes/COBERTURA.md` | `f630494c541ac8fe451423d79d003dd775425bb7` |
| `colaboracao-ia/README.md` | `0c09c743fcce3737c18909c39bc201b5749c41a5` |
| `colaboracao-ia/04_historico/CHANGELOG.md` | `3f111829a1edd3b00c69913a044b97722c03ada6` |
| `colaboracao-ia/.gitignore` | `612369eb472e51a4439694d10a33177a5080e78e` |

**Preservados sem alteração:** os 4 arquivos originais; todos os documentos de revisão anteriores (`REVISAO_SOLICITADA.md`, `RESPOSTA_CLAUDE*.md`, `NOVA_REVISAO_SOLICITADA*.md` e os 3 relatórios `.json`); `02_testes/teste-html-smoke.js`; os 7 CSVs oficiais além de `validacoes.csv` (só cabeçalhos).

## 9. Integridade dos arquivos originais

| Arquivo | Blob em `main` (`ae55c1a…`) | Blob no candidato | |
|---|---|---|---|
| `O Japonês que Encolhe.html` | `e9ba45b4fb3c00074f6ec80162d4a900280f7146` | igual | OK |
| `paginas-modelo.html` | `2a7eda7b13c243abf257a40be8997e5add574561` | igual | OK |
| `docs/index.html` | `1826247758d0a524c55afe208b09ba387aba9a49` | igual | OK |
| `docs/Páginas-modelo · Cap. 4 · A tinta e carimbo  B educacional limpo (1).pdf` | `4f255ddcfb1298f17d92f4ecc309f9fe8ad304a2` | igual | OK |

`main` continua em `ae55c1ae9afcaa2f438ef6639d63f565500d3fae`. Os 35 arquivos do diff `main…candidato` estão todos em `colaboracao-ia/`.

## 10. Critérios de aceitação

| # | Critério | Atendido | Evidência |
|---|---|---|---|
| 1 | Verificador Python implementado e executável | sim | seção 4, linhas 3 e 4; `LinhaDeComando` |
| 2 | Hashes e dependências conforme a especificação | sim | `ESQUEMA.md` 5.1–5.4 = código (`SincroniaEsquemaCodigo`); cenários 1–15; mutações |
| 3 | Testes cobrem todos os cenários obrigatórios | sim | `COBERTURA.md` A2 (15 cenários) e A2b (17 regras) |
| 4 | Testes demonstram as invalidações | sim | `assertSoDesatualizadas` exige exatamente as invalidações esperadas; seção 5; 15/15 mutações |
| 5 | Sem inconsistências entre CSVs, esquema e código | sim | `SincroniaEsquemaCodigo` (3 testes) e `test_csvs_oficiais_vazios_sao_validos` |
| 6 | Protocolo compartilhado documentado | sim | `PROTOCOLO.md`; regras impostas por `verificar-apontamentos` |
| 7 | Instruções de cada IA prontas | sim | `instrucoes/CHATGPT_REVISOR.md`, `instrucoes/CLAUDE_EXECUTOR.md` |
| 8 | Documentação sincronizada | sim | `ESTADO.md` como fonte única; busca por afirmações antigas fora dos documentos históricos sem resultado; teste de sincronia |
| 9 | Teste de integridade confirma os originais | sim | seção 9; `verificar_originais.py` código 0 |
| 10 | Resultados de todos os testes executados registrados | sim | seção 4 (os 6 comandos, com saída e código) |
| 11 | Nenhuma limitação escondida | sim | seção 7 e `ESTADO.md` seções 2 a 4 |
| 12 | PR atualizado e descrição fiel | sim | descrição do PR #1 atualizada depois deste commit |

**Conclusão:** a infraestrutura está **pronta para a revisão independente final do ChatGPT**. A aprovação depende dessa revisão, da confirmação de D-006 e da decisão do responsável humano. Nenhum merge foi feito.
