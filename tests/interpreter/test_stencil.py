import os.path

from pytest import fixture

from stencil_lang.matrix import from_file
from stencil_lang.interpreter.stencil import apply_stencil

from tests.helpers import fixture_path


@fixture(params=[
    'zeros'
])
def matrix_name(request):
    return request.param


def open_matrix(matrix_type, matrix_name):
    return from_file(fixture_path(os.path.join(matrix_type, matrix_name)))


class TestApplyStencil(object):
    def test_successful_application(self, matrix_name):
        stencil_matrix = open_matrix('stencil', matrix_name)
        before_matrix = open_matrix('before', matrix_name)
        after_matrix = open_matrix('after', matrix_name)
        computed_matrix = apply_stencil(stencil_matrix, before_matrix)
        assert computed_matrix == after_matrix
