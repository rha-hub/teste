# Cobertura dos testes

Este arquivo diz exatamente o que cada teste verifica, o que **não** verifica e quais execuções aconteceram. O status geral (implementado, pendente, fora do escopo) fica em `../ESTADO.md`.

- **Parte A**: verificador de dados (`05_ferramentas/verificar_dados.py`) e integridade dos originais. Testes automatizados (`unittest`) com dados fictícios isolados.
- **Parte B**: teste de fumaça de páginas HTML (`teste-html-smoke.js`, Playwright), executado manualmente.

## Parte A · Verificador de dados

### A1. Como os testes funcionam

- `dados_ficticios.py` gera, numa pasta temporária, um conjunto **fictício** com capítulo 99, 2 frases, 3 exercícios (2 de escuta, 1 de múltipla escolha), 5 respostas, 1 faixa com 2 segmentos, 2 gravações (`100` ativa e `080` usada em modo `FIXO`) e 14 validações humanas vigentes. Os "áudios" são pequenos arquivos de texto. Nada disso entra em `01_dados/`.
- Cada teste parte desse estado aprovado (código 0, nenhum achado), muda **uma** coisa e confere o efeito exato: quais validações perdem a vigência, quais **não** perdem, se a gravação fica desatualizada e se o exercício continua aprovado.
- `assertSoDesatualizadas` exige que **só** as validações esperadas percam a vigência e que todas as outras continuem `APROVADO`. Isso detecta tanto a falta de invalidação quanto o excesso.

### A2. Cenários obrigatórios

