""":mod:`stencil_lang.structures` --- Data structures
"""

import math

from rply.token import BaseBox
from rpython.rlib.rarithmetic import r_uint

from stencil_lang.utils import rjust, ljust

# Thought these boxes do the same thing, they all need to exist because they
# hold different types. In addition, a separate __init__ and accessors with
# *different names* need to exist for each box.
#
# float and int initially might seem to be OK to put in the same
# NumberBox. However, I think RPython just casts to float which presents some
# problems, for example, in the error message string formatting.


class BaseParser(object):
    """Base class for parsers. Created to fix problem in RPython with parsers
    being passed to RPLY.
    """
    # This necessitated itself when the SMXF instruction was added, pulling in
    # the code for the matrix parser.
    pass


# The RPLY BaseBox defines `_attrs_ = []', which prevents reading attributes
# from box subclasses. I don't want that!!! Use this hack to fix it.
del BaseBox._attrs_


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
    """NOT_RPYTHON"""
    def __init__(self, value):
        self._value = value
    return __init__


# For tests.
ValueBox.__init__ = _make_init()


# Dynamically create boxes to take the monotony out of typing out each one by
# hand. The contents are almost exactly the same.
for box in ['int', 'float', 'float_list', 'float_list_list', 'bytecode_list']:
    class_name = (
        ''.join([type_.capitalize() for type_ in box.split('_')]) + 'Box')
    getter_name = 'get_' + box
    storage_type = 'list' if 'list' in box else box
    init = _make_init()
    init.__doc__ = """:param value: the value to store
:type value: :class:`%s`
""" % (storage_type, )
    getter = lambda self: self._value
    getter.__doc__ = """:return: the value
:rtype: :class:`%s`
""" % (storage_type, )
    globals()[class_name] = type(class_name, (ValueBox, ), {
        '__init__': init,
        getter_name: getter,
    })


# Matrix has to be a type of box so that it can be passed back from a parser
# production.
class Matrix(BaseBox):
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
        """Get an element of this matrix (no wraparound).

        :param requested_indices: a list of indices representing the element \
        to fetch
        :type requested_indices: :class:`list`
        :return: the requested element
        :rtype: :class:`float`
        """
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
                    "Use `getitem_wraparound' for wrap-around behavior.")
            flat_index += requested_index * significance
            significance *= dimensions[i]

        return self.contents[flat_index]

    def getitem_wraparound(self, requested_indices):
        """Get an element of this matrix with wraparound in effect.

        :param requested_indices: a list of indices representing the element \
        to fetch
        :type requested_indices: :class:`list`
        :return: the requested element
        :rtype: :class:`float`
        """
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
            # Cast to integer to strip off the fractional part of THIS number
            # (which is just 0), then format. Probably not the cleanest way,
            # but it works. This is done because RPython doesn't suport '%.0f'.
            sign_str = '-' if real < 0 else ''
            ipart_str = sign_str + str(int(abs(ipart)))
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
                rjust(part_strs[1], max_widths[1]) +
                ljust(part_strs[0], max_widths[0])
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
        """:param apply_stencil: the \
        :func:`stencil_lang.interpreter.stencil.apply_stencil` function
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
        """:func:`stencil_lang.interpreter.stencil.apply_stencil`
        function to use."""
        self.program_length = -1
        """Number of bytecodes in the program. Intended to be set elsewhere."""
