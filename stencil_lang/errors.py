""":mod:`stencil_lang.errors` -- Various errors

Currently contains only runtime errors.
"""


class UninitializedVariableError(Exception):
    """Raised when a variable is accessed without being initialized."""
    def __init__(self, type_, var_num, remedy):
        """:param type_: type of the variable accessed, \
        typically ``'register'`` or ``'array'``
        :type type_: :class:`str`
        :param var_num: the number of the variable accessed
        :type var_num: :class:`int`
        :param remedy: instruction to initialize it, \
        typically ``'STO'`` or ``'CAR'``
        :type rememdy: :class:`str`
        """
        self._type = type_
        self._var_num = var_num
        self._remedy = remedy

    def __str__(self):
        return ('%s %d is not initialized. Please %s first.') % (
            self._type.capitalize(), self._var_num, self._remedy)


class InvalidArrayDimensionsError(Exception):
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
            self._array_num,
            self._dimensions)
