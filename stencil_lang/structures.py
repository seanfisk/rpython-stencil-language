""":mod:`stencil_lang.structures` --- Data structures
"""

import math

from rply.token import BaseBox
from rpython.rlib.rarithmetic import r_uint

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


class ValueBox(BaseBox):
    """Box created solely to add a repr."""
    def __init__(self, value):
        """Override this __init__ method with a method exactly like it (for
        RPython's type checking.)

        :param value: the number to store
        :type value: :class:`object`
        """
        self._value = value

    def __repr__(self):
        # RPython does not honor this method, so it is solely for testing.
        return '%s(%s)' % (type(self).__name__, self._value)


class IntBox(ValueBox):
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


class FloatBox(ValueBox):
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


class ListBox(ValueBox):
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

    def _check_indices(self, requested_indices):
        if (not isinstance(requested_indices, list)
                or len(requested_indices) != 2):
            raise TypeError(
                'Matrix indices must be a list of integers of length 2')

    def getitem(self, requested_indices):
        self._check_indices(requested_indices)
        dimensions = [self.rows, self.cols]
        flat_index = 0
        significance = 1
        # Cannot use reversed(), so we must iterate reversed the "old way".
        for i in xrange(len(dimensions) - 1, -1, -1):
            requested_index = requested_indices[i]
            if requested_index < 0:
                raise ValueError(
                    'Matrix indices must be non-negative. '
                    "Use `getitem_advanced' for wrap-around behavior.")
            flat_index += requested_index * significance
            significance *= dimensions[i]

        return self.contents[flat_index]

    def getitem_advanced(self, requested_indices):
        self._check_indices(requested_indices)
        dimensions = [self.rows, self.cols]
        # Python follows the correct behavior of modulus (always returning
        # a positive number), so this works.
        return self.getitem([
            requested_indices[i] % dimensions[i] for i
            in xrange(len(requested_indices))])

    def __repr__(self):
        # RPython does not honor this method, so it is mostly for testing.
        return '%s(%d, %d, %s)' % (
            type(self).__name__, self.rows, self.cols, self.contents)

    def _format_as_string(self, bracketed):
        if self.contents == []:
            return 'Unpopulated matrix of dimensions (%d, %d)' % (
                self.rows, self.cols)

        part_strs_list = []
        max_widths = [0, 0]
        for real in self.contents:
            # Fractional part is first, integer part second.
            fpart, ipart = math.modf(real)
            # Remove negative from fpart and strip the leading zero.
            fpart_str = str(abs(fpart))[1:] if fpart != 0 else ''
            ipart_str = '%.0f' % ipart
            part_strs = [fpart_str, ipart_str]
            max_widths = [
                max(len(part_strs[i]), max_widths[i]) for i in xrange(2)]
            part_strs_list.append(part_strs)

        # Tell RPython that these won't, in fact, be negative.
        rows = r_uint(self.rows)
        cols = r_uint(self.cols)
        lines = [
            ' '.join([
                # Fractional part is first, integer part second.
                part_strs[1].rjust(max_widths[1]) +
                part_strs[0].ljust(max_widths[0])
                for part_strs
                in part_strs_list[r * cols:(r + 1) * cols]])
            for r
            in xrange(rows)]

        if bracketed:
            lines = [' [ %s ]' % line for line in lines]
            lines[0] = '[' + lines[0][1:]
            lines[-1] = lines[-1] + ']'
        else:
            lines = [line.rstrip() for line in lines]
        return '\n'.join(lines)

    def as_plain_string(self):
        return self._format_as_string(bracketed=False)

    def as_bracketed_string(self):
        return self._format_as_string(bracketed=True)

    def __str__(self):
        # RPython does not honor this method, so please call matrix.__str__()
        # or matrix.as_bracketed_string() directly.
        return self.as_bracketed_string()
