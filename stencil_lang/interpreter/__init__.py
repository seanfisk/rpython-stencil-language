""":mod:`stencil_lang.interpreter` -- Interpreter code
"""

from stencil_lang.interpreter.lexer import lex
from stencil_lang.interpreter.parser import parse


def run(source_code, context):
    """Run the source code with the specified context.

    :param source_code: code to run
    :type source_code: :class:`str`
    :param context: state for variables
    :type context: :class:`stencil_lang.structures.Context`
    """
    stream = lex(source_code)
    parse(stream, context)
