# Cobertura de testes — infraestrutura do livro PDF

Os testes automatizados verificam: furigana estrutural, integridade dos cabeçalhos, referências entre frases/exercícios/respostas, IDs duplicados, resposta correta em exercício ativo e ausência de tabelas de áudio/interação.

Comando: `python3 -m unittest discover -s colaboracao-ia/02_testes -p 'test_*.py'`.

Limites: testes automatizados não julgam naturalidade do japonês, fidelidade da tradução, qualidade pedagógica, direitos autorais, diagramação ou legibilidade do PDF. Esses pontos exigem revisão editorial humana e inspeção visual do PDF exportado.
