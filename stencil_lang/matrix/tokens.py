""":mod:`stencil_lang.matrix.tokens` -- Tokens for lexing and parsing
"""

from stencil_lang.tokens import numbers

tokens = numbers.copy()
"""Language tokens."""
tokens['NEWLINE'] = r'\n'

ignores = [
    # Ignore all spaces besides the newline character. Jacked this from here
    # and remove the newline `\n' character.
    # <http://docs.python.org/2/library/re.html#regular-expression-syntax>
    r'[ \t\r\f\v]+',
]
"""Patterns to ignore."""
