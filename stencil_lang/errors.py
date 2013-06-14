""":mod:`stencil_lang.errors` -- Various errors

Currently contains only runtime errors.
"""


class UninitializedRegisterError(Exception):
    """Raised when a register is modified without being initialized."""
    def __init__(self, register_num):
        """:param register_num: the register that was modified
        :type register_num: :class:`int`
        """
        self._register_num = register_num

    def __str__(self):
        return ('Attempt to modify uninitialized register %d. '
                'Please STO first.') % self._register_num
