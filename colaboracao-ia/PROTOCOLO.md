# Protocolo de colaboração · Claude (executor) e ChatGPT (revisor)

Versão do protocolo: **2** (2026-10-30). Substitui as seções de fluxo do `README.md` anterior.

O GitHub (`rha-hub/teste`) é a fonte compartilhada do estado e do histórico. Uma informação só existe para o projeto quando está num arquivo versionado ou no PR. Mensagens copiadas entre conversas servem de aviso, não de registro.

Instruções operacionais de cada papel:
- [`instrucoes/CLAUDE_EXECUTOR.md`](instrucoes/CLAUDE_EXECUTOR.md)
- [`instrucoes/CHATGPT_REVISOR.md`](instrucoes/CHATGPT_REVISOR.md)

## 1. Papéis

| Papel | Responsável | Faz | Não faz |
|---|---|---|---|
| Executor | Claude | produz e corrige material, scripts e documentos; roda testes e o verificador; responde aos apontamentos | não marca apontamento como `VERIFICADO`; não registra aprovação final de nenhuma dimensão; não altera nem apaga revisões |
| Revisor técnico | ChatGPT | revisão independente; abre apontamentos; verifica correções contra o commit indicado | não corrige o material por conta própria; não aprova o produto; não substitui o revisor humano de japonês |
| Revisor de japonês | pessoa com competência em japonês (`HUMANO_JAPONES`) | aprovação final de `LINGUISTICA`, `TRADUCAO` e `GRAVACAO` | — |
| Responsável humano | dono do projeto (`HUMANO_RESPONSAVEL`) | decide divergências; aprova versões, merges e publicação; aprovação final de `PEDAGOGICA`, `ROTEIRO` e `ESCUTA` (também aceitas de `HUMANO_JAPONES`) | — |

Aprovação de IA (Claude ou ChatGPT) numa validação de conteúdo é registrada e contada como **auxiliar**. O verificador a mostra como `APROVADO_AUXILIAR` e nunca como aprovação final. Um problema apontado por IA (`AJUSTAR`, `NAO_USAR`) bloqueia normalmente.

## 2. Onde cada coisa fica

| O quê | Onde | Quem escreve |
|---|---|---|
| Pedido de revisão | `03_revisao/REVISAO_SOLICITADA*.md`, `NOVA_REVISAO_SOLICITADA*.md` | Claude |
| Relatório de revisão | `03_revisao/RELATORIO_CHATGPT*.md` | ChatGPT (ou o responsável humano, que copia sem editar) |
| Resposta aos apontamentos | `03_revisao/RESPOSTA_CLAUDE*.md` | Claude |
| Registro de apontamentos | `03_revisao/apontamentos.csv` | quem abre o apontamento cria a linha; Claude atualiza a correção; quem verifica preenche a verificação |
| Validações de conteúdo | `01_dados/validacoes.csv` | o revisor de cada dimensão (só acrescenta linhas) |
| Decisões | `04_historico/DECISOES.md` | responsável humano (ou Claude, transcrevendo uma decisão dada por escrito) |
| Histórico de mudanças | `04_historico/CHANGELOG.md` | Claude |
| Estado da implementação | `ESTADO.md` | Claude; o revisor confere |

Arquivos repetidos dentro de uma rodada recebem sufixo numérico (`_2`, `_3`). Nenhum arquivo de revisão é movido, renomeado ou apagado. Ao encerrar uma rodada, um arquivo `ENCERRAMENTO_RODADA_NN.md` lista os documentos da rodada.

## 3. Apontamentos

Cada problema vira **uma linha** em `03_revisao/apontamentos.csv`, com ID único e nunca reutilizado.

| ID | Quando |
|---|---|
| `C<cap>-<ÁREA>-<nnn>` (ex.: `C04-LING-001`) | apontamento sobre conteúdo de capítulo |
| `P<nn>` | apontamento do revisor sobre a infraestrutura (série usada na rodada 01) |
| `CL-<nn>` | apontamento levantado pelo próprio executor |

Áreas: `LING`, `TRAD`, `PED`, `AUD`, `DADOS`, `TEST`, `DOC`, `EDIT`, `INFRA`. Gravidade: `ALTA`, `MEDIA`, `BAIXA`.

### Ciclo de vida

```
ABERTO → EM_CORRECAO → CORRIGIDO_AGUARDA_VERIFICACAO → VERIFICADO
                    ↘ REJEITADO_COM_JUSTIFICATIVA
ABERTO/qualquer → SUPERADO (substituído por outro ID, citado em observacoes)
qualquer → DIVERGENCIA_AGUARDA_HUMANO (executor e revisor discordam)
```

O verificador impõe estas regras (`verificar_dados.py verificar-apontamentos`):

