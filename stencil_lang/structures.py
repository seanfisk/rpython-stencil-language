""":mod:`stencil_lang.structures` --- Data structures
"""

from rply.token import BaseBox
from rpython.rlib.rarithmetic import r_uint

# Thought these boxes do the same thing, they all need to exist because they
# hold different types. In addition, a separate __init__ and accessors with
# *different names* need to exist for each box.
#
# float and int initially might seem to be OK to put in the same
# NumberBox. However, I think RPython just casts to float which presents some
# problems, for example, in the error message string formatting.


class ValueBox(BaseBox):
    """Box created to add methods not used in RPython."""
    def __repr__(self):
        # RPython does not honor this method, so it is solely for testing.
        return '%s(%s)' % (type(self).__name__, self._value)

    def __eq__(self, other):
        # RPython does not honor this method, so it is solely for testing.
        return self._value == other._value

    def __ne__(self, other):
        return not (self == other)


# We have to "make" a new function each time, otherwise RPython complains with
# a union error.
def _make_init():
    def __init__(self, value):
        self._value = value
    return __init__


# For tests.
ValueBox.__init__ = _make_init()


# Dynamically create boxes to take the monotony out of typing out each one by
# hand. The contents are almost exactly the same.
for box in ['int', 'float', 'float_list', 'bytecode_list']:
    class_name = (
        ''.join([type_.capitalize() for type_ in box.split('_')]) + 'Box')
    getter_name = 'get_' + box
    globals()[class_name] = type(class_name, (ValueBox, ), {
        '__init__': _make_init(),
        getter_name: lambda self: self._value,
    })


class Matrix(object):
    """Matrix object for the interpreter."""
    def __init__(self, rows, cols, init_contents):
        """:param rows: number of rows
        :type rows: :class:`int`
        :param cols: number of columns
        :type cols: :class:`int`
        :param init_contents: initial contents
        :type init_contents: :class:`list` of :class:`float`
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

    def __ne__(self, other):
        # RPython does not honor this method, so it is mostly for testing.
        return not(self == other)

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

    def __str__(self):
        # RPython does not honor this method, so please call it directly.
        if self.contents == []:
            return 'Unpopulated matrix of dimensions (%d, %d)' % (
                self.rows, self.cols)
        row_strs = []

        # Tell RPython that these won't, in fact, be negative.
        rows = r_uint(self.rows)
        cols = r_uint(self.cols)
        for r in xrange(rows):
            this_row_index = r * cols
            next_row_index = (r + 1) * cols
            nums_str_list = [
                str(num) for num in
                self.contents[this_row_index:next_row_index]]
            nums_str = ' '.join(nums_str_list)
            row_strs.append('[%s]' % nums_str)

        return '[%s]' % '\n '.join(row_strs)


class Bytecode(BaseBox):
    """Base bytecode class.
    """
    def eval(self, context):
        """Evaluate this bytecode.

        :param context: the execution context
        :type context: :class:`stencil_lang.structures.Context`
        """
        raise NotImplementedError()

    def __eq__(self, other):
        # RPython does not honor this method, so it is mostly for testing.
        return type(self) is type(other) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        # RPython does not honor this method, so it is mostly for testing.
        return not (self == other)


class Context(object):
    """Execution context/environment for the interpreter.
    """
    def __init__(self, apply_stencil):
        """:param apply_stencil: the apply_stencil function
        :type apply_stencil: :class:`function`
        """
        self.pc = 0
        """Program counter."""
        self.registers = {}
        """Register bank for the interpreter."""
        self.matrices = {}
        """Matrix bank for the interpreter."""
        # Assigning this to the context is probably not the best thing to do,
        # but it's the simplest way to dependency inject it.
        self.apply_stencil = apply_stencil
        """Apply stencil function to use."""
        self.program_length = -1
        """Number of bytecodes in the program. Intended to be set elsewhere."""
