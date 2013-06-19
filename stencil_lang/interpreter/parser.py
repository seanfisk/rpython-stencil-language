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
from stencil_lang.interpreter.stencil import apply_stencil


class Parser(object):
    """Source code parser and intepreter."""
    def __init__(self, apply_stencil):
        """:param apply_stencil: the apply_stencil function
        :type apply_stencil: :class:`function`
        """
        self._apply_stencil = apply_stencil
        self.registers = {}
        """Register bank for the interpreter."""
        self.arrays = {}
        """Array bank for the interpreter."""

    _pg = ParserGenerator(tokens.keys(), cache_id=__name__)

    def _safe_get_array(self, array_num):
        try:
            return self.arrays[array_num]
        except KeyError:
            raise UninitializedVariableError('Array', array_num)

    def _safe_get_register(self, register_num):
        try:
            return self.registers[register_num]
        except KeyError:
            raise UninitializedVariableError('Register', register_num)

    @_pg.production('main : stmt_list')
    def _main(self, p):
        pass

    # A valid program can be just one statement.
    @_pg.production('stmt_list : stmt')
    @_pg.production('stmt_list : stmt stmt_list')
    def _stmt_list(self, p):
        pass

    @_pg.production('stmt : sto')
    @_pg.production('stmt : pr')
    @_pg.production('stmt : add')
    @_pg.production('stmt : car')
    @_pg.production('stmt : pa')
    @_pg.production('stmt : sar')
    @_pg.production('stmt : pde')
    def _stmt(self, p):
        pass

    @_pg.production('sto : STO index number')
    def _sto(self, p):
        index = p[1].get_int()
        number = (p[2].get_int() if isinstance(p[2], IntBox)
                  else p[2].get_float())
        self.registers[index] = number

    @_pg.production('pr : PR index')
    def _pr(self, p):
        index = p[1].get_int()
        print self._safe_get_register(index)

    @_pg.production('add : ADD index number')
    def _add(self, p):
        index = p[1].get_int()
        # number = p[2].get_number()
        number = (p[2].get_int() if isinstance(p[2], IntBox)
                  else p[2].get_float())
        try:
            self.registers[index] += number
        except KeyError:
            raise UninitializedVariableError('Register', index)

    @_pg.production('car : CAR index pos_int pos_int')
    def _car(self, p):
        index = p[1].get_int()
        rows = p[2].get_int()
        cols = p[3].get_int()
        if rows <= 0 or cols <= 0:
            raise InvalidArrayDimensionsError(index, (rows, cols))
        self.arrays[index] = Matrix(rows, cols, [])

    @_pg.production('pa : PA index')
    def _pa(self, p):
        index = p[1].get_int()
        # RPython does not honor most magic methods. Hence, just `print'
        # will work in tests but not when translated.
        print self._safe_get_array(index).__str__()

    @_pg.production('sar : SAR index number_list')
    def _sar(self, p):
        index = p[1].get_int()
        number_list = p[2].get_list()
        two_dim_array = self._safe_get_array(index)
        num_required_args = two_dim_array.rows * two_dim_array.cols
        num_given_args = len(number_list)
        if num_given_args != num_required_args:
            raise ArgumentError(num_required_args, num_given_args)
        two_dim_array.contents = number_list

    @_pg.production('pde : PDE index index')
    def _pde(self, p):
        stencil_index = p[1].get_int()
        stencil = self._safe_get_array(stencil_index)
        matrix_index = p[2].get_int()
        matrix = self._safe_get_array(matrix_index)
        self.arrays[matrix_index] = self._apply_stencil(stencil, matrix)

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
    @_pg.production('index : POS_INT')
    @_pg.production('pos_int : POS_INT')
    def _int(self, p):
        return IntBox(int(p[0].getstr()))

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
    return Parser(apply_stencil).parse(text)
