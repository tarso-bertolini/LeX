# Validation Report - Fase 1

Data: 2026-03-12

## Resultado geral

- Status: `PASS` para requisitos automatizaveis.
- Comando executado: `python3 validate_requirements.py`.

## Checklist por requisito

- Leitura de arquivo com uma expressao por linha: `PASS`.
- Analise lexico por AFD com estados em funcoes: `PASS`.
- Proibicao de regex/parsers prontos: `PASS`.
- Parser RPN com parenteses aninhados: `PASS`.
- Operadores `+ - * / // % ^`: `PASS`.
- Comandos `(N RES)`, `(V MEM)`, `(MEM)`: `PASS`.
- Geracao assembly ARMv7 com VFP double (`vldr.f64`, `vadd.f64`, ...): `PASS`.
- Secao `.data` com alocacao de memorias e historico: `PASS`.
- Exemplo exigido `((3.14 2.0 *) (VAR MEM) +)`: `PASS`.
- Demo web com Node/npm para uso amigavel: `PASS`.

## Evidencias

- Implementacao principal: `compiler.py`.
- Suite de cobertura: `requirements_suite.rpn`.
- Saida da suite: `requirements_output.s`.
- Exemplo pedido: `tests_example.rpn` -> `output_example.s`.
- Demo web: `server.js`, `public/index.html`, `public/app.js`, `public/styles.css`.

## Nota de validacao manual

- Integracao com periféricos do Cpulator (display/leds/botoes/chaves) depende de mapeamento de I/O especifico da placa/simulador e deve ser confirmada em execucao no ambiente da disciplina.
