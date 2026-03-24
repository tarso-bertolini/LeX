#!/usr/bin/env python3
"""Automated checklist for Phase 1 requirement coverage."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SUITE = ROOT / "requirements_suite.rpn"
OUT = ROOT / "requirements_output.s"


def check(flag: bool, label: str, failures: list[str]) -> None:
    status = "PASS" if flag else "FAIL"
    print(f"[{status}] {label}")
    if not flag:
        failures.append(label)


def main() -> int:
    failures: list[str] = []

    run = subprocess.run(
        [sys.executable, str(ROOT / "compiler.py"), str(SUITE), str(OUT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    check(run.returncode == 0, "compiler executes over full suite", failures)
    if run.returncode != 0:
        print(run.stdout)
        print(run.stderr)
        return 1

    asm = OUT.read_text(encoding="utf-8")
    py = (ROOT / "compiler.py").read_text(encoding="utf-8")

    check("def state_start" in py and "def state_number" in py and "def state_identifier" in py,
          "DFA lexer state functions present", failures)
    check("import re" not in py,
          "no regex module usage", failures)

    check("vadd.f64" in asm, "addition codegen", failures)
    check("vsub.f64" in asm, "subtraction codegen", failures)
    check("vmul.f64" in asm, "multiplication codegen", failures)
    check("vdiv.f64" in asm, "real division codegen", failures)
    check("sdiv" in asm, "integer division codegen", failures)
    check("mls" in asm, "integer remainder codegen", failures)
    check("pow_pos_int:" in asm, "power helper emitted", failures)

    check(".data" in asm, "data section emitted", failures)
    check("mem_VAR:" in asm, "memory symbol allocation emitted", failures)
    check("res_" in asm, "result history symbols emitted", failures)

    check("placeholder" not in asm,
          "no placeholder assembly remains", failures)

    if failures:
        print("\nValidation failed items:")
        for item in failures:
            print(f"- {item}")
        return 2

    print("\nAll automated checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
