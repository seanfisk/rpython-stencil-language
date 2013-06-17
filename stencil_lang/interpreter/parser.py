""":mod:`stencil_lang.interpreter.parser` --- Parsing-related classes
"""
from rply import ParserGenerator

from stencil_lang.interpreter.tokens import tokens
from stencil_lang.structures import (
    IntBox,
    FloatBox,
    ListBox,
    Matrix,
)
from stencil_lang.errors import (
    UninitializedVariableError,
    InvalidArrayDimensionsError,
    ArgumentError,
    ParseError,
)

pg = ParserGenerator(tokens.keys(), cache_id=__name__)


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
@pg.production('stmt : car')
@pg.production('stmt : pa')
@pg.production('stmt : sar')
def stmt(state, p):
    pass


@pg.production('sto : STO index number')
def sto(state, p):
    index = p[1].get_int()
    number = p[2].get_int() if isinstance(p[2], IntBox) else p[2].get_float()
    state.registers[index] = number


@pg.production('pr : PR index')
def pr(state, p):
    index = p[1].get_int()
    try:
        print state.registers[index]
    except KeyError:
        raise UninitializedVariableError('Register', index)


@pg.production('add : ADD index number')
def add(state, p):
    index = p[1].get_int()
    # number = p[2].get_number()
    number = p[2].get_int() if isinstance(p[2], IntBox) else p[2].get_float()
    try:
        state.registers[index] += number
    except KeyError:
        raise UninitializedVariableError('Register', index)


@pg.production('car : CAR index pos_int pos_int')
def car(state, p):
    index = p[1].get_int()
    rows = p[2].get_int()
    cols = p[3].get_int()
    if rows <= 0 or cols <= 0:
        raise InvalidArrayDimensionsError(index, (rows, cols))
    state.arrays[index] = Matrix(rows, cols, [])


@pg.production('pa : PA index')
def pa(state, p):
    index = p[1].get_int()
    try:
        # RPython does not honor most magic methods. Hence, just `print' will
        # work in tests but not when translated.
        print state.arrays[index].__str__()
    except KeyError:
        raise UninitializedVariableError('Array', index)


@pg.production('sar : SAR index number_list')
def sar(state, p):
    index = p[1].get_int()
    number_list = p[2].get_list()
    try:
        two_dim_array = state.arrays[index]
    except KeyError:
        raise UninitializedVariableError('Array', index)
    num_required_args = two_dim_array.rows * two_dim_array.cols
    num_given_args = len(number_list)
    if num_given_args != num_required_args:
        raise ArgumentError(num_required_args, num_given_args)
    two_dim_array.contents = number_list


# number_list must come after number so that it can initially create a list for
# insertion.
@pg.production('number_list : number number_list')
@pg.production('number_list : number')
def number_list(state, p):
    number = p[0].get_int() if isinstance(p[0], IntBox) else p[0].get_float()
    if len(p) == 2:
        # number_list : number number_list
        number_list_box = p[1]
        # new_number_list_box = ListBox([number])
        # new_number_list_box.get_value().extend(number_list_box.get_value())
        # number_list_box.get_value().insert(0, number)

        # Make a shallow copy
        # new_number_list = number_list_box.get_list()[:]
        # new_number_list.insert(0, number)
        # new_number_list_box = ListBox(new_number_list)
        # TODO: Might have a problem with this mutating the list in the future.
        number_list_box.get_list().insert(0, number)
    else:
        # number_list : number
        number_list_box = ListBox([number])  # NOQA
    return number_list_box


@pg.production('number : int')
@pg.production('number : real')
def number(state, p):
    return p[0]


@pg.production('real : REAL')
def real(state, p):
    return FloatBox(float(p[0].getstr()))


@pg.production('int : POS_INT')
@pg.production('int : NEG_INT')
@pg.production('index : POS_INT')
@pg.production('pos_int : POS_INT')
def int_(state, p):
    return IntBox(int(p[0].getstr()))


@pg.error
def error_handler(state, token):
    # NOTE: SourcePosition is a class, but it's not actually implemented :(
    raise ParseError(token.gettokentype())

# This has to be called outside a function because the parser must be generated
# in Python during translation, not in RPython during runtime.
_parser = pg.build()
"""This intepreter's parser instance."""


def parse(text, state):
    """Parse and interpret text using the generated parser.

    :param text: text to parse
    :type text: :class:`str`
    :param state: state to pass to the parser
    :type state: :class:`object`
    """
    _parser.parse(text, state)
