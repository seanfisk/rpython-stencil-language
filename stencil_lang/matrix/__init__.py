""":mod:`stencil_lang.matrix` --- Parse matrices from strings/files
"""

from stencil_lang.matrix.lexer import lex
from stencil_lang.matrix.parser import parse


class State(object):
    """State object which gets passed to the parser."""
    def __init__(self):
        self.cols = -1


def from_string(text):
    """Parse a matrix from a string.

    :param text: matrix text to parse
    :type text: :class:`str`
    :return: the created matrix
    :rtype: :class:`Matrix`
    """
    state = State()
    return parse(lex(text), state)
