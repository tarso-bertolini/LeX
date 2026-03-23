#!/usr/bin/env python3
"""RPN lexer/parser and ARMv7 assembly generator.

Implementation constraints honored:
- No regex/parsing libraries.
- Lexer is a deterministic finite automaton (DFA), where each state is an isolated function.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


TOKEN_LPAREN = "LPAREN"
TOKEN_RPAREN = "RPAREN"
TOKEN_NUMBER = "NUMBER"
TOKEN_OPERATOR = "OPERATOR"
TOKEN_IDENTIFIER = "IDENTIFIER"
TOKEN_RES = "RES"
TOKEN_EOL = "EOL"


@dataclass
class Token:
    kind: str
    lexeme: str
    line: int
    column: int


class LexerError(Exception):
    pass


class DFALexer:
    def __init__(self, text: str):
        self.text = text
        self.index = 0
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_col = 1
        self.buffer: List[str] = []
        self.tokens: List[Token] = []

    def lex(self) -> List[Token]:
        state: Callable[[], Optional[Callable]] = self.state_start
        while state is not None:
            state = state()
        self.tokens.append(Token(TOKEN_EOL, "", self.line, self.column))
        return self.tokens

    def peek(self) -> Optional[str]:
        if self.index >= len(self.text):
            return None
        return self.text[self.index]

    def advance(self) -> Optional[str]:
        ch = self.peek()
        if ch is None:
            return None
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def emit(self, kind: str, lexeme: str) -> None:
        self.tokens.append(Token(kind, lexeme, self.start_line, self.start_col))

    def begin(self) -> None:
        self.start_line = self.line
        self.start_col = self.column
        self.buffer = []

    def state_start(self):
        ch = self.peek()
        if ch is None:
            return None
        if ch in " \t\r":
            self.advance()
            return self.state_start
        if ch == "\n":
            self.advance()
            self.emit(TOKEN_EOL, "")
            return self.state_start
        if ch == "(":
            self.begin()
            self.advance()
            self.emit(TOKEN_LPAREN, "(")
            return self.state_start
        if ch == ")":
            self.begin()
            self.advance()
            self.emit(TOKEN_RPAREN, ")")
            return self.state_start
        if ch in "+-":
            self.begin()
            self.buffer.append(self.advance() or "")
            nxt = self.peek()
            if nxt is not None and (nxt.isdigit() or nxt == "."):
                return self.state_number
            if (self.buffer[0] in "+-") and (nxt is None or nxt.isspace() or nxt in "()"):
                self.emit(TOKEN_OPERATOR, self.buffer[0])
                return self.state_start
            raise LexerError(f"Invalid token at line {self.line}, col {self.column}")
        if ch.isdigit() or ch == ".":
            self.begin()
            return self.state_number
        if ch.isalpha() and ch.isupper():
            self.begin()
            return self.state_identifier
        if ch in "*/%^":
            self.begin()
            first = self.advance() or ""
            if first == "/" and self.peek() == "/":
                self.advance()
                self.emit(TOKEN_OPERATOR, "//")
            else:
                self.emit(TOKEN_OPERATOR, first)
            return self.state_start
        raise LexerError(f"Unexpected character {ch!r} at line {self.line}, col {self.column}")

    def state_number(self):
        seen_dot = False
        seen_digit = False

        while True:
            ch = self.peek()
            if ch is None:
                break
            if ch.isdigit():
                seen_digit = True
                self.buffer.append(self.advance() or "")
                continue
            if ch == ".":
                if seen_dot:
                    break
                seen_dot = True
                self.buffer.append(self.advance() or "")
                continue
            break

        if not seen_digit:
            raise LexerError(f"Invalid NUMBER at line {self.start_line}, col {self.start_col}")

        self.emit(TOKEN_NUMBER, "".join(self.buffer))
        return self.state_start

    def state_identifier(self):
        while True:
            ch = self.peek()
            if ch is None:
                break
            if ch.isalpha() and ch.isupper():
                self.buffer.append(self.advance() or "")
                continue
            break

        value = "".join(self.buffer)
        if value == "RES":
            self.emit(TOKEN_RES, value)
        else:
            self.emit(TOKEN_IDENTIFIER, value)
        return self.state_start


class ParserError(Exception):
    pass


class CodegenError(Exception):
    pass


class Expr:
    pass


@dataclass
class Number(Expr):
    value: str


@dataclass
class MemLoad(Expr):
    name: str


@dataclass
class MemStore(Expr):
    name: str
    value: Expr


@dataclass
class ResRef(Expr):
    offset: int


@dataclass
class Binary(Expr):
    op: str
    left: Expr
    right: Expr


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.index = 0

    def parse_program(self) -> List[Expr]:
        lines: List[Expr] = []
        while not self.at_end():
            if self.match(TOKEN_EOL):
                continue
            lines.append(self.parse_expr())
            self.consume(TOKEN_EOL, "Expected end-of-line after expression")
        return lines

    def parse_expr(self) -> Expr:
        if self.match(TOKEN_NUMBER):
            return Number(self.previous().lexeme)

        if self.match(TOKEN_LPAREN):
            expr = self.parse_list_expression()
            self.consume(TOKEN_RPAREN, "Expected ')' to close expression")
            return expr

        tok = self.peek()
        raise ParserError(f"Unexpected token {tok.kind} at line {tok.line}, col {tok.column}")

    def parse_list_expression(self) -> Expr:
        items: List[Expr | Token] = []
        while not self.check(TOKEN_RPAREN):
            if self.at_end() or self.check(TOKEN_EOL):
                tok = self.peek()
                raise ParserError(f"Unclosed '(' at line {tok.line}, col {tok.column}")

            if self.match(TOKEN_OPERATOR, TOKEN_RES, TOKEN_IDENTIFIER):
                items.append(self.previous())
                continue
            items.append(self.parse_expr())

        # (MEMNAME) -> load memory
        if len(items) == 1 and isinstance(items[0], Token) and items[0].kind == TOKEN_IDENTIFIER:
            return MemLoad(items[0].lexeme)

        # (N RES) -> result of N previous lines
        if (
            len(items) == 2
            and isinstance(items[0], Expr)
            and isinstance(items[1], Token)
            and items[1].kind == TOKEN_RES
        ):
            if not isinstance(items[0], Number):
                raise ParserError("RES command requires an integer literal")
            raw = items[0].value
            if raw.startswith("+"):
                raw = raw[1:]
            if raw.startswith("-") or (not raw.isdigit()):
                raise ParserError("RES offset must be a non-negative integer literal")
            offset = int(raw)
            if offset < 0:
                raise ParserError("RES offset must be non-negative")
            return ResRef(offset)

        # Backward-compatible sample syntax: (X MEM) -> load memory X
        if (
            len(items) == 2
            and isinstance(items[0], Token)
            and isinstance(items[1], Token)
            and items[0].kind == TOKEN_IDENTIFIER
            and items[1].kind == TOKEN_IDENTIFIER
            and items[1].lexeme == "MEM"
        ):
            return MemLoad(items[0].lexeme)

        # (V MEMNAME) -> store expression V in MEMNAME and return V
        if (
            len(items) == 2
            and isinstance(items[0], Expr)
            and isinstance(items[1], Token)
            and items[1].kind == TOKEN_IDENTIFIER
        ):
            return MemStore(items[1].lexeme, items[0])

        # (A B op)
        if (
            len(items) == 3
            and isinstance(items[0], Expr)
            and isinstance(items[1], Expr)
            and isinstance(items[2], Token)
            and items[2].kind == TOKEN_OPERATOR
        ):
            return Binary(items[2].lexeme, items[0], items[1])

        raise ParserError("Invalid parenthesized expression form")

    def at_end(self) -> bool:
        return self.index >= len(self.tokens)

    def peek(self) -> Token:
        return self.tokens[self.index]

    def previous(self) -> Token:
        return self.tokens[self.index - 1]

    def check(self, kind: str) -> bool:
        if self.at_end():
            return False
        return self.peek().kind == kind

    def match(self, *kinds: str) -> bool:
        if self.at_end():
            return False
        if self.peek().kind in kinds:
            self.index += 1
            return True
        return False

    def consume(self, kind: str, message: str) -> Token:
        if self.check(kind):
            self.index += 1
            return self.previous()
        tok = self.peek()
        raise ParserError(f"{message} at line {tok.line}, col {tok.column}")


class ARMv7Codegen:
    def __init__(self):
        self.mem_symbols: Dict[str, str] = {}
        self.float_literals: Dict[str, str] = {}
        self.res_labels: List[str] = []
        self.text_lines: List[str] = []
        self.reg_pool = [f"d{i}" for i in range(14, -1, -1)]
        self.current_line_index = 0
        self.label_counter = 0
        self.uses_pow = False

    def compile(self, exprs: List[Expr]) -> str:
        self.res_labels = [f"res_{i}" for i in range(len(exprs))]

        self.text_lines.append(".global _start")
        self.text_lines.append(".text")
        self.text_lines.append("_start:")

        for idx, expr in enumerate(exprs):
            self.current_line_index = idx
            result_reg = self.emit_expr(expr)
            self.text_lines.append(f"    ldr r10, ={self.res_labels[idx]}")
            self.text_lines.append(f"    vstr.f64 {result_reg}, [r10]")
            self.release_reg(result_reg)

        self.text_lines.append("    b .")

        if self.uses_pow:
            self.emit_pow_helper()

        data_lines = [".data"]
        for label in self.res_labels:
            data_lines.append(f"{label}: .double 0.0")

        for _, label in sorted(self.mem_symbols.items(), key=lambda x: x[1]):
            data_lines.append(f"{label}: .double 0.0")

        for value, label in sorted(self.float_literals.items(), key=lambda x: x[1]):
            data_lines.append(f"{label}: .double {value}")

        return "\n".join(self.text_lines + [""] + data_lines) + "\n"

    def emit_expr(self, expr: Expr) -> str:
        if isinstance(expr, Number):
            reg = self.allocate_reg()
            lit = self.get_literal(expr.value)
            self.text_lines.append(f"    ldr r10, ={lit}")
            self.text_lines.append(f"    vldr.f64 {reg}, [r10]")
            return reg

        if isinstance(expr, MemLoad):
            reg = self.allocate_reg()
            mem = self.get_mem_label(expr.name)
            self.text_lines.append(f"    ldr r10, ={mem}")
            self.text_lines.append(f"    vldr.f64 {reg}, [r10]")
            return reg

        if isinstance(expr, MemStore):
            reg = self.emit_expr(expr.value)
            mem = self.get_mem_label(expr.name)
            self.text_lines.append(f"    ldr r10, ={mem}")
            self.text_lines.append(f"    vstr.f64 {reg}, [r10]")
            return reg

        if isinstance(expr, ResRef):
            reg = self.allocate_reg()
            target = self.current_line_index - expr.offset - 1
            if target < 0:
                lit = self.get_literal("0.0")
                self.text_lines.append(f"    ldr r10, ={lit}")
                self.text_lines.append(f"    vldr.f64 {reg}, [r10]")
            else:
                self.text_lines.append(f"    ldr r10, ={self.res_labels[target]}")
                self.text_lines.append(f"    vldr.f64 {reg}, [r10]")
            return reg

        if isinstance(expr, Binary):
            left_reg = self.emit_expr(expr.left)
            right_reg = self.emit_expr(expr.right)

            if expr.op == "+":
                self.text_lines.append(f"    vadd.f64 {left_reg}, {left_reg}, {right_reg}")
            elif expr.op == "-":
                self.text_lines.append(f"    vsub.f64 {left_reg}, {left_reg}, {right_reg}")
            elif expr.op == "*":
                self.text_lines.append(f"    vmul.f64 {left_reg}, {left_reg}, {right_reg}")
            elif expr.op == "/":
                self.text_lines.append(f"    vdiv.f64 {left_reg}, {left_reg}, {right_reg}")
            elif expr.op == "^":
                self.uses_pow = True
                self.get_literal("1.0")
                self.text_lines.append(f"    vcvtr.s32.f64 s31, {right_reg}")
                self.text_lines.append("    vmov r0, s31")
                self.text_lines.append(f"    vmov.f64 d0, {left_reg}")
                self.text_lines.append("    bl pow_pos_int")
                self.text_lines.append(f"    vmov.f64 {left_reg}, d0")
            elif expr.op in {"//", "%"}:
                label_id = self.new_label_id()
                zero_label = f"intop_zero_{label_id}"
                done_label = f"intop_done_{label_id}"

                self.text_lines.append(f"    vcvtr.s32.f64 s31, {left_reg}")
                self.text_lines.append("    vmov r0, s31")
                self.text_lines.append(f"    vcvtr.s32.f64 s30, {right_reg}")
                self.text_lines.append("    vmov r1, s30")
                self.text_lines.append("    cmp r1, #0")
                self.text_lines.append(f"    beq {zero_label}")
                self.text_lines.append("    sdiv r2, r0, r1")
                if expr.op == "%":
                    self.text_lines.append("    mls r2, r2, r1, r0")
                self.text_lines.append(f"    b {done_label}")
                self.text_lines.append(f"{zero_label}:")
                self.text_lines.append("    mov r2, #0")
                self.text_lines.append(f"{done_label}:")
                self.text_lines.append("    vmov s31, r2")
                self.text_lines.append(f"    vcvt.f64.s32 {left_reg}, s31")
            else:
                raise CodegenError(f"Unsupported operator: {expr.op}")

            self.release_reg(right_reg)
            return left_reg

        raise CodegenError(f"Unsupported expression type: {type(expr).__name__}")

    def get_mem_label(self, name: str) -> str:
        if name not in self.mem_symbols:
            self.mem_symbols[name] = f"mem_{name}"
        return self.mem_symbols[name]

    def get_literal(self, value: str) -> str:
        norm = value
        if value.startswith("+"):
            norm = value[1:]
        if norm not in self.float_literals:
            self.float_literals[norm] = f"const_{len(self.float_literals)}"
        return self.float_literals[norm]

    def allocate_reg(self) -> str:
        if not self.reg_pool:
            raise CodegenError("Out of VFP registers")
        return self.reg_pool.pop()

    def release_reg(self, reg: str) -> None:
        self.reg_pool.append(reg)

    def new_label_id(self) -> int:
        self.label_counter += 1
        return self.label_counter

    def emit_pow_helper(self) -> None:
        one_label = self.get_literal("1.0")
        self.text_lines.append("pow_pos_int:")
        self.text_lines.append("    push {r4, lr}")
        self.text_lines.append("    vmov.f64 d1, d0")
        self.text_lines.append(f"    ldr r4, ={one_label}")
        self.text_lines.append("    vldr.f64 d0, [r4]")
        self.text_lines.append("    cmp r0, #0")
        self.text_lines.append("    ble pow_done")
        self.text_lines.append("pow_loop:")
        self.text_lines.append("    vmul.f64 d0, d0, d1")
        self.text_lines.append("    subs r0, r0, #1")
        self.text_lines.append("    bgt pow_loop")
        self.text_lines.append("pow_done:")
        self.text_lines.append("    pop {r4, pc}")


def compile_source(text: str) -> str:
    lexer = DFALexer(text)
    tokens = lexer.lex()
    parser = Parser(tokens)
    exprs = parser.parse_program()
    codegen = ARMv7Codegen()
    return codegen.compile(exprs)


def main(argv: List[str]) -> int:
    if len(argv) == 2 and argv[1] == "--stdin":
        text = sys.stdin.read()
        asm = compile_source(text)
        sys.stdout.write(asm)
        return 0

    if len(argv) != 3:
        print("Usage: python compiler.py <input.rpn> <output.s>")
        print("   or: python compiler.py --stdin")
        return 1

    input_path = argv[1]
    output_path = argv[2]

    with open(input_path, "r", encoding="utf-8") as src:
        text = src.read()

    asm = compile_source(text)

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(asm)

    print(f"Assembly generated: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
