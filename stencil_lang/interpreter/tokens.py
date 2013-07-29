""":mod:`stencil_lang.interpreter.tokens` -- Tokens for lexing and parsing
"""

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

IGNORES = [
    r'\s+',
]
"""Patterns to ignore."""

TOKENS = {
    'POS_INT': r'\d+',
    'NEG_INT': r'-\d+',
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
    'REAL': r'-?\d+\.\d*',
    # A quoted filename.
    'FILENAME': r'"[^"]+"',
}
"""Language tokens for lexing and parsing."""

# Update tokens with literals. Beware that any token duplicated in tokens and
# literals will be overwritten with the value from literals.
for literal in LITERALS:
    # It is important to make sure that the literals are "words", e.g.,
    # surrounded by spaces. This is especially important for SMX and SMXF,
    # because the lexer will find SMX before SMXF.
    TOKENS[literal] = r'\b%s\b' % literal
