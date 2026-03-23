Contexto e Papel:
Aja como um aluno avançado de Ciência da Computação cursando a disciplina de Linguagens Formais e Compiladores. O seu objetivo é resolver o trabalho prático descrito no texto abaixo, utilizando estritamente a base teórica fornecida nos PDFs anexos.

A Tarefa:
Escreva o código completo (em Python ou C++) para o "Analisador Léxico e Gerador de Assembly para ARMv7" descrito na especificação.

Restrições de Implementação (CRÍTICO):
Proibido usar bibliotecas de regex ou parsers prontos (como re, lex, yacc).
O Analisador Léxico deve ser obrigatoriamente implementado como um Autômato Finito Determinístico (AFD) onde cada estado é uma função isolada. As transições (δ) devem ser feitas por meio de chamadas de função ou retorno de ponteiros de função, avaliando o alfabeto caractere por caractere.
O parser deve processar a Notação Polonesa Reversa (RPN) lidando com os parênteses aninhados e identificar os tokens: LPAREN, RPAREN, NUMBER (IEEE 754 de 64 bits), OPERATOR e as palavras-chave RES e MEM.
O Back-End do compilador não deve resolver a matemática, mas sim gerar o código em texto puro de Assembly ARMv7 (compatível com o DEC1-SOC no Cpulator) utilizando o coprocessador VFP para as operações de ponto flutuante de 64 bits (vldr.f64, vadd.f64, etc.).
Crie a seção .data no Assembly gerado para alocar a memória dinâmica exigida pelos comandos (V MEM) e (N RES).
Saída Esperada:
O código fonte comentado, demonstrando claramente onde estão as funções de estado do AFD.
Um arquivo de teste de exemplo com a expressão ((3.14 2.0 *) (VAR MEM) +) e o código Assembly ARMv7 exato que o seu compilador geraria para essa string.
Especificação do Trabalho:

""

---

## Conclusao da Implementacao

Os itens solicitados no enunciado foram implementados neste workspace com os seguintes artefatos:

- `compiler.py`: analisador lexico por AFD (estados como funcoes), parser RPN com parenteses aninhados e gerador de Assembly ARMv7 com VFP.
- `tests_example.rpn`: arquivo de teste contendo `((3.14 2.0 *) (VAR MEM) +)`.
- `output_example.s`: Assembly ARMv7 gerado para o teste acima.
- `README.md`: instrucoes de execucao.

Comando utilizado para gerar o Assembly:

```bash
python3 compiler.py tests_example.rpn output_example.s
```

Assembly ARMv7 gerado (`output_example.s`):

```asm
.global _start
.text
_start:
	ldr r10, =const_0
	vldr.f64 d0, [r10]
	ldr r10, =const_1
	vldr.f64 d1, [r10]
	vmul.f64 d0, d0, d1
	ldr r10, =mem_VAR
	vldr.f64 d1, [r10]
	vadd.f64 d0, d0, d1
	ldr r10, =res_0
	vstr.f64 d0, [r10]
	b .

.data
res_0: .double 0.0
mem_VAR: .double 0.0
const_0: .double 3.14
const_1: .double 2.0
```
26  Fase 1 - Analisador Léxico e Gerador de Assembly para ARMv7
Este trabalho pode ser realizado em grupos de até  alunos. Grupos com mais de 4 membros terão o trabalho anulado. Leia todo este texto antes de começar e siga o seguinte código de ética: você pode discutir as questões com colegas, professores e amigos, consultar livros da disciplina, bibliotecas virtuais ou físicas, e a Internet em geral, em qualquer idioma.


O trabalho deve ser entregue por meio da URL de um repositório público no Github contendo o código-fonte, arquivos de teste, documentação e código Assembly gerado. O repositório deve ser organizado com commits claros e as contribuições de cada aluno devem estar registradas na forma de pull requests.

26.1 Objetivo

