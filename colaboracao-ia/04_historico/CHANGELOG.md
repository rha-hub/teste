# Changelog

## 2026-10-30 — escopo PDF-only

- Decisão de produto: exclusivamente livro digital estático em PDF.
- Removidas as quatro tabelas de áudio e substituído o esquema por modelo editorial.
- Substituído o verificador por validação editorial sem dependências de áudio.
- Reescritos README, protocolo, instruções e cobertura de testes para refletir o escopo PDF-only.
- Pendências: execução independente dos testes, revisão de referências residuais em arquivos históricos e validação visual do PDF final.

## 2026-10-30 — correção de testes e inspeção de entregáveis

- Corrigido o caminho de importação do verificador nos testes, para que a suíte documentada funcione sem configurar `PYTHONPATH`.
- Corrigida a escrita de cabeçalho CSV no teste para preservar LF no Windows.
- Resultado reproduzido localmente: 7/7 testes aprovados; verificador dos CSVs vazio sem erros.
- Inspecionado o PDF do Capítulo 4: 8 páginas em duas versões de layout, com conteúdo provisório e referências a áudio/QR. Não corresponde ao produto final PDF-only.
- Registradas no estado atual as lacunas que impedem concluir o livro e as verificações não executáveis neste ambiente.
