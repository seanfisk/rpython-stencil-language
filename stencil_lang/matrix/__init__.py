""":mod:`stencil_lang.matrix` --- Parse matrices from strings/files
"""

try:
    # PyPy >= 2.0-beta2
    from rpython.rlib.streamio import open_file_as_stream

from stencil_lang.matrix.lexer import lex
from stencil_lang.matrix.parser import parse


def from_string(text):
    """Parse a matrix from a string.

    :param text: matrix text to parse
    :type text: :class:`str`
    :return: the created matrix
    :rtype: :class:`Matrix`
    """
    return parse(lex(text))


def from_file(filename):
    """Parse a matrix from a file.

    :param filename: file name from which to read the matrix
    :type filename: :class:`str`
    :return: the created matrix
    :rtype: :class:`Matrix`
    """
    stream = open_file_as_stream(filename)
    try:
        matrix = from_string(stream.readall())
    finally:
        stream.close()
    return matrix
