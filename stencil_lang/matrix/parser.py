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


class Parser(object):
    """Matrix parser."""
    def __init__(self):
        self._cols = -1

    _pg = ParserGenerator(tokens.keys(), cache_id=__name__)

    @_pg.production('main : lines')
    @_pg.production('main :')
    def _main(self, p):
        if p == []:
            matrix = Matrix(0, 0, [])
        else:
            list_list_box = p[0]
            list_of_lists = list_list_box.get_list()
            rows = len(list_of_lists)
            matrix = Matrix(rows, self._cols, [])
            for list_ in list_of_lists:
                matrix.contents.extend(list_)
        return matrix

    # Newline at the end.
    @_pg.production('lines : lines line')
    @_pg.production('lines : line')
    # No newline at the end.
    @_pg.production('lines : lines row')
    @_pg.production('lines : row')
    def _lines(self, p):
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

    @_pg.production('line : row newline')
    def _line(self, p):
        row = p[0]
        return row

    @_pg.production('row : number_list')
    def _row(self, p):
        number_list_box = p[0]
        current_cols = len(number_list_box.get_list())
        if self._cols == -1:
            # The number of columns in the first row determines the number of
            # columns for all rows.
            self._cols = current_cols
        elif current_cols != self._cols:
            raise InconsistentMatrixDimensions(self._cols, current_cols)
        return number_list_box

    # TODO: copied from stencil_lang/interpreter/parser.py
    # number_list must come first to parse the first number s first.
    @_pg.production('number_list : number_list number')
    @_pg.production('number_list : number')
    def _number_list(self, p):
        if len(p) == 2:
            # number_list : number_list number
            number_list_box = p[0]
            number = (p[1].get_int() if isinstance(p[1], IntBox)
                      else p[1].get_float())
            # TODO: Might have a problem with this mutating the list in the
            # future.
            number_list_box.get_list().append(number)
        else:
            # number_list : number
            number = (p[0].get_int() if isinstance(p[0], IntBox)
                      else p[0].get_float())
            number_list_box = ListBox([number])
        return number_list_box

    @_pg.production('number : int')
    @_pg.production('number : real')
    def _number(self, p):
        return p[0]

    @_pg.production('real : REAL')
    def _real(self, p):
        return FloatBox(float(p[0].getstr()))

    @_pg.production('int : POS_INT')
    @_pg.production('int : NEG_INT')
    def _int(self, p):
        return IntBox(int(p[0].getstr()))

    @_pg.production('newline : NEWLINE')
    def _newline(self, p):
        pass

    @_pg.error
    def _error_handler(self, token):
        # NOTE: SourcePosition is a class, but it's not actually implemented :(
        raise ParseError(token.gettokentype())

    # This has to be called outside a function because the parser must be
    # generated in Python during translation, not in RPython during runtime.
    _parser = _pg.build()

    def parse(self, text):
        """Parse and interpret using the generated parser.

        :param text: text to parse
        :type text: :class:`str`
        :return: the final value parsed
        :rtype: :class:`rply.token.BaseBox`
        """
        return self._parser.parse(text, state=self)


def parse(text):
    """Parse and interpret text using the generated parser.

    :param text: text to parse
    :type text: :class:`str`
    :return: the final value parsed
    :rtype: :class:`rply.token.BaseBox`
    """
    return Parser().parse(text)
