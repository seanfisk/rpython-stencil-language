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
)


# Thought these boxes do the same thing, they all need to exist because they
# hold different types. In addition, a separate __init__ and accessors with
# _different names_ need to exist for each box.
#
# float and int seem to be OK to put in the same NumberBox. I'm not sure if
# that's just a consequence of how I'm using them.
#
# The following things don't work:
#
# * Creating a no-op class which just inherits from a ValueBox that has
#   __init__ and get_value.
# * Creating classes using metaprogramming deep-copied from ValueBox.
# * Creating classes using metaprogramming deep-copied from BaseBox, then
#   assigning __init__ and get_* methods to them.

class NumberBox(BaseBox):
    """Store a number: int or float."""
    def __init__(self, value):
        """:param value: the number to store
        :type value: :class:`int` or :class:`float`
        """
        self._value = value

    def get_number(self):
        """Get the value from the box.

        :return: the value
        :rtype: :class:`int` or :class:`float`
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
    def __init__(self, dimensions, init_contents):
        """:param dimensions: dimensions of the array
        :type dimensions: :class:`tuple` of (:class:`int`, :class:`int`)
        :param init_contents: initial contents of the array
        :type init_contents: :class:`list`
        """
        self.dimensions = dimensions
        """Dimensions of the array."""
        self.contents = init_contents
        """Contents of the array, stored as a flat list."""

    def __eq__(self, other):
        return (self.dimensions == other.dimensions and
                self.contents == other.contents)

    def __repr__(self):
        return '%s(%s, %s)' % (
            type(self).__name__, self.dimensions, self.contents)

    def __str__(self):
        if self.contents == []:
            return 'Unpopulated array of dimensions %s' % (self.dimensions, )
        rows, cols = self.dimensions
        row_strs = []
        for r in xrange(rows):
            this_row_index = r * cols
            next_row_index = (r + 1) * cols
            nums_str_list = [
                str(num) for num in
                self.contents[this_row_index:next_row_index]]
            nums_str = ' '.join(nums_str_list)
            row_strs.append('[%s]' % nums_str)

        return '[%s]' % '\n'.join(row_strs)


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
@pg.production('stmt : car')
@pg.production('stmt : pa')
@pg.production('stmt : sar')
def stmt(state, p):
    pass


@pg.production('sto : STO index number')
def sto(state, p):
    index = p[1].get_number()
    number = p[2].get_number()
    state.registers[index] = number


@pg.production('pr : PR index')
def pr(state, p):
    index = p[1].get_number()
    try:
        print state.registers[index]
    except KeyError:
        raise UninitializedVariableError('register', index)


@pg.production('add : ADD index number')
def add(state, p):
    index = p[1].get_number()
    number = p[2].get_number()
    try:
        state.registers[index] += number
    except KeyError:
        raise UninitializedVariableError('register', index)


@pg.production('car : CAR index pos_int pos_int')
def car(state, p):
    index = p[1].get_number()
    rows = p[2].get_number()
    cols = p[3].get_number()
    dimensions = (rows, cols)
    if rows <= 0 or cols <= 0:
        raise InvalidArrayDimensionsError(index, dimensions)
    state.arrays[index] = TwoDimArray(dimensions, [])


@pg.production('pa : PA index')
def pa(state, p):
    index = p[1].get_number()
    try:
        # RPython does not honor most magic methods. Hence, just `print' will
        # work in tests but not when translated.
        print state.arrays[index].__str__()
    except KeyError:
        raise UninitializedVariableError('array', index)


@pg.production('sar : SAR index number_list')
def sar(state, p):
    index = p[1].get_number()
    number_list = p[2].get_list()
    try:
        two_dim_array = state.arrays[index]
    except KeyError:
        raise UninitializedVariableError('array', index)
    dimensions = two_dim_array.dimensions
    num_required_args = dimensions[0] * dimensions[1]
    num_given_args = len(number_list)
    if num_given_args != num_required_args:
        raise ArgumentError(num_required_args, num_given_args)
    two_dim_array.contents = number_list


# number_list must come after number so that it can initially create a list for
# insertion.
@pg.production('number_list : number number_list')
@pg.production('number_list : number')
def number_list(state, p):
    number = p[0].get_number()
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
    return NumberBox(float(p[0].getstr()))  # NOQA


@pg.production('int : POS_INT')
@pg.production('int : NEG_INT')
@pg.production('index : POS_INT')
@pg.production('pos_int : POS_INT')
def int_(state, p):
    return NumberBox(int(p[0].getstr()))  # NOQA


@pg.error
def error_handler(state, token):
    # NOTE: SourcePosition is a class, but it's not actually implemented :(
    raise ParseError(token.gettokentype())

# This has to be called outside a function because the parser must be generated
# in Python during translation, not in RPython during runtime.
parser = pg.build()
"""This intepreter's parser instance."""