| Nº | Cenário | Teste(s) | Efeito verificado |
|---|---|---|---|
| 1 | Só a tradução muda | `test_01_traducao_nao_invalida_audio` | perdem a vigência: `TRADUCAO` e `PEDAGOGICA` da frase e `PEDAGOGICA` dos 2 exercícios que a usam. Continuam vigentes: `LINGUISTICA`, `ROTEIRO`, `GRAVACAO`, `ESCUTA`. Nenhuma gravação desatualizada. `versao_traducao` sobe para 2, `versao_japones` fica em 1 |
| 2 | Só a explicação muda | `test_02_explicacao_nao_invalida_audio_nem_traducao` | perdem a vigência: `PEDAGOGICA` da frase e dos 2 exercícios. Áudio e tradução intactos. `versao_explicacao` sobe para 2 |
| 3 | Texto japonês muda | `test_03_texto_japones_invalida_roteiro_e_gravacoes` | perdem a vigência as 3 validações da frase, `ROTEIRO` e `PEDAGOGICA` dos 3 exercícios. `ROTEIRO_DESATUALIZADO` só no segmento 1. As 2 gravações ficam desatualizadas e o exercício de escuta fica bloqueado. `versao_roteiro` sobe para 2 |
| 4 | Furigana muda | `test_04_furigana_e_mudanca_no_japones`, `test_04b_furigana_malformada_e_erro` | a leitura é tratada como japonês (roteiro e gravações desatualizados); furigana malformada é ERRO |
| 5 | Ordem dos segmentos muda | `test_05_ordem_dos_segmentos_invalida_roteiro_nao_frases`, `test_05b_ordem_das_linhas_no_csv_nao_importa` | perdem a vigência só `ROTEIRO` e a `PEDAGOGICA` dos exercícios com a faixa; as frases ficam intactas. Reordenar **linhas** do CSV sem mudar `ordem` não muda nada |
| 6 | Gravação ativa substituída | `test_06_substituir_gravacao_ativa`, `test_06b_bytes_regravados_no_mesmo_id_invalidam_validacoes` | o exercício `ATIVO` passa a usar a gravação nova; perdem a vigência só a `PEDAGOGICA` e a `ESCUTA` dele, e a mensagem diz qual gravação foi validada e qual é a atual. A gravação nova fica sem aprovação. O exercício `FIXO` não é afetado. Depois de validar de novo, o código volta a 0. Bytes regravados com o mesmo ID também tiram a vigência (pela impressão) |
| 7 | Velocidade do exercício muda | `test_07_mudar_velocidade_do_exercicio`, `test_07b_mudar_velocidade_sem_atualizar_impressao_e_erro` | resolve para a gravação `080`; perdem a vigência só `PEDAGOGICA` e `ESCUTA` do exercício; `versao` sobe. Sem `atualizar-impressoes`, é ERRO |
| 8 | Modo `FIXO` | `test_08_*`, `test_08b_*`, `test_08c_*`, `test_08d_*` | mantém a gravação quando outra vira ativa (validações continuam vigentes, com aviso). Gravação `RETIRADO`, velocidade diferente, `FIXO` sem arquivo e `ATIVO` com arquivo dão ERRO |
| 9 | Modo `ATIVO` | `test_estado_aprovado_sem_achados`, `test_09_ativo_sem_gravacao_ativa_e_erro` | resolve para a gravação ativa; sem gravação ativa, é ERRO e o exercício fica bloqueado |
| 10 | Referência a gravação inexistente | `test_10_gravacao_inexistente`, `test_10b_*`, `test_10c_*` | ERRO para gravação, item de validação, frase de exercício e frase de segmento inexistentes |
| 11 | Identificador duplicado | `test_11_identificadores_duplicados`, `test_11b_*`, `test_11c_*` | ERRO para frase e gravação duplicadas, ID de gravação incoerente com a tomada e formato inválido |
| 12 | Duas gravações ativas na mesma faixa e velocidade | `test_12_duas_gravacoes_ativas_mesma_faixa_e_velocidade` | ERRO `MAIS_DE_UM_ATIVO` |
| 13 | Gravação com roteiro desatualizado | `test_13_gravacao_com_roteiro_desatualizado`, `test_13b_gravacao_futura_e_erro` | as 2 gravações ficam desatualizadas, o código é 2, os exercícios de escuta ficam bloqueados e o de múltipla escolha continua aprovado; versão de roteiro futura é ERRO |
| 14 | Exercício sem resposta correta | `test_14_exercicio_sem_resposta_correta` | ERRO `SEM_RESPOSTA_CORRETA`; a `PEDAGOGICA` perde a vigência |
| 15 | Validação antiga após mudança de dependência | `test_15_validacao_antiga_nao_continua_aprovada`, `test_15b_reverter_conteudo_reativa_validacao_antiga_com_aviso` | a validação antiga fica no arquivo, mas não vale; o exercício perde a aprovação; uma nova validação restaura o código 0. Se o conteúdo volta ao anterior, a validação antiga volta a valer, com aviso |

### A2b. Regras de integridade × testes

| Regra (`ESQUEMA.md` seção 3) | Teste(s) |
|---|---|
| 1 referências | `test_10_gravacao_inexistente`, `test_10b_validacao_de_item_inexistente`, `test_10c_frase_inexistente_em_exercicio_e_segmento` |
| 2 resposta correta | `test_14_exercicio_sem_resposta_correta` |
| 3 segmentos e ordem | `test_faixa_sem_segmentos`, `test_buraco_na_ordem_dos_segmentos` |
| 4 item retirado | `test_referencia_a_item_retirado`, `test_08b_fixo_para_gravacao_retirada_e_erro` |
| 5 capítulo posterior | `test_frase_de_capitulo_posterior` |
| 6 ID da gravação (inclui tomada) | `test_11b_identificador_de_arquivo_com_tomada_incoerente`, `test_11c_formato_de_identificador_de_arquivo` |
| 7 uma gravação ativa | `test_12_duas_gravacoes_ativas_mesma_faixa_e_velocidade` |
| 8 unicidade | `test_11_identificadores_duplicados` |
| 9 coerência de `FIXO`/`ATIVO` | `test_08c_fixo_com_velocidade_diferente_e_erro`, `test_08d_fixo_sem_arquivo_e_ativo_com_arquivo_sao_erros` |
| 10 gravação ativa disponível | `test_09_ativo_sem_gravacao_ativa_e_erro` |
| 11 `FIXO` substituído / retirado | `test_08_fixo_mantem_gravacao_quando_outra_vira_ativa`, `test_08b_fixo_para_gravacao_retirada_e_erro` |
| 12 escuta sem áudio | `test_escuta_sem_audio` |
| 13 forma reduzida inexistente | `test_segmento_reduzido_de_frase_sem_reducao` |
| 14 versão futura | `test_13b_gravacao_futura_e_erro` |
| 15 capítulo do ID, prefixo da resposta | `test_capitulo_do_id_coerente`, `test_prefixo_da_resposta` |
| 16 furigana | `test_04b_furigana_malformada_e_erro` |
| 17 validações | `test_humano_sem_identificacao_e_erro`, `test_dimensao_incompativel_com_item`, `test_lista_de_gravacoes_resolvidas_obrigatoria`, `test_resolvidos_indevido` |

