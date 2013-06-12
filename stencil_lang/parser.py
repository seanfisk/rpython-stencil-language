from rply import ParserGenerator
from rply.token import BaseBox

from stencil_lang import metadata
from stencil_lang.tokens import tokens


class ValueBox(BaseBox):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


class Context(object):
    """Execution context for the interpreter. Stores all global data."""
    def __init__(self):
        self.registers = {}


class ParseError(Exception):
    def __init__(self, token_name):
        self._token_name = token_name
        # self._source_pos = source_pos

    def __str__(self):
        # if self._source_pos is None:
        return 'Unexpected end of statement'
        # return ("Unexpected `%s' at line %d, col %d" %
        #         self._token_name, self._source_pos)


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
    index = p[1].value
    real = p[2].value
    state.registers[index] = real


@pg.production('pr : PR index')
def pr(state, p):
    index = p[1].value
    print state.registers[index]


@pg.production('real : REAL')
def real(state, p):
    return ValueBox(float(p[0].getstr()))


@pg.production('index : INDEX')
def index(state, p):
    return ValueBox(int(p[0].getstr()))


@pg.error
def error_handler(state, token):
    # token.getsourcepos() will be None if end of statement.
    raise ParseError(token.gettokentype())


def generate_parser():
    return pg.build()