Pesquisar e praticar conceitos de analisador léxico para desenvolver um programa em Python, C, ou C++ que processe expressões aritméticas em notação polonesa reversa (RPN), conforme definida neste texto, a partir de um arquivo de texto, utilizando máquinas de estado finito (FSMs) implementadas obrigatoriamente com funções. O programa deve executar as expressões em um ambiente de teste (ex.: o notebook do aluno, ou um computador da instituição) usando como ambiente de execução o simulador disponível em CPULATOR usando obrigatoriamente modelo ARMv7 DEC1-SOC(v16.1).

O seu trabalho será criar um analisador léxico e, a partir do string de tokens gerar um código Assembly, compatível com a arquitetura ARMv7 DEC1-SOC(v16.1) que represente o programa de testes.

26.2 Descrição do Trabalho

Seu objetivo é desenvolver um programa (em Python, C ou C++) capaz de:

Ler um arquivo de texto contendo expressões aritméticas em Escritas RPN, segundo o formato especificado neste documento, com uma expressão por linha. Este arquivo contém o código do programa que será analisado pelo analisador léxico.
Analisar as expressões usando um analisador léxico baseado em Autômatos Finitos Determinísticos, com estados implementados por funções.
Transformar as expressões em um texto contendo o código Assembly para o Cpulator-ARMv7 DEC1-SOC(v16.1). As operações descritas no texto de entrada serão realizadas no Cpulator-ARMv7 DEC1-SOC(v16.1).
Garantir que o resultado do programa, ou as interações necessárias, sejam realizadas por meio das interfaces disponíveis no Cpulator-ARMv7 DEC1-SOC(v16.1) (display, leds, botões, chaves, etc.).
Hospedar o código, arquivos de teste e documentação em um repositório público no GitHub.
26.2.1 Características Especiais da Linguagem
As expressões devem ser escritas em notação RPN, no formato (A B op), no qual A e B são números reais de 64 bits, e op é um operador aritmético entre os listados neste documento. O programa deve suportar apenas as operações aritméticas básicas listadas neste documento e os comandos especiais para manipulação de memória também listados neste documento. Além disso, o programa deve ser capaz de lidar com expressões aninhadas sem limites de aninhadas.

Para a criação da nossa linguagem de programação, considere a seguinte sintaxe:

Considerando que A e B são números reais, e usando o ponto como separador decimal, (ex.: 3.14), teremos:
Operadores suportados na Fase 1:
Adição: + (ex.: (A B +));
Subtração: - (ex.: (A B -));
Multiplicação: * (ex.: (A B *));
Divisão real: / (ex.: (A B /));
Divisão inteira: / (ex.: (A B //) para inteiros);
Resto da divisão inteira: % (ex.: (A B %));
Potenciação: ^ (ex.: (A B ^), onde B é um inteiro positivo );
Todas as operações (exceto divisão inteira e resto) usam números reais codificados em 64 bits segundo a norma IEEE 754. A página Os desafios da norma IEEE 754 contém informações relevantes sobre a norma IEEE 754 para a realização desta tarefa.

Expressões podem ser aninhadas sem limite, por exemplo:

(A (C D *) +): Soma A ao produto de C e D;
((A B *) (D E *) /): Divide o produto de A e B pelo produto de D e E.
((A B +) (C D *) /): Divide a soma de A e B pelo produto de C e D.
Warning
A ordem de precedência das operações segue a ordem de precedência usual em matemática.
26.2.2 Comandos Especiais
A linguagem que estamos criando inclui três comandos especiais para manipulação de memória e resultados:

(N RES): Retorna o resultado da expressão N linhas anteriores (N é um inteiro não negativo).
(V MEM): Armazena o valor real V em uma memória chamada MEM.
(MEM): Retorna o valor armazenado em MEM. Se a memória não foi inicializada, retorna .
Nos quais: - MEM pode ser qualquer conjunto de letras maiúsculas, tal como MEM, VAR, X, etc. - RES é uma keyword da linguagem que estamos criando. A única keyword da linguagem nesta fase.

Warning
Cada arquivo de texto, código fonte da linguagem que estamos criando, representa um escopo independente de memória.
""
