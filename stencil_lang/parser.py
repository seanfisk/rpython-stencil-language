""":mod:`stencil_lang.parser` --- Parsing-related variables and classes
"""

from rply import ParserGenerator
from rply.token import BaseBox

from stencil_lang import metadata
from stencil_lang.tokens import tokens
from stencil_lang.errors import (
    UninitializedVariableError,
    InvalidArrayDimensionsError,
    ArgumentError,
    ParseError,
)


# Thought these boxes do the same thing, they all need to exist because they
# hold different types. In addition, a separate __init__ and accessors with
# _different names_ need to exist for each box.
#
# float and int initially might seem to be OK to put in the same
# NumberBox. However, I think RPython just casts to float which presents some
# problems, for example, in the error message string formatting.
#
# The following things don't work:
#
# * Creating a no-op class which just inherits from a ValueBox that has
#   __init__ and get_value.
# * Creating classes using metaprogramming deep-copied from ValueBox.
# * Creating classes using metaprogramming deep-copied from BaseBox, then
#   assigning __init__ and get_* methods to them.

class IntBox(BaseBox):
    """Store an integer."""
    def __init__(self, value):
        """:param value: the number to store
        :type value: :class:`int`
        """
        self._value = value

    def get_int(self):
        """Get the value from the box.

        :return: the value
        :rtype: :class:`int`
        """
        return self._value


class FloatBox(BaseBox):
    """Store a floating-point real number."""
    def __init__(self, value):
        """:param value: the number to store
        :type value: :class:`float`
        """
        self._value = value

    def get_float(self):
        """Get the value from the box.

        :return: the value
        :rtype: :class:`float`
        """
        return self._value


class ListBox(BaseBox):
    """Store a list of numbers."""
    def __init__(self, value):
        """:param value: the value to store
        :type value: :class:`list`
        """
        self._value = value

    def get_list(self):
        """Get the value from the box.

        :return: the value
        :rtype: :class:`list`
        """
        return self._value


class Context(object):
    """Execution context for the interpreter. Stores all global data."""
    def __init__(self):
        self.registers = {}
        """Register bank for the interpreter."""
        self.arrays = {}
        """Array bank for the interpreter."""


# Can't start a class name with a number.
class TwoDimArray(object):
    """Array object for the interpreter."""
    def __init__(self, rows, cols, init_contents):
        """:param rows: number of rows in the array
        :type rows: :class:`int`
        :param cols: number of columns in the array
        :type cols: :class:`int`
        :param init_contents: initial contents of the array
        :type init_contents: :class:`list`
        """
        # I'd prefer to have a dimensions tuple, but RPython loses track of
        # whether they are positive or negative when inserted into a tuple.
        self.rows = rows
        """Number of rows in the array."""
        self.cols = cols
        """Number of columns in the array."""
        self.contents = init_contents
        """Contents of the array, stored as a flat list."""

    def __eq__(self, other):
        # RPython does not honor this method, so it is mostly for testing.
        return (self.rows == other.rows and self.cols == other.cols and
                self.contents == other.contents)

    def __repr__(self):
        # RPython does not honor this method, so it is mostly for testing.
        return '%s(%d, %d, %s)' % (
            type(self).__name__, self.rows, self.cols, self.contents)

    def __str__(self):
        # RPython does not honor this method, but we call it directly.
        if self.contents == []:
            return 'Unpopulated array of dimensions %s' % (
                (self.rows, self.cols), )
        row_strs = []
        for r in xrange(self.rows):
            this_row_index = r * self.cols
            next_row_index = (r + 1) * self.cols
            nums_str_list = [
                str(num) for num in
                self.contents[this_row_index:next_row_index]]
            nums_str = ' '.join(nums_str_list)
            row_strs.append('[%s]' % nums_str)

        return '[%s]' % '\n'.join(row_strs)


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
    state.arrays[index] = TwoDimArray(rows, cols, [])


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
parser = pg.build()
"""This intepreter's parser instance."""