A classe `SincroniaEsquemaCodigo` falha se uma coluna, um valor fixo, uma dimensão ou a versão do esquema estiver no código e não em `ESQUEMA.md`, ou se os CSVs oficiais tiverem cabeçalho diferente do código.

Casos válidos: `test_estado_aprovado_sem_achados`, `test_csvs_oficiais_vazios_sao_validos`, `test_05b_ordem_das_linhas_no_csv_nao_importa`, `test_atualizar_impressoes_nao_muda_nada_no_estado_aprovado`, `test_08_fixo_mantem_gravacao_quando_outra_vira_ativa`, `Apontamentos.test_valido`, `Apontamentos.test_registro_oficial_e_valido`.

Outras classes:
- `RevisoresEValidacoes`: aprovação de IA como auxiliar e competência por dimensão.
- `EstruturaEArquivos` e `CodigosRestantes`: cabeçalho, BOM, CRLF, listas, capítulos, retiradas, velocidades, bytes de áudio, roteiro não fechado e demais códigos.
- `LinhaDeComando`: códigos de saída 0/1/2/3, `impressao-validacao` e JSON.
- `Apontamentos`: regras do protocolo.
- `CoberturaDosCodigos`: falha se algum código de achado do verificador não aparece em nenhum teste.
- `Originais`: integridade dos 4 arquivos originais. É pulado fora de um repositório git; por isso é pulado dentro das cópias temporárias do teste de mutação.

### A3. Teste de mutação

`mutacoes.py` primeiro roda a suíte numa cópia sem mutação (controle) e só continua se ela passar. Depois introduz, uma de cada vez, 15 defeitos no verificador e exige que a suíte falhe em cada um.

Duas lições da construção desse teste ficaram registradas:
- Retirar o campo `ordem` de dentro do registro do segmento é uma mutação **equivalente**: os segmentos já são ordenados antes do cálculo. Ela foi trocada por "não ordenar os segmentos", que só o `test_05b` detecta.
- Sem a cópia de `03_revisao/`, o teste do registro oficial de apontamentos falhava em toda mutação, e todas pareciam detectadas por engano. A execução de controle impede isso.

### A4. O que a Parte A não verifica

- A qualidade do conteúdo: o verificador confere a existência e a vigência de validações humanas, não se o japonês, a tradução ou a pedagogia estão bons.
- Arquivos MP3 reais: os testes usam bytes fictícios.
- O caminho de falha de `verificar_originais.py` (só o de sucesso é testado).
- Desempenho com volumes grandes de dados.

### A5. Execuções registradas

Os resultados de cada execução, com o commit exato, estão em `03_revisao/RELATORIO_FINAL_CANDIDATO_APROVACAO.md`, seção "Resultados".

## Parte B · Teste de fumaça HTML (`teste-html-smoke.js`, versão 3)

Um resultado "sem falhas" significa só que os itens da primeira tabela passaram. Ele não diz que o material está correto.

### Reação observável não é funcionamento correto

