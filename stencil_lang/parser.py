from rply import ParserGenerator
from rply.token import BaseBox

from stencil_lang import metadata
from stencil_lang.tokens import tokens
""":mod:`stencil_lang.parser` --- Parsing-related variables and classes
"""

from stencil_lang.errors import UninitializedRegisterError


class ValueBox(BaseBox):
    """Box that stores a single value."""
    def __init__(self, value):
        """:param value: the value to store
        :type value: :class:`object`
        """
        self._value = value

    # Don't name this function `value'. RPython doesn't like it when
    # translating.
    def get_value(self):
        """Get the value from the box.

        :return: the value
        :rtype: :class:`object`
        """
        return self._value

# Thought IntBox and RealBox do the same thing, they both need to exist because
# they hold different types.


class IntBox(ValueBox):
    """Store an integer."""
    pass


class RealBox(ValueBox):
    """Store a real number."""
    pass


class Context(object):
    """Execution context for the interpreter. Stores all global data."""
    def __init__(self):
        self.registers = {}
        """Register bank for the interpreter."""


class ParseError(Exception):
    """Raised when parser encounters a generic issue."""
    def __init__(self, token_name):
        """:param token_name: name of the token that caused the error
        :type token_name: :class:`str`
        """
        self._token_name = token_name

    def __str__(self):
        return "Unexpected `%s'" % self._token_name


pg = ParserGenerator(tokens.keys(), cache_id=metadata.package)


@pg.production('main : stmt_list')
def main(state, p):
    pass


# A valid program can be just one statement.
@pg.production('stmt_list : stmt')
@pg.production('stmt_list : stmt stmt_list')
def stmt_list(state, p):
    pass


@pg.production('stmt : sto')
@pg.production('stmt : pr')
@pg.production('stmt : add')
def stmt(state, p):
    pass


@pg.production('sto : STO index number')
def sto(state, p):
    index = p[1].get_value()
    number = p[2].get_value()
    state.registers[index] = number


@pg.production('pr : PR index')
def pr(state, p):
    index = p[1].get_value()
    print state.registers[index]


@pg.production('add : ADD index number')
def add(state, p):
    index = p[1].get_value()
    number = p[2].get_value()
    try:
        state.registers[index] += number
    except KeyError:
        raise UninitializedRegisterError(index)


@pg.production('number : int')
@pg.production('number : real')
def number(state, p):
    return p[0]


@pg.production('real : REAL')
def real(state, p):
    return RealBox(float(p[0].getstr()))


@pg.production('int : POS_INT')
@pg.production('int : NEG_INT')
@pg.production('index : POS_INT')
def int_(state, p):
    return IntBox(int(p[0].getstr()))


@pg.error
def error_handler(state, token):
    # NOTE: SourcePosition is a class, but it's not actually implemented :(
    raise ParseError(token.gettokentype())

# This has to be called outside a function because the parser must be generated
# in Python during translation, not in RPython during runtime.
parser = pg.build()
"""This intepreter's parser instance."""
