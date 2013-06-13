from rply import ParserGenerator
from rply.token import BaseBox

from stencil_lang import metadata
from stencil_lang.tokens import tokens


class ValueBox(BaseBox):
    def __init__(self, value):
        self._value = value

    def value(self):
        return self._value

# Thought IntBox and RealBox do the same thing, they both need to exist because
# they hold different types.


class IntBox(ValueBox):
    pass


class RealBox(ValueBox):
    pass


class Context(object):
    """Execution context for the interpreter. Stores all global data."""
    def __init__(self):
        self.registers = {}


class ParseError(Exception):
    def __init__(self, token_name):
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
def stmt(state, p):
    pass


@pg.production('sto : STO index real')
def sto(state, p):
    index = p[1].value()
    real = p[2].value()
    state.registers[index] = real


@pg.production('pr : PR index')
def pr(state, p):
    index = p[1].value()
    print state.registers[index]


@pg.production('real : REAL')
def real(state, p):
    return RealBox(float(p[0].getstr()))


@pg.production('index : INDEX')
def index(state, p):
    return IntBox(int(p[0].getstr()))


@pg.error
def error_handler(state, token):
    # NOTE: SourcePosition is a class, but it's not actually implemented :(
    raise ParseError(token.gettokentype())

# This has to be called outside a function because the parser must be generated
# in Python during translation, not in RPython during runtime.
parser = pg.build()
"""This intepreter's parser instance."""
