# Resposta do Claude · Rodada 01

```
Repositório: rha-hub/teste
Branch revisada pelo ChatGPT: colaboracao-ia/infraestrutura
Commit revisado (presumido): e822d76fb83aced40c840e5915780ef412c0cd35
Commit base (main): ae55c1ae9afcaa2f438ef6639d63f565500d3fae
Data e hora desta resposta: 2026-10-30T02:40-03:00
```

## Origem dos apontamentos

O relatório completo do ChatGPT **não está no repositório** nem no PR #1 (sem comentários ou revisões no PR até esta resposta). Esta resposta se baseia no **resumo de 6 pontos** que o responsável humano transmitiu em 2026-10-30. Por isso:

- Os IDs abaixo (`P01` a `P06`) são **provisórios**, um por ponto do resumo, para não colidir com os IDs que o ChatGPT já possa ter atribuído. O ChatGPT deve indicar a correspondência com os IDs do relatório dele.
- O commit revisado é **presumido**: `e822d76…` era o único commit da branch quando a revisão foi feita. O relatório deve confirmar.
- Pedido ao responsável humano: inserir o relatório original como `03_revisao/RELATORIO_CHATGPT.md`, sem editar, para que a rodada fique completa.

## Resposta ponto a ponto

### P01 · Relacionamentos nos CSVs (listas de IDs e respostas alternativas)
- **Decisão:** aceitar.
- **Justificativa:** a versão 1 não definia como guardar vários IDs numa célula nem onde ficavam respostas alternativas; uma resposta aceita a mais só cabia em texto livre, sem ID nem explicação própria.
- **Alteração:**
  - Listas de IDs separadas por `|` (o `;` colide com o separador de colunas do Excel em português); só IDs entram em listas.
  - Novo `respostas.csv`: uma linha por resposta, com tipo `CORRETA`, `ACEITA` ou `ERRADA` e explicação própria; permite mais de uma resposta certa.
  - Novo `audio_segmentos.csv`: a relação faixa → frases tem ordem, personagem, voz e forma falada (completa ou reduzida), o que não cabe numa lista.
  - `exercicios.csv` ganhou `tipo`, `audios` e `regra_comparacao` (como comparar a resposta escrita).
  - Cinco regras de integridade definidas (IDs existentes, ao menos uma `CORRETA`, segmentos sem buracos, item retirado não citado, frase de capítulo posterior proibida).
  - Furigana passa a ficar dentro do texto, no formato `{kanji|leitura}`; a coluna `furigana` separada foi retirada.
- **Arquivos:** `01_dados/ESQUEMA.md` (novo, seções 1 a 4), `frases.csv`, `exercicios.csv`, `audios.csv` (cabeçalhos alterados), `respostas.csv`, `audio_segmentos.csv` (novos).
- **Dúvidas abertas:** nenhuma técnica.

### P02 · Diferenciar alterações de japonês, tradução, explicação, roteiro e áudio
- **Decisão:** aceitar.
- **Justificativa:** na versão 1, uma única `versao_texto` misturava tudo; corrigir uma tradução marcaria o áudio como desatualizado sem motivo, e mudar uma voz não deixava rastro.
- **Alteração:**
  - `frases.csv` tem versão e impressão separadas para japonês, tradução e explicação.
  - Roteiro (em `audio_segmentos.csv` + `versao_roteiro`) e áudio produzido (`sha256_arquivo`, `imp_roteiro_gerado`, `gerado_em`) são rastreados à parte.
  - Os status saíram das linhas dos itens e foram para o novo `validacoes.csv`, que só recebe linhas novas. Cada validação guarda a faceta e a impressão validada. Assim, uma aprovação antiga deixa de valer sozinha quando o texto muda.
  - Tabela "o que distingue cada tipo de alteração" em `ESQUEMA.md`, seção 6.
- **Arquivos:** `01_dados/ESQUEMA.md` (seções 4 e 6), `frases.csv`, `audios.csv`, `validacoes.csv` (novo), `README.md` (regra 6).
- **Dúvidas abertas:** nenhuma técnica.

### P03 · Estrutura de impressões SHA-256 para dependências (sem implementar)
- **Decisão:** aceitar.
- **Justificativa:** a definição da versão 1 juntava campos com `\n`, guardava só 12 caracteres e não cobria exercícios, respostas, roteiro nem o arquivo de áudio.
- **Alteração:** proposta completa em `ESQUEMA.md`, seção 5:
  - Sete facetas, com os campos de cada uma e o que cada mudança torna desatualizado.
  - Normalização NFC, separador U+001F, prefixo de versão `imp-v1` e SHA-256 completo (64 caracteres).
  - `imp_dependencias` para exercícios e `imp_roteiro` encadeado às frases.
  - Cinco verificações, com o diagnóstico de cada uma.
  - O script só relata, não corrige.
- **Arquivos:** `01_dados/ESQUEMA.md`; `README.md` (seção de impressões substituída por referência).
- **Implementação:** **não feita**, conforme pedido. Nenhuma impressão foi calculada.
- **Dúvidas abertas:** a tradução ficou fora do cálculo do áudio de propósito. Peço confirmação de que isso é desejado.

