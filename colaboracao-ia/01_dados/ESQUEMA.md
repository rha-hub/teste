# Esquema editorial — livro PDF

Versão 6. Escopo exclusivo: produzir, revisar e publicar **um livro estático em PDF**.

Não fazem parte do produto nem desta infraestrutura: áudio, narração, QR codes, vídeo, links para atividades externas, exercícios interativos, aplicativo, site de aluno, plataforma, assinatura, comunidade ou recursos que exijam interação fora do PDF. Exercícios impressos e respostas comentadas dentro do próprio livro são permitidos.

## Arquivos de dados

| Arquivo | Conteúdo | Chave |
|---|---|---|
| `frases.csv` | exemplos japoneses, forma completa/reduzida, tradução e explicação | `id_frase` |
| `exercicios.csv` | exercícios estáticos que serão impressos no PDF | `id_exercicio` |
| `respostas.csv` | gabarito e explicações impressas no PDF | `id_resposta` |
| `validacoes.csv` | histórico de revisão editorial, linguística e pedagógica | `id_validacao` |

Todos os CSVs são UTF-8 sem BOM, LF, separados por vírgula e com cabeçalhos exatos. IDs não são reutilizados. Furigana usa `{kanji|leitura}`.

## Cabeçalhos

- `frases.csv`: `id_frase,capitulo,licao,forma_completa,forma_reduzida,reducao,registro,traducao_ptbr,explicacao_curta,versao_japones,versao_traducao,versao_explicacao,imp_japones,imp_traducao,imp_explicacao,situacao,observacoes`
- `exercicios.csv`: `id_exercicio,capitulo,licao,degrau,tipo,enunciado,frases_usadas,secao_que_ensina,regra_comparacao,versao,imp_exercicio,situacao,observacoes`
- `respostas.csv`: `id_resposta,id_exercicio,rotulo,texto,tipo,explicacao,versao,imp_resposta,situacao,observacoes`
- `validacoes.csv`: `id_validacao,data,id_item,dimensao,imp_validada,status,revisor,revisor_identificacao,commit_revisado,apontamento,observacoes`

## Critérios editoriais

1. Cada exemplo apresenta japonês, tradução PT-BR e explicação contextual suficiente.
2. Diferenciar forma completa, redução coloquial, registro e contexto; não transformar tendências em regras absolutas.
3. Furigana deve estar correta e consistente.
4. Exercícios são impressos no livro; gabarito e justificativas também ficam no PDF.
5. Não usar conteúdo protegido de terceiros sem autorização.
6. Toda alteração relevante recebe nova revisão; aprovações de IA são auxiliares, nunca aprovação humana final.
7. O PDF final deve ser legível em tela e impressão, ter sumário, paginação, hierarquia tipográfica consistente, fontes incorporadas e links internos funcionais quando usados.
8. A exportação precisa ser inspecionada visualmente página a página antes da publicação.

## Validações

Dimensões: `LINGUISTICA`, `TRADUCAO`, `PEDAGOGICA`, `EDITORIAL`.
Status: `APROVADO`, `AJUSTAR`, `NAO_USAR`, `PENDENTE_DE_VALIDACAO`.
Aprovação final: japonês competente para linguística e tradução; responsável humano para editorial; pedagógica por japonês competente ou responsável humano. Aprovação de IA é apenas auxiliar.

O verificador confere estrutura, IDs, referências, capítulo, furigana e consistência básica. Ele **não** atesta naturalidade do japonês, qualidade didática, diagramação ou correção visual do PDF; isso exige revisão humana.
