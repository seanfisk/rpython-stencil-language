""":mod:`stencil_lang.errors` -- Various errors

Currently contains only runtime errors.
"""


class UninitializedRegisterError(Exception):
    """Raised when a register is accessed without being initialized."""
    def __init__(self, register_num):
        """:param register_num: the register that was accessed
        :type register_num: :class:`int`
        """
        self._register_num = register_num

    def __str__(self):
        return ('Attempt to modify uninitialized register %d. '
                'Please STO first.') % self._register_num


class UninitializedArrayError(Exception):
    """Raised when an array is accessed without being initialized."""
    def __init__(self, array_num):
        """:param array_num: the array that was accessed
        :type array_num: :class:`int`
        """
        self._array_num = array_num

    def __str__(self):
        return ('Attempt to modify uninitialized array %d. '
                'Please SAR first.') % self._array_num


class InvalidArrayDimensions(Exception):
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
