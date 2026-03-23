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


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: python compiler.py <input.rpn>")
        return 1

    with open(argv[1], "r", encoding="utf-8") as src:
        text = src.read()

    lexer = DFALexer(text)
    tokens = lexer.lex()
    for tok in tokens:
        print(f"{tok.kind:12s} | {tok.lexeme!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
