""":mod:`stencil_lang.matrix.parser` -- Matrix parser
"""

from rply import ParserGenerator

from stencil_lang.matrix.tokens import tokens
from stencil_lang.structures import (
    IntBox,
    FloatBox,
    ListBox,
    Matrix,
)
from stencil_lang.errors import (
    InconsistentMatrixDimensions,
    ParseError,
)

pg = ParserGenerator(tokens.keys(), cache_id=__name__)


@pg.production('main : lines')
@pg.production('main :')
def main(state, p):
    if p == []:
        matrix = Matrix(0, 0, [])
    else:
        list_list_box = p[0]
        list_of_lists = list_list_box.get_list()
        rows = len(list_of_lists)
        cols = state.cols
        matrix = Matrix(rows, cols, [])
        for list_ in list_of_lists:
            matrix.contents.extend(list_)
    return matrix


# Newline at the end.
@pg.production('lines : lines line')
@pg.production('lines : line')
# No newline at the end.
@pg.production('lines : lines row')
@pg.production('lines : row')
def lines(state, p):
    if len(p) == 2:
        # lines: lines line
        # lines: lines row
        list_list_box = p[0]
        number_list_box = p[1]
        list_list_box.get_list().append(number_list_box.get_list())
    else:
        # lines : line
        # lines : row
        number_list_box = p[0]
        list_list_box = ListBox([number_list_box.get_list()])
    return list_list_box


@pg.production('line : row newline')
def line(state, p):
    row = p[0]
    return row


@pg.production('row : number_list')
def row(state, p):
    number_list_box = p[0]
    current_cols = len(number_list_box.get_list())
    if state.cols == -1:
        # The number of columns in the first row determines the number of
        # columns for all rows.
        state.cols = current_cols
    elif current_cols != state.cols:
        raise InconsistentMatrixDimensions(state.cols, current_cols)
    return number_list_box


# TODO: copied from stencil_lang/interpreter/parser.py
# number_list must come first to parse the first number s first.
@pg.production('number_list : number_list number')
@pg.production('number_list : number')
def number_list(state, p):
    if len(p) == 2:
        # number_list : number_list number
        number_list_box = p[0]
        number = (p[1].get_int() if isinstance(p[1], IntBox)
                  else p[1].get_float())
        # TODO: Might have a problem with this mutating the list in the future.
        number_list_box.get_list().append(number)
    else:
        # number_list : number
        number = (p[0].get_int() if isinstance(p[0], IntBox)
                  else p[0].get_float())
        number_list_box = ListBox([number])
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
def int_(state, p):
    return IntBox(int(p[0].getstr()))


@pg.production('newline : NEWLINE')
def newline(state, p):
    pass


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
    :return: the final value parsed
    :rtype: :class:`rply.token.BaseBox`
    """
    return _parser.parse(text, state)
