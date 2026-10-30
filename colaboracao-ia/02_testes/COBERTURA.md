# Cobertura do teste de HTML (`teste-html-smoke.js`, versão 2)

Este arquivo diz exatamente o que o teste verifica e o que ele **não** verifica. Um resultado "sem falhas" significa só que os itens da primeira tabela passaram; ele não diz que o material está correto.

## O que é verificado

| Verificação | Como | Tela | Resultado |
|---|---|---|---|
| Erros de script | evento `pageerror` do navegador | computador e celular | falha |
| Arquivos locais ausentes (áudio, imagem, CSS) | requisições `file:` que falharam | computador e celular | falha |
| Recursos externos que não carregaram (fontes, CDN) | requisições `http(s):` que falharam | computador e celular | aviso (pode ser bloqueio de rede do ambiente) |
| Rolagem horizontal | `scrollWidth − clientWidth` | 1280 px e 390 px | aviso |
| Japonês sem `lang="ja"` | cada nó de texto com kana ou kanji, procurando `lang` no ancestral mais próximo | computador | aviso |
| Idioma do documento | atributo `lang` de `<html>` | computador | registrado |
| Botões sem nome acessível | texto, `aria-label`, `aria-labelledby` ou `title` | computador | aviso |
| Imagens sem `alt`, campos sem rótulo | atributos e `<label>` | computador | aviso |
| Links internos (`#âncora`) quebrados | o `id` de destino existe | computador | falha |
| Reação aos cliques | um clique em cada botão visível e habilitado; registra **sinais**: mutação do DOM, chamada de `play()` em áudio, escrita no armazenamento local, mudança de endereço | computador | registrado por botão |
| Caixas de diálogo | são fechadas automaticamente e contadas | computador e celular | registrado |
| Capturas de tela | uma por tela, para revisão humana | computador e celular | arquivo |

Botões com termos como "apagar", "reset", "limpar" ou classe `danger` **não** são clicados, para não apagar dados.

## O que não é verificado

| Fora da cobertura | Por quê / como cobrir |
|---|---|
| Se o feedback de um exercício está **certo** (acerto marcado como acerto) | o teste não conhece as respostas; exige uma versão guiada por `respostas.csv` |
| Todas as alternativas de cada exercício | os cliques acumulam estado sem recarregar a página; depois do primeiro clique numa questão, as outras alternativas costumam ficar desabilitadas e não são testadas |
| Se o áudio **toca** e se o conteúdo falado está certo | o teste vê a chamada de `play()`, não o som; conteúdo exige transcrição comparada ao roteiro |
| Se o texto da página é igual à versão aprovada | exige comparação com `frases.csv` |
| Qualidade visual, alinhamento do furigana, hierarquia | as capturas são para olho humano; nada é comparado automaticamente |
| Contraste de cores, navegação por teclado, leitor de tela | não implementado |
| Safari/WebKit, Firefox, aparelhos reais | só Chromium, em tela simulada |
| Persistência após recarregar a página | não implementado |
| PDF | fora do escopo deste script |

## Execuções registradas

Só entram aqui execuções que de fato aconteceram, com o SHA completo do que foi testado.

| Data | Script | Arquivo testado | Commit | SHA-256 do arquivo | Resultado |
|---|---|---|---|---|---|
| 2026-10-30T02:27-03:00 | v2 | `O Japonês que Encolhe.html` (raiz do repositório) | `e822d76fb83aced40c840e5915780ef412c0cd35` | `4a81cb50622b20dd12725839dbb9d19f26aeb1bf92d0a725e73063dc730f830e` | 2 falhas, 1 aviso (abaixo) |
| 2026-10-30 (rodada 01) | v1 | cópia local do demo do Cap. 4, **não** o arquivo do repositório | — | — | ver `03_revisao/REVISAO_SOLICITADA.md` |

Detalhe da execução v2 (os mesmos números em duas execuções seguidas, gravadas em pastas separadas):

- **Falha:** 5 arquivos MP3 locais ausentes (`formal.mp3`, `casual.mp3`, `dlg_a1.mp3`, `dlg_b.mp3`, `dlg_a2.mp3`), no computador e no celular. O repositório não tem a pasta de áudio.
- **Aviso:** 159 de 159 trechos em japonês sem `lang="ja"`; `<html>` sem `lang`.
- Sem erros de script, sem rolagem horizontal (1280 px e 390 px), sem links internos quebrados, sem botões, imagens ou campos sem nome.
- Cliques: 60 botões; 40 clicados e todos reagiram (29 com mudança no DOM e escrita no armazenamento, 11 só no DOM); 17 não testados por estarem desabilitados (5 botões de áudio e 12 alternativas de exercício; a causa provável é a falta dos MP3 no primeiro caso e o clique anterior em outra alternativa da mesma questão no segundo, mas o teste não registra a causa); 3 não testados por serem destrutivos ("Apagar meu progresso", "Sim, apagar" e "Cancelar", este último porque seu `id` contém "reset").
