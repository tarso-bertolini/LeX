# Analisador Lexico (AFD) e Gerador ARMv7

Implementacao da Fase 1 com:

- analisador lexico por AFD (cada estado e uma funcao);
- parser de expressoes RPN com parenteses aninhados;
- gerador de Assembly ARMv7 DEC1-SOC com VFP em 64 bits;
- validacao automatica dos requisitos principais;
- demonstracao web user-friendly com Node.js + npm.

## Requisitos

- Python 3
- Node.js + npm

## Uso no terminal

Gerar assembly a partir de arquivo:

```bash
python3 compiler.py tests_example.rpn output_example.s
```

Modo stdin (usado pela demo web):

```bash
echo "((3.14 2.0 *) (VAR MEM) +)" | python3 compiler.py --stdin
```

## Validacao automatica

Executa o compilador sobre uma suite completa (`requirements_suite.rpn`) e verifica cobertura de operadores/comandos:

```bash
python3 validate_requirements.py
```

Via npm script:

```bash
npm run validate
```

## Demo web (Node + npm)

Instalar dependencias:

```bash
npm install
```

Subir servidor:

```bash
npm start
```

Abrir: `http://localhost:3000`

## Arquivos principais

- `compiler.py`: lexer DFA, parser, codegen ARMv7.
- `tests_example.rpn`: exemplo exigido no enunciado.
- `output_example.s`: assembly do exemplo exigido.
- `requirements_suite.rpn`: suite de validacao de requisitos.
- `requirements_output.s`: assembly gerado para a suite completa.
- `validate_requirements.py`: checklist automatizado.
- `server.js` e `public/*`: demonstracao web.

## Cobertura implementada

- Sem `re`, `lex`, `yacc` ou parser pronto.
- Tokens: `LPAREN`, `RPAREN`, `NUMBER`, `OPERATOR`, `IDENTIFIER`, `RES`.
- Operadores: `+`, `-`, `*`, `/`, `//`, `%`, `^`.
- Comandos: `(N RES)`, `(V MEMVAR)`, `(MEMVAR)`.
- Compatibilidade com sintaxe de exemplo legado: `(VAR MEM)`.
- Secao `.data` para historico de resultados (`res_*`) e memorias (`mem_*`).

## Observacao sobre hardware do Cpulator

O projeto gera assembly compativel com ARMv7 DEC1-SOC (VFP). Integracao especifica com periféricos (display/leds/botoes/chaves) depende do mapeamento de I/O adotado no ambiente de execucao e deve ser ajustada conforme o roteiro da disciplina.
