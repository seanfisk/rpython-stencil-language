""":mod:`stencil_lang.errors` -- Various errors

Currently contains only runtime errors.
"""


class UninitializedVariableError(Exception):
    """Raised when a variable is accessed without being initialized."""
    def __init__(self, type_, var_num):
        """:param type_: type of the variable accessed, \
        valid values are ``'register'`` or ``'array'``
        :type type_: :class:`str`
        :param var_num: the number of the variable accessed
        :type var_num: :class:`int`
        """
        self._type = type_
        self._var_num = var_num

    def __str__(self):
        if self._type == 'register':
            remedy = 'STO'
        elif self._type == 'array':
            remedy = 'CAR'
        else:
            raise TypeError('Invalid variable type')
        return ('%s %d is not initialized. Please %s first.') % (
            self._type.capitalize(), self._var_num, remedy)


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