- `CORRIGIDO_AGUARDA_VERIFICACAO` e `VERIFICADO` exigem `commit_correcao` (40 caracteres) e `evidencia`.
- `VERIFICADO` exige `verificado_por` **diferente do executor** (`IA_CHATGPT` ou `HUMANO_*`) e `commit_verificado` (40 caracteres).
- `REJEITADO_COM_JUSTIFICATIVA`, `SUPERADO` e `DIVERGENCIA_AGUARDA_HUMANO` exigem justificativa em `observacoes`.

## 4. Evidência obrigatória para declarar uma correção concluída

Uma resposta em texto **não** é prova de implementação. Para mudar um apontamento para `CORRIGIDO_AGUARDA_VERIFICACAO`, o executor indica:

1. o commit (40 caracteres) que contém a correção;
2. o arquivo e o trecho alterados;
3. quando há código: o teste automatizado que falharia sem a correção e o resultado da execução (comando, data, saída);
4. quando há documentação: a seção exata, e que nenhum outro documento afirma o contrário.

O revisor só marca `VERIFICADO` depois de conferir os itens 1 a 4 no commit indicado. Ele roda os testes quando pode; quando não pode, diz que não rodou.

## 5. Critérios de aprovação

**Um apontamento é aprovado** (`VERIFICADO`) quando a evidência da seção 4 confere e a correção não cria problema novo relacionado.

**Uma versão da infraestrutura é candidata à aprovação** quando:

1. `python3 -m unittest discover -s colaboracao-ia/02_testes -p 'test_*.py'` passa;
2. `python3 colaboracao-ia/02_testes/mutacoes.py` detecta todas as mutações;
3. `verificar_dados.py verificar` sobre `01_dados/` não tem ERRO;
4. `verificar_dados.py verificar-apontamentos` não tem ERRO;
5. `verificar_originais.py` dá ÍNTEGRO;
6. não há apontamento `ALTA` em `ABERTO`, `EM_CORRECAO` ou `DIVERGENCIA_AGUARDA_HUMANO`;
7. `ESTADO.md` não declara implementado nada que não esteja no código.

**Reprovação**: qualquer item acima falhando, ou um `NAO_USAR` do revisor sem resposta.

**Aprovação final** (merge, publicação, uso comercial) é sempre do responsável humano, por escrito em `04_historico/DECISOES.md`. Nenhuma IA faz merge.

## 6. Versão revisada e SHA

Todo pedido, relatório e resposta começa com:

```
Repositório: rha-hub/teste
Branch: <nome>
Commit revisado: <SHA completo, 40 caracteres>
Commit base (main): <SHA completo, 40 caracteres>
Data e hora: <ISO 8601 com fuso>
Arquivos examinados: <caminho + blob SHA (git ls-tree <commit> <caminho>)>
```

Um documento não contém o SHA do commit que o cria. Por isso, o pedido cita o commit do material e entra num commit posterior. Commits nunca são reescritos (sem rebase, amend ou force push nas branches compartilhadas).

## 7. Divergências

1. O executor pode discordar de um apontamento. Ele responde com justificativa técnica e marca `DIVERGENCIA_AGUARDA_HUMANO`.
2. O revisor responde no próximo relatório, mantendo ou retirando o apontamento.
3. Se a divergência continuar, o responsável humano decide e registra a decisão em `DECISOES.md`, com o ID do apontamento.
4. Nenhuma IA muda o sentido de um exemplo ou de uma regra só para encerrar uma divergência.

## 8. Integridade dos registros

- Cada IA escreve apenas nos seus arquivos (seção 2). O executor nunca edita `RELATORIO_CHATGPT*.md`. O revisor nunca edita `RESPOSTA_CLAUDE*.md`.
- `validacoes.csv` e `apontamentos.csv` não perdem linhas. Para corrigir uma validação, acrescenta-se outra; para corrigir um apontamento, muda-se o status e a justificativa.
- Correções em documentos de revisão já enviados são feitas num commit novo, com nota de correção no próprio documento (ex.: `NOVA_REVISAO_SOLICITADA_3.md`, commit `2623de6…`).
- `verificar_originais.py` confirma que os quatro arquivos originais do projeto não mudaram.

## 9. Encerramento de uma tarefa

Uma tarefa está encerrada quando:

1. todos os apontamentos dela estão `VERIFICADO`, `REJEITADO_COM_JUSTIFICATIVA` ou `SUPERADO`;
2. os comandos da seção 5 foram executados e os resultados estão registrados (data, commit, saída);
3. `CHANGELOG.md` e `ESTADO.md` refletem o estado final;
4. o responsável humano registrou a decisão (aprovar, pedir mudança, encerrar sem merge) em `DECISOES.md`.

## 10. Privacidade

O repositório é público. Ele recebe estrutura, documentação, scripts e exemplos fictícios. Não recebe conteúdo comercial não aprovado, capítulos pagos, áudios comerciais, dados pessoais ou material protegido. Os áudios ficam fora do repositório; o verificador confere os bytes com `--raiz-audio` apontando para a pasta local.
