# Cobertura do teste de HTML (`teste-html-smoke.js`, versão 3)

Este arquivo diz exatamente o que o teste verifica e o que ele **não** verifica. Um resultado "sem falhas" significa só que os itens da primeira tabela passaram. Ele não diz que o material está correto.

## Reação observável não é funcionamento correto

O teste clica nos botões e registra se **algo mudou** depois do clique: mudança no DOM, chamada de `play()` em áudio, escrita no armazenamento local ou mudança de endereço. Isso se chama **reação observável**.

Reação observável **não prova** que o botão faz o que deveria. Uma mudança no DOM pode ser a mensagem "errado!" aparecendo depois de uma resposta certa. A chamada de `play()` pode carregar o arquivo errado ou um arquivo inexistente. Só um teste que conheça o resultado esperado de cada botão (por exemplo, guiado por `respostas.csv`) verifica funcionamento.

Os cliques são feitos em sequência, sem recarregar a página, e o estado se acumula. Por isso o relatório separa:

- **desabilitado desde o carregamento**: o botão já estava desabilitado antes de qualquer clique do teste;
- **desabilitado após interações anteriores**: o botão estava habilitado no carregamento, mas foi desabilitado durante o teste. Isso pode ter sido causado por um clique anterior do próprio teste, como as alternativas bloqueadas depois que uma resposta da mesma questão é escolhida. O teste não registra qual clique causou o bloqueio.

## O que é verificado

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

## O que não é verificado

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

## Execuções registradas

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
