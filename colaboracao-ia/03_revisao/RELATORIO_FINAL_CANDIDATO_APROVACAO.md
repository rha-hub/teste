# Relatório de transição de escopo — PDF-only

**Este documento substitui o relatório de candidato à aprovação anterior.** Os testes e resultados nele descritos pertenciam à arquitetura anterior, que incluía áudio, e não devem ser usados como evidência de aprovação da nova versão.

## Decisão de produto

O responsável pelo projeto determinou que o produto será exclusivamente um livro estático em PDF. Nenhuma interação fora do PDF será desenvolvida.

## Alterações aplicadas nesta rodada

- Removidos `audios.csv`, `audio_segmentos.csv`, `arquivos_audio.csv` e `exercicio_audios.csv`.
- Removida a coluna `arquivos_audio_resolvidos` de `validacoes.csv`.
- Substituído o esquema v5 por um esquema editorial PDF-only.
- Substituído o verificador para operar somente com frases, exercícios impressos, respostas e validações editoriais.
- Removidos os geradores de dados fictícios e testes de mutação que dependiam de áudio.
- Criada uma suíte inicial de testes para o modelo PDF-only.
- Reescritos README, protocolo, instruções de executor/revisor, cobertura e estado.

## Limites e pendências

- Os testes **ainda não foram executados independentemente nesta rodada**. Não declarar a nova suíte aprovada até executá-la em clone limpo.
- O verificador é estrutural; não julga naturalidade do japonês, fidelidade de tradução, qualidade pedagógica, direitos autorais ou diagramação.
- Ainda é necessário revisar documentos históricos e apontamentos antigos que mencionam áudio, identificando-os como superados, sem apagar o histórico.
- O fluxo de produção e inspeção visual do PDF final ainda precisa ser validado.
- Nenhuma aprovação de publicação ou merge está concedida.

## Critério de encerramento

O PR só poderá ser considerado pronto quando a suíte PDF-only e o verificador forem executados com sucesso em clone limpo, as referências residuais ao escopo anterior estiverem claramente marcadas como históricas/superadas, e houver um processo verificável de inspeção visual do PDF.
