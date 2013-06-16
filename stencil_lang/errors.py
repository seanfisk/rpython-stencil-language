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
        valid values are ``'Register'`` or ``'Array'``
        :type type_: :class:`str`
        :param var_num: the number of the variable accessed
        :type var_num: :class:`int`
        """
        self._type = type_
        self._var_num = var_num

    def __str__(self):
        if self._type == 'Register':
            remedy = 'STO'
        elif self._type == 'Array':
            remedy = 'CAR'
        else:
            raise TypeError('Invalid variable type')
        return '%s %d is not initialized. Please %s first.' % (
            self._type, self._var_num, remedy)


class InvalidArrayDimensionsError(StencilLanguageError):
    """Raised when an array is created with invalid dimensions."""
    def __init__(self, array_num, dimensions):
        """:param array_num: created array number
        :type array_num: :class:`int`
        :param dimensions: new dimensions of array
        :type dimensions: :class:`tuple` of (:class:`int`, :class:`int`)
        """
        self._array_num = array_num
        self._dimensions = dimensions

    def __str__(self):
        return 'Invalid positive dimensions for array %d: %s' % (
            self._array_num, self._dimensions)


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


# Get around limitations in RPython: type(error).__name__ does not work. See
# stencil_lang/main.py for more information.
for subclass in StencilLanguageError.__subclasses__():
    subclass.name = subclass.__name__
