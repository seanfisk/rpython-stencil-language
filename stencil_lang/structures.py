""":mod:`stencil_lang.structures` --- Data structures
"""

from rply.token import BaseBox

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


class Matrix(object):
    """Matrix object for the interpreter."""
    def __init__(self, rows, cols, init_contents):
        """:param rows: number of rows
        :type rows: :class:`int`
        :param cols: number of columns
        :type cols: :class:`int`
        :param init_contents: initial contents
        :type init_contents: :class:`list`
        """
        # I'd prefer to have a dimensions tuple, but RPython loses track of
        # whether they are positive or negative when inserted into a tuple.
        self.rows = rows
        """Number of rows in the matrix."""
        self.cols = cols
        """Number of columns in the matrix."""
        self.contents = init_contents
        """Contents of the matrix, stored as a flat list."""

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
