#!/usr/bin/env python3
"""RPN lexer based on DFA with states as functions.

Implementation constraints honored:
- No regex/parsing libraries.
- Lexer is a deterministic finite automaton (DFA), where each state is an isolated function.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable, List, Optional


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


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: python compiler.py <input.rpn>")
        return 1

    with open(argv[1], "r", encoding="utf-8") as src:
        text = src.read()

    lexer = DFALexer(text)
    tokens = lexer.lex()
    parser = Parser(tokens)
    exprs = parser.parse_program()
    for i, expr in enumerate(exprs):
        print(f"Line {i}: {expr}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
