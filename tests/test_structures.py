from pprint import isreadable

from pytest import fixture, raises

from stencil_lang.structures import Matrix, ValueBox, Bytecode

from tests.helpers import assert_exc_info_msg


@fixture
def mat():
    return Matrix(3, 4, range(12))


class TestValueBox(object):
    def test_repr(self):
        box = ValueBox(['abcd', 123])
        assert repr(box) == "ValueBox(['abcd', 123])"


class TestMatrix(object):
    class TestEqNe(object):
        def test_empty(self):
            assert Matrix(4, 5, []) == Matrix(4, 5, [])

        def test_full(self):
            assert Matrix(2, 3, range(6)) == Matrix(2, 3, range(6))

        def test_ne(self):
            assert Matrix(2, 2, range(4)) != Matrix(2, 2, range(1, 5))

    class TestGetitem(object):
        def test_regular(self, mat):
            assert mat.getitem([0, 2]) == 2

        def test_negative_error(self, mat):
            with raises(ValueError) as exc_info:
                mat.getitem([-1, 5])
            assert_exc_info_msg(
                exc_info, 'Matrix indices must be non-negative. '
                "Use `getitem_wraparound' for wrap-around behavior.")

        def test_list_length_one(self, mat):
            with raises(TypeError) as exc_info:
                mat.getitem([1])
            assert_exc_info_msg(
                exc_info,
                'Matrix indices must be a list of integers of length 2')

        def test_str(self, mat):
            with raises(TypeError) as exc_info:
                mat.getitem('abcd')
            assert_exc_info_msg(
                exc_info,
                'Matrix indices must be a list of integers of length 2')

    class TestGetitemWraparound(object):
        def test_regular(self, mat):
            assert mat.getitem_wraparound([0, 2]) == 2

        def test_negative(self, mat):
            assert mat.getitem_wraparound([-2, 1]) == 5

        def test_double_negative(self, mat):
            assert mat.getitem_wraparound([-1, -1]) == 11

        def test_past_bounds(self, mat):
            assert mat.getitem_wraparound([4, 0]) == 4

        def test_double_past_bounds(self, mat):
            assert mat.getitem_wraparound([4, 4]) == 4

        def test_double_wraparound(self, mat):
            assert mat.getitem_wraparound([6, -6]) == 2

        def test_list_length_one(self, mat):
            with raises(TypeError) as exc_info:
                mat.getitem([1])
            assert_exc_info_msg(
                exc_info,
                'Matrix indices must be a list of integers of length 2')

        def test_str(self, mat):
            with raises(TypeError) as exc_info:
                mat.getitem('abcd')
            assert_exc_info_msg(
                exc_info,
                'Matrix indices must be a list of integers of length 2')

    class TestRepr(object):
        def test_empty(self):
            assert (repr(Matrix(20, 30, [])) ==
                    'Matrix(20, 30, [])')

        def test_full(self):
            assert (
                repr(Matrix(2, 3, [45, 26, -32.5, 11.1, 0.5, -0.2])) ==
                'Matrix(2, 3, [45, 26, -32.5, 11.1, 0.5, -0.2])')

        def test_readable(self):
            assert isreadable(Matrix(2, 4, range(8)))

    class TestStr(object):
        def test_empty(self):
            assert ('Unpopulated matrix of dimensions (4, 5)' ==
                    str(Matrix(4, 5, [])))

        def test_full_small(self):
            # Typical assert order reversed for a nicer multiline diff.
            assert '''[[ 0 1 2 ]
 [ 3 4 5 ]]''' == str(Matrix(2, 3, range(6)))

        def test_full_big(self):
            # Output style is inspired by NumPy. However, this one is an
            # evenly-spaced grid with points aligned. The integer part is right
            # aligned and its width is equal to the width of the maximal
            # integer part. The fractional part is aligned left and its width
            # is equal to the width of the maximal fractional part.
            assert (
                '[[  12.3        7.800001   4          0.398    -11        ]\n'
                ' [ -22.357     34.2      -11.11111   42.2        0.104    ]]'
                == str(Matrix(
                    2, 5, [
                        12.3, 7.800001, 4, 0.398, -11,
                        -22.357, 34.2, -11.11111, 42.2, 0.104])))

    class TestAsPlainString(object):
        # Make sure to not print trailing whitespace.
        def test_small(self):
            assert '''-456.4     52.2     -0.243
  42       67      -99''' == Matrix(2, 3, [
                -456.4, 52.2, -0.243, 42, 67, -99]).as_plain_string()


class Bytecode1(Bytecode):
    def __init__(self, a, b):
        self.a = a
        self.b = b


class Bytecode2(Bytecode):
    def __init__(self, c, d):
        self.c = c
        self.d = d


class Bytecode3(Bytecode):
    def __init__(self, a, b):
        self.a = a
        self.b = b


class TestBytecode:
    class TestEqNe:
        def test_should_equal(self):
            assert Bytecode1(10, -20) == Bytecode1(10, -20)

        def test_different_attr_values(self):
            assert Bytecode1(0, 1) != Bytecode2(0, -1)

        def test_different_attrs(self):
            assert Bytecode1(30, 40) != Bytecode2(30, 40)

        def test_same_attr_values_different_class(self):
            assert Bytecode1(30, 40) != Bytecode3(30, 40)
