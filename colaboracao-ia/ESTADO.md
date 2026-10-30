# Estado da implementação

Fonte única do status da infraestrutura. Outros documentos citam este arquivo em vez de repetir o status. Atualizado em 2026-10-30, na rodada final da rodada 01. Os commits estão em `04_historico/CHANGELOG.md`.

## 1. Implementado e testado

| Funcionalidade | Onde | Testes |
|---|---|---|
| Leitura dos 8 CSVs com conferência de UTF-8 sem BOM, LF, cabeçalho exato e número de colunas | `05_ferramentas/verificar_dados.py` (`ler_tabela`) | `EstruturaEArquivos`, `CodigosRestantes` |
| Formatos e valores de todos os campos (IDs, enums, inteiros, datas, SHAs, listas `\|`, furigana, velocidade 010–200, caminho relativo) | `_validar_campos` | `CodigosRestantes`, `EstruturaEArquivos`, `test_11c` |
| Unicidade de todas as chaves, inclusive (faixa, velocidade, versão, tomada) | `_indexar` | `test_11_*` |
| Regras de integridade 1 a 17 (`ESQUEMA.md` seção 3) | `_validar_relacoes`, `_resolver_audios`, `_avaliar_validacoes` | ao menos um teste por regra (`COBERTURA.md`, tabela A2b) |
| Esquema, CSVs oficiais e código descrevem as mesmas colunas, valores fixos e versão | — | `SincroniaEsquemaCodigo` |
| Impressões SHA-256 (normalização NFC, separadores U+001F/U+001E/U+001D, ordenação, prefixo `imp-v1`) | `normalizar`, `registro`, `lista`, `impressao`, `_calcular_impressoes` | `test_impressao_e_deterministica_e_normalizada`, `test_05b` |
| Conferência das impressões correntes gravadas | `_conferir_impressoes_gravadas` | `test_07b`, `test_impressao_nao_gravada` |
| Resolução da gravação usada por exercício (`ATIVO` e `FIXO`) | `_resolver_audios` | `test_06*`, `test_08*`, `test_09` |
| Detecção de roteiro desatualizado, roteiro não fechado e gravação desatualizada | `_conferir_instantaneos` | `test_03`, `test_04`, `test_05`, `test_13`, `test_roteiro_nao_fechado` |
| Conferência dos bytes de áudio com `--raiz-audio` | `_conferir_arquivos_em_disco` | `test_bytes_do_audio_trocados_sem_registro`, `test_audio_ausente_ou_nao_conferido_e_aviso` |
| Dependências por dimensão e validações desatualizadas | `impressao_dimensao`, `_avaliar_validacoes` | cenários 1 a 15 |
| Aprovação final só por revisor humano competente; aprovação de IA como auxiliar | `APROVADORES_FINAIS`, `_avaliar_validacoes` | `RevisoresEValidacoes` |
| Aprovação efetiva do exercício (bloqueios por frase, roteiro, gravação, escuta) | `_avaliar_aprovacao` | `test_03`, `test_06`, `test_13`, `test_exercicio_nao_aprovado_lista_bloqueios` |
| Comando `atualizar-impressoes` (preenche e sobe versões; não toca instantâneos) | `atualizar_impressoes` | `test_01`, `test_02`, `test_03`, `test_07`, `test_atualizar_impressoes_nao_muda_nada_no_estado_aprovado` |
| Comando `fechar-roteiro` | `fechar_roteiro` | `test_roteiro_nao_fechado` |
| Comando `impressao-validacao` | `main` | `test_impressao_validacao` |
| Relatório em texto e JSON; códigos de saída 0/1/2/3 | `relatorio_texto`, `main` | `LinhaDeComando` |
| Registro de apontamentos e regras do protocolo (evidência obrigatória, verificação independente, justificativa) | `verificar_apontamentos` | `Apontamentos` |
| Integridade dos 4 arquivos originais e restrição de alterações a `colaboracao-ia/` | `05_ferramentas/verificar_originais.py` | `Originais.test_quatro_originais_intactos` (caminho de sucesso) |
| Todo código de achado tem ao menos um teste | — | `CoberturaDosCodigos` |
| A suíte detecta defeitos introduzidos de propósito | `02_testes/mutacoes.py` | 15 mutações, com execução de controle |

## 2. Implementado, mas sem teste automatizado

| Funcionalidade | Onde | Situação |
|---|---|---|
| Teste de fumaça HTML (Playwright) | `02_testes/teste-html-smoke.js` | executado manualmente 5 vezes (registros em `COBERTURA.md`, parte B); não há teste automatizado do próprio script |
| Caminho de falha de `verificar_originais.py` (arquivo original alterado) | `05_ferramentas/verificar_originais.py` | só o caminho de sucesso é testado; simular a falha exigiria alterar um original ou montar um repositório git temporário |
| Arquivos de áudio reais (MP3) | `_conferir_arquivos_em_disco` | testado com arquivos fictícios; a lógica não depende do formato, mas nenhum MP3 real foi conferido |

## 3. Documentado, mas ainda não implementado

| Item | Onde está descrito | Observação |
|---|---|---|
| Teste HTML guiado por `respostas.csv` (feedback certo de cada exercício) | `02_testes/COBERTURA.md` (parte B, "fora da cobertura") | o teste atual só observa reação, não correção |
| Comparação do texto de páginas HTML e PDF com `frases.csv` | `ESQUEMA.md` seção 8; `COBERTURA.md` | não implementado |
| Testes de PDF (fontes, furigana, referências de página, QR codes) | plano anterior (documento "Infraestrutura de produção e revisão") | não implementado; o download do PDF do Canva é bloqueado no ambiente do executor |
| Comparação automática entre transcrição do áudio e roteiro | `ESQUEMA.md` (coluna `transcricao_confere`) | hoje a coluna é preenchida manualmente |
| Exigir que `SUPERADO` cite o ID substituto | `PROTOCOLO.md` seção 3 | o verificador exige justificativa, mas não confere se ela contém um ID |

Nenhuma regra obrigatória de `ESQUEMA.md` está nesta lista: todas as regras 1 a 17 e todas as verificações das seções 5.4 e 5.5 estão implementadas e testadas.

## 4. Dependente de decisão ou validação humana

| Item | Por quê |
|---|---|
| Confirmar D-006 (quem dá aprovação final em cada dimensão) | é uma aplicação de D-005 proposta pelo executor |
| Aprovar ou recusar o PR #1 e decidir o merge | só o responsável humano faz merge |
| Indicar o revisor com competência em japonês | as validações `LINGUISTICA`, `TRADUCAO` e `GRAVACAO` dependem dele |
| Corrigir o link quebrado em `docs/index.html` | é um dos quatro arquivos originais (alteração não autorizada) |
| Licença comercial do serviço de voz e dos elementos visuais do Canva | depende dos planos contratados e de verificação nos serviços |
| Verificação independente dos apontamentos `CORRIGIDO_AGUARDA_VERIFICACAO` | cabe ao ChatGPT ou a um humano (`PROTOCOLO.md` seção 4) |

## 5. Fora do escopo desta infraestrutura

- Produção de capítulos, frases didáticas, exercícios reais e roteiros.
- Geração de áudio.
- Diagramação no Canva e exportação de PDF.
- Plataforma de assinatura, loja e publicação.
- Interface de edição no Google Sheets (D-001 a prevê só como camada futura).
- Julgamento da qualidade linguística ou pedagógica: o verificador só confere se existe validação humana vigente.
