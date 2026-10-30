> **HISTÓRICO — SUPERADO.** Este documento registra uma rodada anterior e pode conter requisitos de áudio ou arquitetura que não se aplicam mais. A decisão vigente é exclusivamente um livro estático em PDF. Preservado como evidência; não usar como instrução atual.

# Resposta do Claude · Rodada 01, 3ª revisão

```
Repositório: rha-hub/teste
Branch revisada pelo ChatGPT: colaboracao-ia/infraestrutura (PR #1)
Head da branch durante a 3ª revisão (presumido): 31cccb55fae8d17e0ef902826c13c4d3c08ad1bb
Material examinado na 3ª revisão: 81c3479233768db7a5760d70790ca1f7096c071d
Commit base (main): ae55c1ae9afcaa2f438ef6639d63f565500d3fae
Data e hora desta resposta: 2026-10-30T03:00-03:00
```

## Resultado da 3ª revisão (transmitido pelo responsável humano)

- **Aprovados:** P07, P09, P10, P11, P12.
- **P08:** precisa de ajuste. O ajuste foi detalhado como P13.
- **Novos:** P13, P14, P15.

O relatório da 3ª revisão também não foi gravado no repositório: a branch continuava em `31cccb5…`. Os IDs P13–P15 foram atribuídos pelo ChatGPT.

## Resposta ponto a ponto

### P13 · Dependência pedagógica do arquivo de áudio efetivamente usado (ajuste de P08)
- **Decisão:** aceitar.
- **Justificativa:** o apontamento está correto. Na versão 3, a validação pedagógica do exercício dependia só de `imp_roteiro`. Uma tomada nova, com roteiro igual, trocava o que o aluno ouve sem invalidar nada. E `exercicios.audios` citava só a faixa lógica, sem velocidade e sem dizer qual gravação.
- **Alteração** (`01_dados/ESQUEMA.md`, esquema v4):
  1. **Identificar a gravação usada.** O novo `exercicio_audios.csv` tem uma linha por áudio do exercício, com `id_audio`, `velocidade`, `modo_selecao` e `uso`.
     - `modo_selecao=ATIVO`: o exercício usa a gravação ativa daquela faixa e velocidade.
     - `modo_selecao=FIXO`: o exercício usa uma gravação específica (`id_arquivo_audio`).
     - O arquivo que o aluno efetivamente ouve recebeu um nome: **gravação resolvida**.
     - A coluna `audios` saiu de `exercicios.csv`.
  2. **Validação pedagógica depende da gravação usada.** A nova impressão `imp_selecao_audio` cobre, para cada áudio do exercício, a gravação resolvida, seu `sha256_arquivo` e seu `imp_roteiro_gerado`. A validação `PEDAGOGICA` do exercício passa a depender dela.
     - `imp_exercicio` cobre a seleção **declarada**; `imp_selecao_audio` cobre o arquivo **resolvido**. No modo `ATIVO` a declaração continua igual enquanto o arquivo muda, e por isso as duas existem.
     - `validacoes.csv` ganhou `arquivos_audio_resolvidos`, que diz qual gravação foi aprovada sem precisar recalcular nada.
  3. **Três dimensões para áudio:**
     - `ROTEIRO` (faixa): o texto a falar está certo.
     - `GRAVACAO` (arquivo; antes `AUDIO`): o arquivo fala o roteiro com fidelidade e qualidade, independentemente de qualquer exercício.
     - `ESCUTA` (exercício; nova): esta gravação, nesta velocidade, funciona para este exercício.
  4. **Regra preservada:** tradução e explicação não entram em `imp_roteiro`, `sha256_arquivo` nem `imp_selecao_audio`. Elas invalidam só `TRADUCAO` e `PEDAGOGICA`, nunca a gravação, `ROTEIRO`, `GRAVACAO` ou `ESCUTA`. A regra está escrita explicitamente na seção 5.2 e aparece na tabela de exemplos.
  5. **Substituição de gravação ativa:** a nova seção 5.5 descreve o processo passo a passo:
     - troca de `ATIVO` no mesmo commit, sem apagar nada;
     - a gravação nova não herda validação;
     - exercícios `ATIVO` perdem `PEDAGOGICA` e `ESCUTA`;
     - exercícios `FIXO` mantêm as validações, mas geram aviso, e a equipe decide entre migrar ou manter com justificativa;
     - `ROTEIRO` não é afetado, salvo quando a substituição vem de mudança de roteiro.

  Também entraram as regras de integridade 9, 10 e 11 (coerência do modo de seleção, gravação ativa ausente, gravação fixa substituída ou retirada) e duas verificações novas na seção 5.4.
