""":mod:`stencil_lang.interpreter.bytecodes` -- Interpreter bytecodes
"""

from stencil_lang.structures import Bytecode, Matrix
from stencil_lang.errors import (
    UninitializedVariableError,
    InvalidMatrixDimensionsError,
    ArgumentError,
    InvalidBranchOffsetError,
)


def _safe_get_matrix(context, matrix_num):
    try:
        return context.matrices[matrix_num]
    except KeyError:
        raise UninitializedVariableError('Matrix', matrix_num)


def _safe_get_register(context, register_num):
    try:
        return context.registers[register_num]
    except KeyError:
        raise UninitializedVariableError('Register', register_num)


class Sto(Bytecode):
    """Register store bytecode."""
    def __init__(self, index, integer):
        """:param index: register index in which to store value
        :type index: :class:`int`
        :param integer: integer to store
        :type integer: :class:`int`
        """
        self._index = index
        self._integer = integer

    def eval(self, context):
        context.registers[self._index] = self._integer


class Pr(Bytecode):
    """Print register bytecode."""
    def __init__(self, index):
        """:param index: register index to print
        :type index: :class:`int`
        """
        self._index = index

    def eval(self, context):
        print _safe_get_register(context, self._index)


class Add(Bytecode):
    """Add bytecode."""
    def __init__(self, index, integer):
        """:param index: register index to which to add
        :type index: :class:`int`
        :param integer: integer to add to register
        :type integer: :class:`int`
        """
        self._index = index
        self._integer = integer

    def eval(self, context):
        index = self._index
        try:
            context.registers[index] += self._integer
        except KeyError:
            raise UninitializedVariableError('Register', index)


class Cmx(Bytecode):
    """Create matrix bytecode."""
    def __init__(self, index, rows, cols):
        """:param index: matrix index
        :type index: :class:`int`
        :param rows: number of rows in the matrix
        :type rows: :class:`int`
        :param cols: number of rows in the matrix
        :type cols: :class:`int`
        """
        self._index = index
        self._rows = rows
        self._cols = cols

    def eval(self, context):
        index = self._index
        rows = self._rows
        cols = self._cols
        if rows <= 0 or cols <= 0:
            raise InvalidMatrixDimensionsError(index, (rows, cols))
        context.matrices[index] = Matrix(rows, cols, [])


class Pmx(Bytecode):
    """Print matrix bytecode."""
    def __init__(self, index):
        """:param index: matrix index
        :type index: :class:`int`
        """
        self._index = index

    def eval(self, context):
        # RPython does not honor most magic methods. Hence, just `print'
        # will work in tests but not when translated.
        print _safe_get_matrix(context, self._index).__str__()


class Smx(Bytecode):
    """Set matrix bytecode"""
    def __init__(self, index, real_list):
        """:param index: matrix index
        :type index: :class:`int`
        :param real_list: contents of matrix
        :type real_list: :class:`list`
        """
        self._index = index
        self._real_list = real_list

    def eval(self, context):
        index = self._index
        real_list = self._real_list
        matrix = _safe_get_matrix(context, index)
        num_required_args = matrix.rows * matrix.cols
        num_given_args = len(real_list)
        if num_given_args != num_required_args:
            raise ArgumentError(num_required_args, num_given_args)
        matrix.contents = real_list


class Pde(Bytecode):
    """Partial differential equation bytecode (apply the stencil)."""
    def __init__(self, stencil_index, matrix_index):
        """:param stencil_index: index of the stencil
        :type stencil_index: :class:`int`
        :param matrix_index: index of the matrix
        :type matrix_index: :class:`int`
        """
        self._stencil_index = stencil_index
        self._matrix_index = matrix_index

    def eval(self, context):
        stencil_index = self._stencil_index
        stencil = _safe_get_matrix(context, stencil_index)
        matrix_index = self._matrix_index
        matrix = _safe_get_matrix(context, matrix_index)
        context.matrices[matrix_index] = context.apply_stencil(stencil, matrix)


class Bne(Bytecode):
    """Branch-not-equal bytecode."""
    def __init__(self, register_index, value, offset):
        """:param register_index: index for register to check
        :type register_index: :class:`int`
        :param value: value with which to compare to register
        :type value: :class:`int`
        :param offset: instruction jump offset
        :type offset: :class:`int`
        """
        self._register_index = register_index
        self._value = value
        self._offset = offset

    def eval(self, context):
        destination = context.pc + self._offset
        if (self._offset == 0 or
                destination >= context.program_length or
                destination < 0):
            raise InvalidBranchOffsetError(self._offset, destination)
        register_value = _safe_get_register(context, self._register_index)
        if register_value != self._value:
            # Subtract one because the main loop increment will add another.
            context.pc = destination - 1


BYTECODES = [cls.__name__.upper() for cls in Bytecode.__subclasses__()]
"""All language bytecodes."""
