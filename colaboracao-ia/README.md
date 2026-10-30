# Colaboração entre IAs · O Japonês por Trás das Palavras

Infraestrutura de produção e revisão do projeto. **Claude** produz e corrige, **ChatGPT** revisa de forma independente e o **responsável humano** decide. O GitHub é a fonte compartilhada do estado e do histórico.

> **Repositório público.** Aqui entram estrutura, documentação, scripts e exemplos fictícios. Não entram conteúdo comercial não aprovado, capítulos pagos, áudios comerciais, dados pessoais nem credenciais (decisão D-004).
>
> Esta pasta fica fora de `docs/`: se o GitHub Pages publicar `docs/`, nada daqui vira página.

## Por onde começar

| Quero… | Leia |
|---|---|
| saber o que está pronto e o que falta | [`ESTADO.md`](ESTADO.md) (fonte única desse status) |
| entender como Claude e ChatGPT trabalham juntos | [`PROTOCOLO.md`](PROTOCOLO.md) |
| instruções do papel de revisor (ChatGPT) | [`instrucoes/CHATGPT_REVISOR.md`](instrucoes/CHATGPT_REVISOR.md) |
| instruções do papel de executor (Claude) | [`instrucoes/CLAUDE_EXECUTOR.md`](instrucoes/CLAUDE_EXECUTOR.md) |
| conhecer os dados, IDs, regras e dependências | [`01_dados/ESQUEMA.md`](01_dados/ESQUEMA.md) |
| saber o que os testes cobrem e os resultados | [`02_testes/COBERTURA.md`](02_testes/COBERTURA.md) |
| ver as decisões tomadas | [`04_historico/DECISOES.md`](04_historico/DECISOES.md) |
| ver o histórico de mudanças e commits | [`04_historico/CHANGELOG.md`](04_historico/CHANGELOG.md) |
| ver os apontamentos e a situação de cada um | [`03_revisao/apontamentos.csv`](03_revisao/apontamentos.csv) |

## Estrutura

```
colaboracao-ia/
├── README.md                     ← este índice
├── ESTADO.md                     ← implementado / testado / pendente / fora do escopo
├── PROTOCOLO.md                  ← regras de colaboração entre as IAs
├── .gitignore
├── instrucoes/
│   ├── CHATGPT_REVISOR.md
│   └── CLAUDE_EXECUTOR.md
├── 01_dados/                     ← fonte oficial dos dados (CSV UTF-8, D-001); hoje só cabeçalhos
│   ├── ESQUEMA.md
│   ├── frases.csv · exercicios.csv · respostas.csv
│   ├── audios.csv · audio_segmentos.csv · arquivos_audio.csv · exercicio_audios.csv
│   └── validacoes.csv
├── 02_testes/
│   ├── COBERTURA.md
│   ├── test_verificar_dados.py   ← suíte automatizada (unittest)
│   ├── dados_ficticios.py        ← gerador de dados fictícios isolados (capítulo 99)
│   ├── mutacoes.py               ← prova de que a suíte detecta defeitos
│   └── teste-html-smoke.js       ← teste Playwright de materiais HTML
├── 03_revisao/                   ← pedidos, relatórios, respostas, apontamentos.csv
├── 04_historico/
│   ├── CHANGELOG.md
│   └── DECISOES.md
└── 05_ferramentas/
    ├── verificar_dados.py        ← verificador de integridade e dependências
    └── verificar_originais.py    ← confere que os 4 arquivos originais não mudaram
```

## Comandos

Requer Python 3.9 ou superior (só a biblioteca padrão). O teste HTML requer Node e Playwright.

```
# toda a suíte de testes (dados fictícios isolados)
python3 -m unittest discover -s colaboracao-ia/02_testes -p 'test_*.py'

# teste de mutação (a suíte precisa detectar cada defeito introduzido)
python3 colaboracao-ia/02_testes/mutacoes.py

# verificar os CSVs oficiais (0 = ok, 1 = erro, 2 = pendências, 3 = uso)
python3 colaboracao-ia/05_ferramentas/verificar_dados.py verificar [--raiz-audio PASTA_DOS_AUDIOS]

# depois de editar CSVs: gravar impressões e subir versões
python3 colaboracao-ia/05_ferramentas/verificar_dados.py atualizar-impressoes

# registro de apontamentos e integridade dos originais
python3 colaboracao-ia/05_ferramentas/verificar_dados.py verificar-apontamentos
python3 colaboracao-ia/05_ferramentas/verificar_originais.py

# teste de fumaça de uma página HTML
node colaboracao-ia/02_testes/teste-html-smoke.js "arquivo.html" [--saida pasta]
```

## IDs

| Tipo | Formato | Exemplo |
|---|---|---|
| Frase | `J<cap>-<nº>` | `J04-14` |
| Exercício | `X<cap>-<rótulo>` | `X04-R1` |
| Resposta | `X<cap>-<rótulo>-<letra ou nº>` | `X04-R1-a` |
| Faixa de áudio | `A<cap>-<nº>` | `A04-03` |
| Gravação | `<faixa>_v<velocidade>_r<versão>_t<tomada>` | `A04-03_v080_r2_t1` |
| Validação | `V-<nº>` | `V-0001` |
| Cartão de revisão | `K<cap>-<nº>` | `K04-07` |
| Apontamento | `C<cap>-<ÁREA>-<nnn>`, `P<nn>`, `CL-<nn>` | `C04-LING-001` |
| Decisão | `D-<nnn>` | `D-002` |

IDs nunca são reutilizados.
