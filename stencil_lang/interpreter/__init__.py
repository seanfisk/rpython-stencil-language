""":mod:`stencil_lang.interpreter` -- Interpreter code
"""

from stencil_lang.interpreter.lexer import lex
from stencil_lang.interpreter.parser import parse


def run(source_code):
    """Run the source code.

    :param source_code: code to run
    :type source_code: :class:`str`
    """
    parse(lex(source_code))
