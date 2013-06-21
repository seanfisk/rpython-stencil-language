""":mod:`stencil_lang.errors` -- Various errors

Currently contains only runtime errors.
"""


class StencilLanguageError(Exception):
    """Base class for all stencil language interpreter errors."""
    pass


class UninitializedVariableError(StencilLanguageError):
    """Raised when a variable is accessed without being initialized."""
    def __init__(self, type_, var_num):
        """:param type_: type of the variable accessed, \
        valid values are ``'Register'`` or ``'Matrix'``
        :type type_: :class:`str`
        :param var_num: the number of the variable accessed
        :type var_num: :class:`int`
        """
        self._type = type_
        self._var_num = var_num

    def __str__(self):
        if self._type == 'Register':
            remedy = 'STO'
        elif self._type == 'Matrix':
            remedy = 'CAR'
        else:
            raise TypeError('Invalid variable type: %s' % self._type)
        return '%s %d is not initialized. Please %s first.' % (
            self._type, self._var_num, remedy)


class InvalidMatrixDimensionsError(StencilLanguageError):
    """Raised when an matrix is created with invalid dimensions."""
    def __init__(self, matrix_num, dimensions):
        """:param matrix_num: created matrix number
        :type matrix_num: :class:`int`
        :param dimensions: new dimensions of matrix
        :type dimensions: :class:`tuple` of (:class:`int`, :class:`int`)
        """
        self._matrix_num = matrix_num
        self._dimensions = dimensions

    def __str__(self):
        return 'Invalid positive dimensions for matrix %d: %s' % (
            self._matrix_num, self._dimensions)


class ArgumentError(StencilLanguageError):
    """Raised when an incorrect number of arguments is given."""
    def __init__(self, num_args_required, num_args_given):
        """:param num_args_required: Required number of args
        :type num_args_required: :class:`int`
        :param num_args_given: Given number of args
        :type num_args_given: :class:`int`
        """
        self._num_args_required = num_args_required
        self._num_args_given = num_args_given

    def __str__(self):
        return 'Takes exactly %d arguments (%d given)' % (
            self._num_args_required, self._num_args_given)


class ParseError(StencilLanguageError):
    """Raised when parser encounters a generic issue."""
    def __init__(self, token_name):
        """:param token_name: name of the token that caused the error
        :type token_name: :class:`str`
        """
        self._token_name = token_name

    def __str__(self):
        return "Unexpected `%s'" % self._token_name


class InconsistentMatrixDimensions(StencilLanguageError):
    """Raised when matrix dimensions are no longer consistent."""
    def __init__(self, first_row_cols, current_cols):
        """:param first_row_cols: Number of columns in the first row
        :type first_row_cols: :class:`int`
        :param current_cols: Number of columns in the current row
        :type current_cols: :class:`int`
        """
        self._first_row_cols = first_row_cols
        self._current_cols = current_cols

    def __str__(self):
        return ('Inconsistent columns in current row (%d) '
                'from those in the first row (%d)') % (
                    self._current_cols, self._first_row_cols)


class InvalidStencilDimensionsError(StencilLanguageError):
    """Raised when an matrix is attempted to be used as a stencil and its
    dimensions are not correct for that usage."""
    def __init__(self, dimensions):
        """:param dimensions: new dimensions of matrix
        :type dimensions: :class:`list` of (:class:`int`, :class:`int`)
        """
        self._dimensions = dimensions

    def __str__(self):
        return 'Invalid odd dimensions for stencil: (%d, %d)' % (
            self._dimensions[0], self._dimensions[1])


# Get around limitations in RPython: type(error).__name__ does not work. See
# stencil_lang/main.py for more information.
#
# Use `_subclass' instead of `subclass' so that docs don't pick it up (it is
# indicated "private").
for _subclass in StencilLanguageError.__subclasses__():
    _subclass.name = _subclass.__name__
