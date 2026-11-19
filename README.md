# Citizen Assist AI

Assistente de terminal, feito em Python, que orienta **jovens no primeiro emprego** com informações verificadas, mostrando a fonte e sem coletar dados pessoais.

## Integrantes

| Nome | RM |

| Matheus Carpinheiro Moreno | 571770 |

| Ângelo Malta Reina | 570769 |

| Gustavo Mendonça Duarte | 570561 |

## Público e problema

Quem consegue o primeiro emprego costuma ter dúvidas simples, mas importantes: como tirar o CPF, como emitir a Carteira de Trabalho Digital, o que é o exame admissional, quando o salário deve ser pago, como funcionam férias, 13º e FGTS. A informação existe, mas está espalhada, em linguagem técnica e misturada com sites que parecem oficiais e não são. O assistente reúne respostas curtas, em linguagem simples, sempre com a fonte oficial.

## ODS relacionados

- ODS 8: Trabalho decente e crescimento econômico
- ODS 10: Redução das desigualdades
- ODS 16: Paz, justiça e instituições eficazes (acesso à informação)

## Como executar

Requisitos: Python 3.8 ou mais novo. Não usa bibliotecas externas.

```
python main.py
```

Menu: fazer uma pergunta, navegar por categorias, ver indicadores, exportar CSV e sair. Ao sair, o assistente pede uma nota de facilidade de 1 a 5.

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py
├── orientacao.py          # classe Orientacao
├── base_conhecimento.py   # classe BaseConhecimento (JSON, normalizar, busca)
├── assistente.py          # classe Assistente (atendimento, histórico, indicadores, CSV)
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    ├── notas.json
    └── atendimentos.csv
```

## Regra de pontuação

A pergunta e os textos da base são normalizados (minúsculas, sem acentos e sem pontuação). Depois cada orientação recebe pontos:

| Regra | Pontos |
|---|---|
| Palavra-chave da orientação que aparece na pergunta | +3 |
| Palavra da pergunta (4 letras ou mais) que aparece no título | +1 |

| Melhor pontuação | Resultado |
|---|---|
| 6 pontos ou mais | Confiança ALTA |
| 3 a 5 pontos | Confiança MÉDIA |
| Nenhuma com 3 pontos | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)`, da maior para a menor pontuação. O assistente mostra a melhor orientação e até duas alternativas com 3 pontos ou mais.

**Ajustes feitos em relação ao enunciado:**
- Palavras muito comuns (como, para, qual, onde, quando, preciso, posso, quero, tenho, minha, quanto) não valem ponto no título, porque aparecem em perguntas de qualquer assunto.
- Cada palavra da pergunta conta no máximo 1 ponto no título, mesmo se repetida.
- As alternativas só aparecem com 3 pontos ou mais, para não sugerir orientações pouco relacionadas.

## Regras de atendimento

- Entradas inválidas (opção fora da faixa, letras, resposta vazia, s/n inválido) nunca encerram o programa.
- Perguntas com 8 ou mais dígitos ou com `@` são recusadas e não são registradas.
- Toda resposta mostra a fonte, a data de verificação e o aviso de que o assistente não é canal oficial.
- Base ausente ou corrompida não trava o programa: ele mostra uma mensagem e encerra. Histórico ou notas corrompidos são recriados.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` (data, origem, pergunta, id da orientação, se encontrou, se ajudou, tentativas e tempo em segundos). Um atendimento começa na primeira pergunta válida e termina quando a pessoa responde "s" ou volta com 0. As notas de facilidade ficam em `data/notas.json`.

Indicadores calculados: resposta encontrada (%), taxa de acerto (%), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (1 a 5) e lista de dúvidas sem solução.

O CSV é exportado com `csv.DictWriter` para `data/atendimentos.csv` (pelo menu e automaticamente ao sair). O arquivo usa UTF-8 com BOM para o Excel abrir os acentos corretamente.

## Integrações com outras disciplinas

Não houve integração com outras diciplinas

## Fontes consultadas

- Receita Federal: https://www.gov.br/receitafederal
- Ministério do Trabalho e Emprego: https://www.gov.br/trabalho-e-emprego
- Tribunal Superior Eleitoral: https://www.tse.jus.br
- Governo Digital (conta gov.br): https://www.gov.br/governodigital/pt-br/identidade/conta-gov-br
- Caixa (FGTS): https://www.caixa.gov.br/beneficios-trabalhador/fgts/Paginas/default.aspx
- CLT (Decreto-Lei 5.452/1943): https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm
- Lei 7.418/1985 (vale-transporte): https://www.planalto.gov.br/ccivil_03/leis/l7418.htm
- Lei 4.090/1962 (13º salário): https://www.planalto.gov.br/ccivil_03/leis/l4090.htm

## Resultado do teste com usuários



| Indicador | Resultado |
|---|---|
| Pessoas testadas | 4 |
| Atendimentos | 4 |
| Resposta encontrada (%) | 100% |
| Taxa de acerto (%) | 50% |
| Tempo médio para encontrar (s) | 51,45 |
| Tentativas por atendimento | 1 |
| Facilidade de uso (1 a 5) | 5 |

**Dúvidas sem solução:** 

**Melhoria feita a partir do teste:** 

## Limitações

- A busca é por regras: só entende palavras-chave e palavras do título, não o sentido da frase.
- O assistente só responde o que está na base (14 orientações). Perguntas fora dela caem em "não encontrei".
- Leis e procedimentos mudam. Cada orientação tem a data de verificação, e a informação deve ser conferida na fonte oficial.
- Não é canal oficial e não substitui um atendimento jurídico ou do governo.

