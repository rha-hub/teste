# Cobertura de testes — infraestrutura do livro PDF

Os testes automatizados ativos (suíte Python) verificam: furigana estrutural, integridade dos cabeçalhos, referências entre frases/exercícios/respostas, IDs duplicados, resposta correta em exercício ativo e ausência de tabelas de áudio/interação.

O script `teste-html-smoke.js` e seus JSONs de captura são históricos, ligados aos protótipos HTML anteriores. Não são testes ativos nem critério para o produto PDF-only; ficam preservados como evidência da arquitetura anterior.

Comando: `python3 -m unittest discover -s colaboracao-ia/02_testes -p 'test_*.py'`.

Limites: testes automatizados não julgam naturalidade do japonês, fidelidade da tradução, qualidade pedagógica, direitos autorais, diagramação ou legibilidade do PDF. Esses pontos exigem revisão editorial humana e inspeção visual do PDF exportado.