O teste clica nos botões e registra se **algo mudou** depois do clique: mudança no DOM, chamada de `play()` em áudio, escrita no armazenamento local ou mudança de endereço. Isso se chama **reação observável**.

Reação observável **não prova** que o botão faz o que deveria. Uma mudança no DOM pode ser a mensagem "errado!" aparecendo depois de uma resposta certa. A chamada de `play()` pode carregar o arquivo errado ou um arquivo inexistente. Só um teste que conheça o resultado esperado de cada botão (por exemplo, guiado por `respostas.csv`) verifica funcionamento.

Os cliques são feitos em sequência, sem recarregar a página, e o estado se acumula. Por isso o relatório separa:

- **desabilitado desde o carregamento**: o botão já estava desabilitado antes de qualquer clique do teste;
- **desabilitado após interações anteriores**: o botão estava habilitado no carregamento, mas foi desabilitado durante o teste. Isso pode ter sido causado por um clique anterior do próprio teste, como as alternativas bloqueadas depois que uma resposta da mesma questão é escolhida. O teste não registra qual clique causou o bloqueio.

### O que é verificado

| Verificação | Como | Tela | Resultado |
|---|---|---|---|
| Erros de script | evento `pageerror` do navegador | computador e celular | falha |
| Arquivos locais ausentes (áudio, imagem, CSS, PDF) | requisições `file:` que falharam | computador e celular | falha |
| Recursos externos que não carregaram (fontes, CDN) | requisições `http(s):` que falharam | computador e celular | aviso (pode ser bloqueio de rede do ambiente) |
| Rolagem horizontal | `scrollWidth − clientWidth` | 1280 px e 390 px | aviso |
| Japonês sem `lang="ja"` | cada nó de texto com kana ou kanji, procurando `lang` no ancestral mais próximo | computador | aviso |
| Idioma do documento | atributo `lang` de `<html>` | computador | registrado |
| Botões sem nome acessível | texto, `aria-label`, `aria-labelledby` ou `title` | computador | aviso |
| Imagens sem `alt`, campos sem rótulo | atributos e `<label>` | computador | aviso |
| Links internos (`#âncora`) quebrados | o `id` de destino existe | computador | falha |
| Reação observável aos cliques | um clique em cada botão visível e habilitado; registra os sinais acima | computador | registrado por botão; **não** é falha nem aprovação |
| Estado dos botões não clicados | oculto; desabilitado desde o carregamento; desabilitado após interações; destrutivo | computador | registrado por botão |
| Caixas de diálogo | fechadas automaticamente e contadas | computador e celular | registrado |
| Origem do arquivo testado | SHA-256 do arquivo; se estiver num repositório git: caminho relativo à raiz, commit (40 caracteres), blob e se há alteração não commitada | — | registrado |
| Capturas de tela | uma por tela, para revisão humana | computador e celular | arquivo |

Botões com termos como "apagar", "reset", "limpar" ou classe `danger` no texto, no `id` ou na classe **não** são clicados, para não apagar dados.

### O que não é verificado

| Fora da cobertura | Por quê / como cobrir |
|---|---|
| Se cada botão faz a coisa **certa** | o teste só observa que algo mudou; exige resultado esperado por botão |
| Se o feedback de um exercício está certo (acerto marcado como acerto) | o teste não conhece as respostas; exige uma versão guiada por `respostas.csv` |
| Todas as alternativas de cada exercício | o estado se acumula; depois do primeiro clique numa questão, as outras alternativas costumam ficar desabilitadas e não são clicadas |
| Se o áudio **toca** e se o conteúdo falado está certo | o teste vê a chamada de `play()`, não o som; conteúdo exige transcrição comparada ao roteiro |
| Se o texto da página é igual à versão aprovada | exige comparação com `frases.csv` |
| Qualidade visual, alinhamento do furigana, hierarquia | as capturas são para olho humano; nada é comparado automaticamente |
| Contraste de cores, navegação por teclado, leitor de tela | não implementado |
| Safari/WebKit, Firefox, aparelhos reais | só Chromium, em tela simulada |
| Persistência após recarregar a página | não implementado |
| PDF | fora do escopo deste script |