- **Arquivos:** `01_dados/ESQUEMA.md`, `01_dados/exercicio_audios.csv` (novo), `01_dados/exercicios.csv`, `01_dados/validacoes.csv`, `README.md`.
- **Hashes:** **não implementados**, conforme pedido.
- **Dúvidas abertas:** quem faz a validação `ESCUTA` (revisor nativo, ChatGPT ou responsável humano) é decisão editorial. O esquema aceita qualquer um deles em `revisor`.

### P14 · Integridade do identificador de áudio
- **Decisão:** aceitar.
- **Justificativa:** a regra 6 da versão 3 conferia `id_audio`, `velocidade` e `versao_roteiro`, mas não `tomada`. Um arquivo `…_t2` registrado com `tomada=1` passaria. Também faltava dizer que o identificador é único.
- **Alteração:**
  - A seção 2 define o formato de cada parte: velocidade com exatamente três dígitos; versão e tomada inteiros ≥ 1, sem zeros à esquerda.
  - A regra 6 passa a conferir o identificador completo, montado com as quatro colunas da mesma linha. Qualquer divergência, inclusive só na tomada, é erro.
  - A nova regra 8 exige `id_arquivo_audio` único e nunca reutilizado, e também a combinação (`id_audio`, `velocidade`, `versao_roteiro`, `tomada`) única.
- **Arquivos:** `01_dados/ESQUEMA.md` (seções 2 e 3).
- **Dúvidas abertas:** nenhuma.

### P15 · Separador CSV e Excel
- **Decisão:** aceitar.
- **Justificativa:** a afirmação "o Excel em português usa `;`" generalizava. O separador usado ao abrir por duplo clique depende da configuração regional (no Windows, o "separador de lista") e da forma de abertura.
- **Alteração:**
  - O texto de `ESQUEMA.md`, seção 1, foi reescrito. O motivo para usar `|` dentro das células agora é a segurança em qualquer configuração, sem afirmar o que todas as instalações fazem.
  - Nova subseção "Abrir os CSVs em planilhas":
    - o separador dos arquivos é sempre a vírgula;
    - abrir por duplo clique pode ou não funcionar;
    - no Excel, importar escolhendo UTF-8 (65001) e delimitador vírgula, com a ressalva de que o nome do menu varia por versão;
    - instruções equivalentes para LibreOffice e Google Planilhas;
    - ao salvar, manter CSV UTF-8 com vírgula.
- **Arquivos:** `01_dados/ESQUEMA.md` (seção 1).
- **Observação:** a mesma afirmação aparece em `03_revisao/RESPOSTA_CLAUDE.md` (P01). Esse documento é registro de uma revisão anterior e não foi alterado; a afirmação fica superada por esta resposta.
- **Dúvidas abertas:** nenhuma.

## O que não foi alterado

- Os quatro arquivos originais do projeto.
- Todos os documentos de revisão anteriores em `03_revisao/`.
- `02_testes/` (P09 e P10 aprovados).
- Nenhum conteúdo de capítulo, nenhum áudio, nenhum cálculo de hash.

## Decisões que continuam com o responsável humano

1. Valores de velocidade do áudio.
2. Fonte oficial dos dados.
3. Privacidade (repositório público).
4. Correção do link quebrado em `docs/index.html`.
5. Quem valida a dimensão `ESCUTA`.
