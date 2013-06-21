""":mod:`stencil_lang.interpreter.tokens` -- Tokens for lexing and parsing
"""

from stencil_lang.tokens import NUMBERS

LITERALS = [
    'STO',
    'PR',
    'ADD',
    'CMX',
    'PMX',
    'SMX',
    'PDE',
]
"""Language literals, i.e., the name is the same as the value."""

TOKENS = NUMBERS.copy()
# Update tokens with literals. Beware that any token duplicated in tokens and
# literals will be overwritten with the value from literals.
for literal in LITERALS:
    TOKENS[literal] = literal
