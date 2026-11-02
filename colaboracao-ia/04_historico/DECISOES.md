# Decisões do projeto (infraestrutura de colaboração)

**Vigência:** D-008 é a decisão atual de produto. D-002, D-003, D-006 e D-007 foram superadas por ela; a parte de D-005 específica a gravação/roteiro/escuta também foi superada. D-001 (CSVs como fonte) e D-004 (privacidade) continuam aplicáveis. O registro antigo permanece para preservar o histórico.

Registro das decisões do responsável humano. Uma linha por decisão, nunca apagada. Quando uma decisão muda, acrescenta-se uma nova que cita a anterior.

| ID | Data | Decisão | Origem | Onde se aplica |
|---|---|---|---|---|
| D-001 | 2026-10-30 | Os CSVs versionados no GitHub (`colaboracao-ia/01_dados/`) são a **fonte oficial** dos dados nesta primeira versão. Uma interface no Google Sheets, se existir, será só uma camada de edição futura, nunca uma segunda fonte. | instrução escrita do responsável humano (rodada final da rodada 01) | `01_dados/ESQUEMA.md` seção 1 |
| D-002 | 2026-10-30 | Velocidades previstas para o piloto: **normal (100%) e reduzida (80%)**, gravadas como `100` e `080`. Outras velocidades continuam aceitas pela estrutura, mas o verificador as aponta com aviso. | idem | `ESQUEMA.md` seção 2; `verificar_dados.py` (`VELOCIDADES_PILOTO`) |
| D-003 | 2026-10-30 | Seleção de gravação nos exercícios: `ATIVO` é o padrão recomendado (usa a gravação aprovada em uso); `FIXO` só quando há necessidade pedagógica de preservar uma gravação específica. Ambos são suportados e validados. | idem | `ESQUEMA.md` seções 2 e 5.5 |
| D-004 | 2026-10-30 | Privacidade: o repositório público recebe estrutura, documentação, scripts e exemplos fictícios. **Não** recebe conteúdo comercial não aprovado, dados pessoais, capítulos pagos, áudios comerciais ou material protegido. | idem | `PROTOCOLO.md` seção 10 |
| D-005 | 2026-10-30 | Competência de validação: linguística (revisor com competência em japonês); tradução (fidelidade de sentido e naturalidade em português); pedagógica (nível, clareza, coerência dos exercícios); roteiro (texto e sequência falada); gravação (fidelidade, pronúncia, qualidade técnica); escuta (adequação da gravação ao exercício e à velocidade). Claude e ChatGPT não substituem automaticamente um revisor nativo; a validação humana deve ser possível e identificável. | idem | `ESQUEMA.md` seção 5.2; `PROTOCOLO.md` seção 1 |
| D-006 | 2026-10-30 | Aplicação de D-005 no verificador, definida pelo executor e sujeita a revisão: aprovação final de `LINGUISTICA`, `TRADUCAO` e `GRAVACAO` só por `HUMANO_JAPONES`; de `PEDAGOGICA`, `ROTEIRO` e `ESCUTA` por `HUMANO_JAPONES` ou `HUMANO_RESPONSAVEL`. Aprovação de IA conta como `APROVADO_AUXILIAR`. Validação humana exige `revisor_identificacao`. | proposta do Claude a partir de D-005; **aguarda confirmação do responsável humano** | `verificar_dados.py` (`APROVADORES_FINAIS`) |
| D-007 | 2026-10-30 | Áudios comerciais ficam fora do repositório. O verificador confere os bytes com `--raiz-audio` apontando para uma pasta local; sem ela, o conteúdo dos áudios é registrado como não conferido. | consequência de D-004, definida pelo executor | `verificar_dados.py`; `ESQUEMA.md` seção 5.4 |
| D-008 | 2026-10-30 | O Volume 1 é exclusivamente um livro estático em PDF. Não produzir áudio, narração, QR codes, vídeo, atividades externas, site, aplicativo, plataforma ou qualquer interação fora do PDF. | instrução escrita do responsável humano nesta conversa | todo o projeto; `README.md`, `PROTOCOLO.md`, `ESTADO.md` |

Nenhuma decisão de merge ou publicação foi registrada até esta data.
