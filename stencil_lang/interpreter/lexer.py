""":mod:`stencil_lang.interpreter.lexer` --- Scanning-related variables
"""
from rply import LexerGenerator

from stencil_lang.interpreter.tokens import TOKENS
from stencil_lang.tokens import IGNORES

lg = LexerGenerator()

for rule_name, regex in TOKENS.iteritems():
    lg.add(rule_name, regex)

for regex in IGNORES:
    lg.ignore(regex)

# This has to be called outside a function because the parser must be generated
# in Python during translation, not in RPython during runtime.
_lexer = lg.build()
"""This intepreter's lexer instance."""


def lex(text):
    """Scan text using the generated lexer.

    :param text: text to lex
    :type text: :class:`str`
    :return: parsed stream
    :rtype: :class:`rply.lexer.LexerStream`
    """
    return _lexer.lex(text)
