"""Docs."""


from collections import defaultdict
from typing import Final, Iterator
from enum import IntEnum, auto
import re
import sys
import math

import argparse

_TERM: Final[str] = r"(?:\d+\*?\1(?:\^\d+)?|\d+|\1(?:\^\d+)?)"
POLYNOMIAL_RE: Final = re.compile(
    rf"[A-Za-z]\(([a-z])\)=[+-]?{_TERM}(?:[+-]{_TERM})*"
)


def poly_validade_source(source: str) -> bool:
    return POLYNOMIAL_RE.fullmatch(source.replace(" ", "")) is not None

def poly_get_coeff(source: str) -> list[int]:
    if not poly_validade_source(source):
        sys.stderr.write(f"ERROR: Invalid polynomal formula, ({source})\n")
        sys.stderr.write(f" > Write \"P(x)=45x^2 + 37x + 6\" format.\n")
        sys.exit(1)

    if '-' in source:
        sys.stderr.write(f"ERROR: Subtraction is not supported for now.\n")
        sys.exit(1)

    source = source.replace(" ", "")
    head = re.fullmatch(r"[A-Za-z]\(([a-z])\)=(.+)", source)
    if not head:
        sys.stderr.write(f"ERROR: Invalid header.\n")
        sys.stderr.write(f" > Write \"P(x) = ...\" format.\n")
        sys.exit(1)
    
    var, body = head.groups()

    term_re = re.compile(
        rf"(?P<sign>[+-]?)(?=\d|{var})"
        rf"(?:(?P<coef>\d+)(?:\*(?={var}))?)?"
        rf"(?:(?P<var>{var})(?:\^(?P<exp>\d+))?)?"
    )

    coeffs: dict[int, int] = defaultdict(int)
    position: int = 0

    TERM_SIGN: Final[str] = "sign"
    TERM_COEF: Final[str] = "coef"
    TERM_VAR: Final[str] = "var"
    TERM_EXP: Final[str] = "exp"

    class Term:
        def __init__(self, data) -> None:
            self.__data = data

        @property
        def start(self) -> int:
            return self.__data.start()
        
        @property
        def end(self) -> int:
            return self.__data.end()
        
        @property
        def sign(self) -> str:
            return self.__data[TERM_SIGN]
        
        @property
        def coef(self) -> str:
            return self.__data[TERM_COEF]
        
        @property
        def var(self) -> str:
            return self.__data[TERM_VAR]
        
        @property
        def exp(self) -> str:
            return self.__data[TERM_EXP]

    def body_matchs() -> Iterator[Term]:
        for match in term_re.finditer(body): yield Term(match)

    for term in body_matchs():
        if term.start != position:
            sys.stderr.write(f"ERROR: Unexpected text at {body[position:term.start()]!r}.\n")
            sys.exit(1)
        
        if position > 0 and not term.sign:
            sys.stderr.write(f"ERROR: Missing operator between terms.\n")
            sys.exit(1)

        position = term.end
        
        coef = int(term.coef) if term.coef else 1

        if term.sign == '-':
            sys.stderr.write(f"WARNING: Using a negative coeff, not implemented.\n")
            coef = -coef

        if term.var is None:
            degree = 0

        else:
            degree = int(term.exp) if term.exp else 1 
        
        coeffs[degree] += coef

    if position != len(body):
        sys.stderr.write(f"ERROR: Unexpected text at {body[position:]!r}.\n")
        sys.exit(1)

    # TODO: Add a better factorization.
    if max(coeffs) > 2:
        sys.stderr.write(f"ERROR: Not implemented cases for degree greater than 2.\n")
        sys.exit(1)

    return dict(coeffs)

def poly_eval_at(coeffs: dict[int, int], x: int) -> float:
    return sum(coeffs[exp] * math.pow(x, exp) for exp in coeffs)

def poly_get_k(coeffs: dict[int, int]) -> int:
    k: float = poly_eval_at(coeffs, 10)
    if not k.is_integer():
        sys.stderr.write(f"ERROR: Something went wrong, expected integer k.\n")
        sys.exit(1)

    return int(k)

def k_factors(k: int) -> list[tuple[int, int]]:
    m = math.ceil(math.sqrt(k))
    return [(n, k//n) for n in range(1, m + 1) if k % n == 0]

def factor_to_formula(factor: tuple[int, int]) -> None:
    digits = lambda number: [int(digit) for digit in reversed(str(number))]

    def side(n: int) -> None:
        data = digits(n)
        for exp, digit in enumerate(data):
            print(digit, end='')
            if exp == 1:
                print("x", end='')

            elif exp > 1:
                print(f"x^{exp}", end='')
            if exp + 1 < len(data):
                print(" + ", end='')
        print()
    side(factor[0])
    side(factor[1])

def poly_have_real_sol(coeffs: dict[int, int]) -> bool:
    if max(coeffs) > 2:
        sys.stderr.write(f"ERROR: Not implemented cases for degree greater than 2.\n")
        sys.exit(1)

    a: float = coeffs[2] if 2 in coeffs else 0
    b: float = coeffs[1] if 1 in coeffs else 0
    c: float = coeffs[0] if 0 in coeffs else 0

    d: float = (b**2) - 4*a*c
    return d >= 0

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='PolyBase',
        description='factorize a polynomial',
    )
    parser.add_argument(
        'poly',
        help="the expression",
        type=str
    )
    args = parser.parse_args()
    coeffs: dict[int, int] = poly_get_coeff(args.poly)
    if not poly_have_real_sol(coeffs):
        sys.stderr.write(f"ERROR: This polynomal don't have real solution.\n")
        sys.exit(1)

    k: int = poly_get_k(coeffs)
    print("P(10) =", k)
    print(k_factors(k))
    # TODO: Find the correct factorization.


if __name__ == "__main__":
    main()
