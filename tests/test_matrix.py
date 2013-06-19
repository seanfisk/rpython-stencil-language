from pytest import raises, fixture
from rply.errors import LexingError

from stencil_lang.matrix import from_string, from_file
from stencil_lang.errors import InconsistentMatrixDimensions
from stencil_lang.structures import Matrix

from tests.helpers import assert_exc_info_msg, fixture_path


class TestFromString(object):
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

    def test_lex_error(self):
        with raises(LexingError):
            from_string('ABCD')

    # TODO: cannot test ParsingError because there is nothing that the parser
    # knows about but doesn't expect (e.g., numbers).


@fixture(params=['simple-newline', 'simple-no-newline'])
def matrix_name(request):
    return request.param


class TestFromFile(object):
    def test_simple(self, matrix_name):
        assert (from_file(fixture_path(matrix_name)) ==
                Matrix(2, 2, [11.7, 52, -34, -12.2]))
