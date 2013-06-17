from pytest import raises

from stencil_lang.matrix import from_string, from_file
from stencil_lang.errors import InconsistentMatrixDimensions
from stencil_lang.structures import Matrix

from tests.helpers import assert_exc_info_msg, fixture_path


class TestMatrix(object):
    def test_empty(self):
        assert from_string('') == Matrix(0, 0, [])

    def test_single(self):
        # Must end in a newline.
        assert from_string('34.2\n') == Matrix(1, 1, [34.2])

    def test_square(self):
        assert from_string('''11.7 52
-34 -12.2
''') == Matrix(2, 2, [11.7, 52, -34, -12.2])

    def test_inconsistent_dims(self):
        with raises(InconsistentMatrixDimensions) as exc_info:
            from_string('''34 5
2
''')
        assert_exc_info_msg(
            exc_info,
            'Inconsistent columns in current row (1) '
            'from those in the first row (2)')

    def test_simple_file(self):
        # Make sure to end this file with a newline.
        assert (from_file(fixture_path('simple.matrix')) ==
                Matrix(2, 2, [11.7, 52, -34, -12.2]))
