""":mod:`stencil_lang.tokens` -- Common tokens for parsing
"""
numbers = {
    'POS_INT': r'\d+',
    'NEG_INT': r'-\d+',
    # Reals must include an integer part, so `.3' is not a valid real. It must
    # be `0.3'.
    'REAL': r'-?\d+\.\d*',
}
"""Language tokens for lexing and parsing."""

ignores = [
    r'\s+',
    r'\n+',
]
"""Patterns to ignore."""
