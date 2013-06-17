""":mod:`stencil_lang.matrix.lexer` -- Matrix scanner
"""

from rply import LexerGenerator

from stencil_lang.matrix.tokens import tokens, ignores

lg = LexerGenerator()

for rule_name, regex in tokens.iteritems():
    lg.add(rule_name, regex)

for regex in ignores:
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
    :rtype: rply.lexer.LexerStream
    """
    return _lexer.lex(text)
