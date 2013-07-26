""":mod:`stencil_lang.interpreter` -- Interpreter code
"""

from stencil_lang.structures import Context
from stencil_lang.interpreter.lexer import lex
from stencil_lang.interpreter.parser import parse
from stencil_lang.interpreter.evaluator import eval_
from stencil_lang.interpreter.stencil import apply_stencil


def run(source_code):
    """Run the source code.

    :param source_code: code to run
    :type source_code: :class:`str`
    """
    eval_(parse(lex(source_code)), Context(apply_stencil))