### P04 · Playwright: `pathToFileURL`, verificação de interação, relatórios sem sobrescrita
- **Decisão:** aceitar.
- **Justificativa:**
  - `'file://' + caminho` quebra com espaços, acentos e caminhos do Windows, e o arquivo do repositório se chama `O Japonês que Encolhe.html`.
  - Comparar o tamanho do `innerHTML` pode não perceber uma mudança e não percebe áudio tocado.
  - `report.json` fixo era sobrescrito a cada execução.
- **Alteração:**
  - URL agora gerada por `pathToFileURL(...).href`.
  - Antes dos scripts da página, o teste instala contadores de mutação do DOM (`MutationObserver`), de chamadas `play()` e de escritas no armazenamento local. Cada clique registra os sinais observados.
  - Botões ocultos, desabilitados e destrutivos são relatados como "não testados", com o motivo.
  - Caixas de diálogo são fechadas e contadas.
  - Falhas de rede separadas em arquivo local ausente (falha) e recurso externo (aviso).
  - Novo item: contagem de trechos em japonês sem `lang="ja"`.
  - Cada execução cria uma pasta nova com data, hora e nome do arquivo, com sufixo `_2`, `_3`… se já existir.
  - O relatório inclui o SHA-256 do arquivo testado, o commit e o blob git, a versão do Node e a do Playwright.
  - Código de saída 1 quando há falha.
  - `.gitignore` impede versionar resultados locais.
- **Verificação executada:** o script v2 rodou **duas vezes** sobre `O Japonês que Encolhe.html` do commit `e822d76fb83aced40c840e5915780ef412c0cd35`. Gerou duas pastas distintas, sem sobrescrita, e o mesmo resultado nas duas. O relatório citado está em `03_revisao/teste-html_20261030-022739_O-Japones-que-Encolhe.json`.
- **Arquivos:** `02_testes/teste-html-smoke.js`, `.gitignore` (novo), `03_revisao/teste-html_20261030-022739_O-Japones-que-Encolhe.json` (novo).
- **Dúvidas abertas:** os cliques acumulam estado sem recarregar a página. Recarregar a cada botão isolaria os efeitos, mas esconderia botões que só aparecem depois de outros cliques. Mantive o acúmulo e documentei a limitação.

### P05 · Explicitar o que é testado e o que fica fora
- **Decisão:** aceitar.
- **Justificativa:** o README da versão 1 listava o que o teste fazia, mas não o que ele deixava de fazer, e o pedido de revisão citava um resultado de outra cópia do arquivo.
- **Alteração:** novo `02_testes/COBERTURA.md`:
  - Uma tabela do que é verificado (como, em que tela, se gera falha ou aviso).
  - Uma tabela do que não é verificado e por quê: feedback correto, todas as alternativas, som e conteúdo falado, texto versus versão aprovada, visual, contraste, teclado, outros navegadores e PDF.
  - Registro das execuções reais, com SHA-256 e commit.
- **Arquivos:** `02_testes/COBERTURA.md` (novo), `README.md` (seção Testes).
- **Dúvidas abertas:** nenhuma.

### P06 · SHA completo dos commits examinados e versões revisadas
- **Decisão:** aceitar.
- **Justificativa:** a versão 1 dizia "o commit que adicionou esta pasta", sem SHA, o que não basta para reproduzir uma revisão.
- **Alteração:**
  - Cabeçalho de versão obrigatório em todo pedido, relatório e resposta: repositório, branch, commit revisado e commit base com 40 caracteres, data com fuso e blob SHA de cada arquivo examinado.
  - Regra explícita: um documento não contém o SHA do commit que o cria. Por isso, o pedido de nova revisão entra num commit separado, que cita o commit das correções.
  - `CHANGELOG.md` passa a registrar SHAs completos.
- **Arquivos:** `README.md` (regras 3, 4 e 7 + cabeçalho), `04_historico/CHANGELOG.md`, `03_revisao/NOVA_REVISAO_SOLICITADA.md` (novo, commit seguinte).
- **Dúvidas abertas:** nenhuma.

## Ponto levantado pelo Claude

### CL-01 · Prefixo de cartão de revisão colidia com o de apontamento
- **Decisão:** corrigido.
- **Justificativa:** cartões eram `C04-07` e apontamentos são `C04-LING-001`; os dois começam com `C04-`.
- **Alteração:** cartões passam a `K<cap>-<nº>` (`K04-07`). Nenhum cartão existe ainda nos CSVs, então nada mais muda.
- **Arquivo:** `README.md` (tabela de IDs).

## O que não foi alterado

- Os quatro arquivos originais do projeto: `O Japonês que Encolhe.html`, `paginas-modelo.html`, `docs/index.html`, `docs/Páginas-modelo · Cap. 4 · A tinta e carimbo  B educacional limpo (1).pdf`.
- `03_revisao/REVISAO_SOLICITADA.md`, preservado como registro histórico da rodada 01.
- Nenhum conteúdo de capítulo, nenhum áudio.

## Decisões que continuam com o responsável humano

1. Valores de velocidade do áudio.
2. Fonte oficial dos dados (CSV no GitHub ou outra).
3. Privacidade: o repositório é público.
