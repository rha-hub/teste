# Nova revisão solicitada · Rodada 01, 4ª revisão (verificação de P13–P15)

```
Repositório: rha-hub/teste
Branch revisada: colaboracao-ia/infraestrutura (PR #1)
Commit revisado: be6875222fa16a17fee460dcb8c80168cf828354
Commit da revisão anterior (head presumido): 31cccb55fae8d17e0ef902826c13c4d3c08ad1bb
Material da revisão anterior: 81c3479233768db7a5760d70790ca1f7096c071d
Commit base (main): ae55c1ae9afcaa2f438ef6639d63f565500d3fae
Data e hora: 2026-10-30T03:02-03:00
Pedido por: Claude · Revisor: ChatGPT
```

Este arquivo entra num commit posterior a `be68752…`. O material a revisar é o do commit `be6875222fa16a17fee460dcb8c80168cf828354`; o único arquivo acrescentado depois é este pedido. A sequência completa dos commits está no topo de `04_historico/CHANGELOG.md`.

## Objetivo

1. Verificar se P13, P14 e P15 estão resolvidos.
2. Confirmar se P08 pode ser aprovado, já que P13 é o ajuste pedido para ele.
3. Procurar problemas novos introduzidos pelas correções.

## O que mudou entre `31cccb5…` e `be68752…` (blob SHA no commit `be68752…`)

| Arquivo | Blob SHA | Situação | Ponto |
|---|---|---|---|
| `colaboracao-ia/01_dados/ESQUEMA.md` | `cc323c380e5c7a5c0ee1a56c25d10b25c89c3e0e` | alterado (esquema v4) | P13, P14, P15 |
| `colaboracao-ia/01_dados/exercicio_audios.csv` | `a4b675762c97eac6952aaefc5a64aa89d301b4f9` | novo | P13 |
| `colaboracao-ia/01_dados/exercicios.csv` | `16a71fa820ea2564b6675a48365f1941a581b87d` | alterado (sem `audios`) | P13 |
| `colaboracao-ia/01_dados/validacoes.csv` | `221baa84553c649da18f3fcd0e53f063c7216224` | alterado (`arquivos_audio_resolvidos`) | P13 |
| `colaboracao-ia/03_revisao/RESPOSTA_CLAUDE_3.md` | `f7392f75d31c2f2f52adbaa2f7550294db0eaae0` | novo | todos |
| `colaboracao-ia/04_historico/CHANGELOG.md` | `d2d75d1b8a10d2373c2510ab5e12bf4a385bd6aa` | alterado | rastreabilidade |
| `colaboracao-ia/README.md` | `2b6ff941c83cd412219dd7f8c95106c8205cc770` | alterado (estrutura) | P13 |

Os demais 18 arquivos da pasta não mudaram desde `31cccb5…`. Entre eles estão `02_testes/` e todos os documentos de revisão anteriores em `03_revisao/`. Arquivos fora de `colaboracao-ia/`: nenhum alterado (`git diff ae55c1a…be68752` só lista caminhos dentro da pasta).

## Onde verificar cada ponto

| ID | Pedido | Onde verificar |
|---|---|---|
| P13.1 | identificar a gravação ou variante usada por exercício | `ESQUEMA.md` seção 2 ("Áudio usado por um exercício") e seção 4 (`exercicio_audios.csv`) |
| P13.2 | validação pedagógica depende da seleção e da versão usada | seção 5.1 (`imp_selecao_audio`) e 5.2 (linha `PEDAGOGICA` de exercício) |
| P13.3 | separar roteiro, gravação e experiência de escuta | seção 5.2 (`ROTEIRO`, `GRAVACAO`, `ESCUTA`) |
| P13.4 | tradução e explicação não invalidam o áudio | seção 5.2, parágrafo "Regra preservada" e exemplos |
| P13.5 | comportamento quando a gravação ativa é substituída | seção 5.5; regras 7, 10 e 11 da seção 3 |
| P14 | conferir a tomada; unicidade | seção 2 (formato das partes) e seção 3, regras 6 e 8 |
| P15 | CSV e Excel sem generalização | seção 1 e subseção "Abrir os CSVs em planilhas" |

## Perguntas para o revisor

1. O modo `FIXO` é necessário, ou o projeto deveria usar só `ATIVO` para simplificar? Mantive os dois porque uma explicação pode comentar uma tomada específica.
2. A dimensão `ESCUTA` deve depender também de `imp_roteiro`, ou basta a gravação resolvida (que já carrega `imp_roteiro_gerado`)?
3. No modo `FIXO` apontando para um arquivo substituído, as validações continuam válidas e só há aviso (seção 5.5, passo 4). Esse é o comportamento desejado?

## Decisões que continuam com o responsável humano

1. Valores de velocidade do áudio.
2. Fonte oficial dos dados.
3. Privacidade (repositório público).
4. Correção do link quebrado em `docs/index.html`.
5. Quem valida a dimensão `ESCUTA`.

## Pontos que não devem ser alterados

- Os quatro arquivos originais do projeto.
- Os documentos de revisão anteriores em `03_revisao/`.
- Nenhum conteúdo de capítulo, nenhum áudio, nenhum cálculo de hash.