### Execuções registradas

Só entram aqui execuções que de fato aconteceram, com o SHA completo do que foi testado. Os números das execuções antigas não foram alterados; só a terminologia das linhas de detalhe segue a versão 3.

| Data | Script | Arquivo testado | Commit do repositório | Blob do arquivo | SHA-256 do arquivo | Resultado |
|---|---|---|---|---|---|---|
| 2026-10-30T02:36:35-03:00 | v3 | `O Japonês que Encolhe.html` | `cd08f0da92f994157fb1a55f2fb9080924dd427f` | `e9ba45b4fb3c00074f6ec80162d4a900280f7146` | `4a81cb50622b20dd12725839dbb9d19f26aeb1bf92d0a725e73063dc730f830e` | 2 falhas, 1 aviso (detalhe A) |
| 2026-10-30T02:36:52-03:00 | v3 | `docs/index.html` | `cd08f0da92f994157fb1a55f2fb9080924dd427f` | `1826247758d0a524c55afe208b09ba387aba9a49` | `e1e94ea108c32cdf15d468598bd7f9af5c465eb97a1962e989359783f7641e43` | 2 falhas (detalhe B) |
| 2026-10-30T02:27:39-03:00 | v2 | `O Japonês que Encolhe.html` | `e822d76fb83aced40c840e5915780ef412c0cd35` | `e9ba45b4fb3c00074f6ec80162d4a900280f7146` | `4a81cb50622b20dd12725839dbb9d19f26aeb1bf92d0a725e73063dc730f830e` | 2 falhas, 1 aviso (mesmos números do detalhe A) |
| 2026-10-30 (pedido da rodada 01) | v1 | cópia local do demo do Cap. 4, **não** o arquivo do repositório | — | — | — | ver `03_revisao/REVISAO_SOLICITADA.md` |

Em todas as execuções acima, o arquivo testado não tinha alteração não commitada. O commit do repositório muda de `e822d76…` para `cd08f0d…` porque o teste foi executado em momentos diferentes da branch. O conteúdo do arquivo é o mesmo nos dois casos (blob e SHA-256 idênticos).

**Detalhe A**, `O Japonês que Encolhe.html` (v3; a execução v2 deu os mesmos números):

- **Falhas:** 5 arquivos MP3 locais ausentes (`formal.mp3`, `casual.mp3`, `dlg_a1.mp3`, `dlg_b.mp3`, `dlg_a2.mp3`), no computador e no celular. O repositório não tem a pasta de áudio.
- **Aviso:** 159 de 159 trechos em japonês sem `lang="ja"`; `<html>` sem `lang`.
- Sem erros de script, sem rolagem horizontal (1280 px e 390 px), sem links internos quebrados, sem botões, imagens ou campos sem nome.
- **Cliques** (60 botões):
  - 40 clicados, todos com reação observável: 29 com mudança no DOM e escrita no armazenamento, 11 só no DOM. Isso não diz se reagiram corretamente.
  - 5 desabilitados desde o carregamento: os botões de ouvir. A causa provável é a falta dos MP3; o teste não registra a causa.
  - 12 desabilitados após interações anteriores: alternativas de exercício. A causa provável é o teste ter clicado antes em outra alternativa da mesma questão.
  - 3 não clicados por serem destrutivos: "Apagar meu progresso", "Sim, apagar" e "Cancelar". Este último foi pulado porque seu `id` contém "reset".

**Detalhe B**, `docs/index.html` (v3; primeira execução do teste neste arquivo):

- **Falha:** 1 arquivo local ausente, no computador e no celular: o PDF que o `iframe` procura na raiz do repositório. Isso confirma, por execução, o link quebrado já apontado por leitura do código no pedido da rodada 01. O arquivo **não** foi corrigido, por falta de autorização para alterar os arquivos originais.
- A página não tem botões.

Os relatórios citados estão em `03_revisao/teste-html_20261030-*.json`.
