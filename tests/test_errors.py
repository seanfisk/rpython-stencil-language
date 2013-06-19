from pytest import raises

from tests.helpers import assert_exc_info_msg

from stencil_lang.errors import UninitializedVariableError


class TestUninitVar(object):
    def test_raises_on_invalid_type(self):
        error = UninitializedVariableError('Invalid', 20)
        with raises(TypeError) as exc_info:
            str(error)
        assert_exc_info_msg(exc_info, 'Invalid variable type: Invalid')
