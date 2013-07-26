""":mod:`stencil_lang.matrix.tokens` -- Tokens for lexing and parsing
"""

TOKENS = {
    # Read integers and reals the same way.
    'NUMBER': r'-?\d+(?:\.\d*)?',
    'NEWLINE':  r'\n',
}
"""Language tokens."""

IGNORES = [
    # Ignore all spaces besides the newline character. Jacked this from here
    # and remove the newline `\n' character.
    # <http://docs.python.org/2/library/re.html#regular-expression-syntax>
    r'[ \t\r\f\v]+',
]
"""Patterns to ignore."""
