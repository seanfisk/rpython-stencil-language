from rply import LexerGenerator
from stencil_lang.tokens import tokens, ignores

lg = LexerGenerator()

for rule_name, regex in tokens.iteritems():
    lg.add(rule_name, regex)

for regex in ignores:
    lg.ignore(regex)


def generate_lexer():
    """Generate a stencil language lexer.

    :return: the lexer
    :rtype: :class:`rlpy.lexer.Lexer`
    """
    return lg.build()
