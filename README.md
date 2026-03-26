# Analisador Lexico (AFD) e Gerador ARMv7

**Instituição:** PUCPR - Pontifícia Universidade Católica do Paraná  
**Disciplina:** Construção de Interpretadores  
**Professor:** Frank Alcantara  
**Grupo Canvas:** LeX  
**Alunos:**
- Eduardo Contin (GitHub: [EduContin](https://github.com/EduContin))
- Tarso Bertolini (GitHub: [tarso-bertolini](https://github.com/tarso-bertolini))

---

Implementamento da Fase 1 com:
- Analisador lexico por AFD (cada estado e uma funcao, sem regex);
- Parser de expressoes RPN com parenteses aninhados;
- Simulador Python de 64-bits IEEE754 para validacao (executa os calculos localmente);
- Gerador de Assembly ARMv7 DEC1-SOC com VFP em 64 bits para Cpulator;
- Demonstracao web user-friendly com Node.js + npm.

Aviso: Durante o desenvolvimento, todas as contribuições dos alunos foram registradas em Pull Requests e Issues deste repositório, garantindo divisão correta das atribuições estipuladas no documento.

## Como Compilar, Executar e Testar

O programa recebe um arquivo de entrada em formato `.rpn` e irá gerar o código assembly (`.s`) e registrará os tokens gerados em um arquivo texto (`_tokens.txt`).

1. **Executando o Programa:**

```bash
python3 compiler.py test1.rpn
```

2. **Testes Fornecidos (Minimo 3, 10+ linhas):**
```bash
python3 compiler.py test1.rpn
python3 compiler.py test2.rpn
python3 compiler.py test3.rpn
```

3. **Validação Automática:**
Executa o compilador sobre testes de cobertura:
```bash
python3 validate_requirements.py --target compiler.py
```
