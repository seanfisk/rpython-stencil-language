""":mod:`stencil_lang.tokens` -- Tokens for lexing and parsing
"""

from stencil_lang.tokens import numbers

literals = [
    'STO',
    'PR',
    'ADD',
    'CAR',
    'PA',
    'SAR',
]
"""Language literals, i.e., the name is the same as the value."""

tokens = numbers.copy()
# Update tokens with literals. Beware that any token duplicated in tokens and
# literals will be overwritten with the value from literals.
for literal in literals:
    tokens[literal] = literal