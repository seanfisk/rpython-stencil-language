import os

from pytest import fixture, raises

from stencil_lang.interpreter.stencil import apply_stencil
from stencil_lang.structures import Matrix
from stencil_lang.errors import InvalidStencilDimensionsError

from tests.helpers import fixture_path, assert_exc_info_msg, open_matrix


@fixture(params=os.listdir(fixture_path('stencil')))
def matrix_name(request):
    return request.param


class TestApplyStencil(object):
    def test_successful_application(self, matrix_name):
        stencil_matrix = open_matrix('stencil', matrix_name)
        before_matrix = open_matrix('before', matrix_name)
        after_matrix = open_matrix('after', matrix_name)
        computed_matrix = apply_stencil(stencil_matrix, before_matrix)
        assert computed_matrix == after_matrix

    def test_zero_dimension(self):
        with raises(InvalidStencilDimensionsError) as exc_info:
            apply_stencil(Matrix(0, 4, []), Matrix(4, 4, range(16)))
        assert_exc_info_msg(
            exc_info, 'Invalid odd dimensions for stencil: (0, 4)')

    def test_even_dimension(self):
        with raises(InvalidStencilDimensionsError) as exc_info:
            apply_stencil(Matrix(2, 2, range(4)), Matrix(4, 4, range(16)))
        assert_exc_info_msg(
            exc_info, 'Invalid odd dimensions for stencil: (2, 2)')
