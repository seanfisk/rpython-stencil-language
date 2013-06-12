""":mod:`stencil_lang.tokens` -- Tokens for lexing and parsing
"""

literals = [
    'STO',
    'PR',
]
"""Language literals, i.e., the name is the same as the value."""

tokens = {
    # Indexes cannot be negative.
    'INDEX': r'\d+',
    # Reals must include an integer part, so `.3' is not a valid real. It must
    # be `0.3'.
    'REAL': r'-?\d+\.\d*',
}
"""Language tokens for lexing and parsing."""

# Update tokens with literals. Beware that any token duplicated in tokens and
# literals will be overwritten with the value from literals.
for literal in literals:
    tokens[literal] = literal

ignores = [
    r'\s+',
    r'\n+',
]
"""Patterns to ignore."""