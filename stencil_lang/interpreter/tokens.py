""":mod:`stencil_lang.interpreter.tokens` -- Tokens for lexing and parsing
"""

from collections import OrderedDict

# Order does matter here! It indicates precedence.
TOKENS = OrderedDict()
"""Language tokens for lexing and parsing."""

LITERALS = [
    'STO',
    'PR',
    'ADD',
    'CMX',
    'PMX',
    'SMXF',
    'SMX',
    'PDE',
    'BNE',
]
"""Language literals, i.e., the name is the same as the value."""

# Update tokens with literals.
for literal in LITERALS:
    # It is important to make sure that the literals are "words", e.g.,
    # surrounded by spaces. This is especially important for SMX and SMXF,
    # because the lexer will find SMX before SMXF.
    TOKENS[literal] = r'\b%s\b' % literal

# Order matters here too. It is arranged to find the longest match first.
TOKEN_PATTERNS = OrderedDict([
    # Valid real scis:
    #
    # 9e10
    # 3e-4
    # 2.2e5
    # -11.8e-2
    #
    ('REAL_SCI', r'-?\d+(\.\d*)?e-?\d+'),
    # Valid reals:
    #
    # 23.
    # 82.2
    # 10.90
    # 010.9
    # 0.456
    # -23.
    # -82.2
    # -10.90
    # -010.9
    # -0.456
    #
    # Invalid reals:
    #
    # 23
    # -81
    # .4
    # -.4
    #
    ('REAL', r'-?\d+\.\d*'),
    ('POS_INT', r'\d+'),
    ('NEG_INT', r'-\d+'),
    # A quoted filename.
    ('FILENAME', r'"[^"]+"'),
])

TOKENS.update(TOKEN_PATTERNS)

IGNORES = [
    r'\s+',
]
"""Patterns to ignore."""
