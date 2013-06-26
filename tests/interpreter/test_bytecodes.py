from pytest import fixture, raises
from mock import create_autospec, sentinel

from stencil_lang.interpreter.stencil import apply_stencil
from stencil_lang.interpreter.bytecodes import *  # NOQA
from stencil_lang.structures import Matrix
from stencil_lang.structures import Context
from stencil_lang.errors import (
    UninitializedVariableError,
    InvalidMatrixDimensionsError,
    ArgumentError,
)
from stencil_lang.interpreter.evaluator import eval_

from tests.helpers import assert_exc_info_msg, open_matrix


def create_matrix_bytecodes(matrix, matrix_num):
    return [
        Cmx(matrix_num, matrix.rows, matrix.cols),
        Smx(matrix_num, matrix.contents)
    ]


@fixture
def mock_apply_stencil():
    return create_autospec(apply_stencil, spec_set=True)


@fixture
def context(mock_apply_stencil):
    return Context(mock_apply_stencil)


class TestSto(object):
    def test_real(self, context):
        eval_([Sto(10, -768.245)], context)
        assert context.registers[10] == -768.245

    def test_pos_int(self, context):
        eval_([Sto(10, 32)], context)
        assert context.registers[10] == 32

    def test_neg_int(self, context):
        eval_([Sto(10, -88)], context)
        assert context.registers[10] == -88


class TestPr(object):
    def test_sto_pr(self, context, capsys):
        eval_([
            Sto(37, -452.11),
            Pr(37),
        ], context)
        out, err = capsys.readouterr()
        assert '-452.11\n' == out
        assert '' == err

    def test_uninitialized(self, context, capsys):
        with raises(UninitializedVariableError) as exc_info:
            eval_([
                Pr(6),
            ], context)
        assert_exc_info_msg(
            exc_info, 'Register 6 is not initialized. Please STO first.')
        # Should not have printed anything.
        out, err = capsys.readouterr()
        assert '' == out
        assert '' == err


class TestAdd(object):
    def test_sto_add(self, context):
        eval_([
            Sto(10, -88),
            Add(10, 22.2),
        ], context)
        assert context.registers[10] == -65.8

    def test_sto_pr_add_pr(self, context, capsys):
        eval_([
            Sto(10, 45.5),
            Pr(10),
            Add(10, 54.4),
            Pr(10),
        ], context)
        assert context.registers[10] == 99.9
        out, err = capsys.readouterr()
        assert '45.5\n99.9\n' == out
        assert '' == err

    def test_uninitialized(self, context):
        with raises(UninitializedVariableError) as exc_info:
            eval_([
                Add(7, 89.2),
            ], context)
        assert_exc_info_msg(
            exc_info,
            'Register 7 is not initialized. Please STO first.')


class TestCmx(object):
    def test_internals(self, context):
        eval_([
            Cmx(22, 33, 11),
        ], context)
        assert context.matrices[22] == Matrix(33, 11, [])

    def test_zero_rows(self, context):
        with raises(InvalidMatrixDimensionsError) as exc_info:
            eval_([
                Cmx(11, 0, 32),
            ], context)
        assert_exc_info_msg(
            exc_info, "Invalid positive dimensions for matrix 11: (0, 32)")

    def test_zero_cols(self, context):
        with raises(InvalidMatrixDimensionsError) as exc_info:
            eval_([
                Cmx(11, 7, 0),
            ], context)
        assert_exc_info_msg(
            exc_info, "Invalid positive dimensions for matrix 11: (7, 0)")


class TestPmx(object):
    def test_empty(self, context, capsys):
        eval_([
            Cmx(40, 22, 78),
            Pmx(40),
        ], context)
        out, err = capsys.readouterr()
        # Should call __str__ and add a newline.
        assert 'Unpopulated matrix of dimensions (22, 78)\n' == out
        assert '' == err

    def test_uninitialized(self, context, capsys):
        with raises(UninitializedVariableError) as exc_info:
            eval_([
                Pmx(20),
            ], context)
        assert_exc_info_msg(
            exc_info,
            'Matrix 20 is not initialized. Please CMX first.')
        # Should not have printed anything.
        out, err = capsys.readouterr()
        assert '' == out
        assert '' == err

    def test_pmx_one_row_matrix(self, context, capsys):
        eval_([
            Cmx(22, 1, 4),
            Smx(22, [23.2, -42.11, 54.001, 7.11]),
            Pmx(22),
        ], context)
        out, err = capsys.readouterr()
        assert '[[23.2 -42.11 54.001 7.11]]\n' == out
        assert '' == err

    def test_pmx_one_col_matrix(self, context, capsys):
        eval_([
            Cmx(22, 4, 1),
            Smx(22, [23.2, -42.11, 54.001, 7.11]),
            Pmx(22),
        ], context)
        out, err = capsys.readouterr()
        assert '''[[23.2]
 [-42.11]
 [54.001]
 [7.11]]
''' == out
        assert '' == err

    def test_cmx_smx_pmx(self, context, capsys):
        eval_([
            Cmx(31, 2, 3),
            Smx(31, [-13.4, 9876, 45.234, -42, 34.8, -88.2]),
            Pmx(31),
        ], context)
        out, err = capsys.readouterr()
        assert '''[[-13.4 9876 45.234]
 [-42 34.8 -88.2]]
''' == out
        assert '' == err


class TestSmx(object):
    def test_cmx_smx(self, context):
        eval_([
            Cmx(31, 2, 3),
            Smx(31, [-13.4, 9876, 45.234, -42, 34.8, -88.2]),
        ], context)
        assert context.matrices[31] == Matrix(2, 3, [
            -13.4, 9876, 45.234, -42, 34.8, -88.2
        ])

    def test_incorrect_number_of_arguments(self, context):
        with raises(ArgumentError) as exc_info:
            eval_([
                Cmx(31, 2, 3),
                # Missing one
                Smx(31, [-13.4, 9876, 45.234, -42, 34.8]),
            ], context)
        assert_exc_info_msg(
            exc_info, 'Takes exactly 6 arguments (5 given)')

    def test_uninitialized(self, context):
        with raises(UninitializedVariableError) as exc_info:
            eval_([
                # We don't know how large an uninitialized matrix is, so there
                # isn't even a "right" amount of arguments we could give here.
                Smx(7, [1, 10, 71, -32]),
            ], context)
        assert_exc_info_msg(
            exc_info,
            'Matrix 7 is not initialized. Please CMX first.')


class TestPde(object):
    def test_cmx_smx_pde(self, context, mock_apply_stencil):
        mock_apply_stencil.return_value = sentinel.transformed_matrix

        stencil = open_matrix('stencil', 'ints')
        matrix = open_matrix('before', 'ints')
        bytecodes = create_matrix_bytecodes(stencil, 10)
        bytecodes += create_matrix_bytecodes(matrix, 20)
        bytecodes.append(Pde(10, 20))
        eval_(bytecodes, context)

        # Stencil should not have changed.
        assert context.matrices[10] == stencil
        # Matrix should have been swapped with the transformed matrix.
        assert context.matrices[20] == sentinel.transformed_matrix

        mock_apply_stencil.assert_called_once_with(stencil, matrix)

    def test_pde_uninitialized_stencil(self, context, mock_apply_stencil):
        matrix = open_matrix('before', 'ints')
        bytecodes = create_matrix_bytecodes(matrix, 20)
        bytecodes.append(Pde(10, 20))
        with raises(UninitializedVariableError) as exc_info:
            eval_(bytecodes, context)
        assert_exc_info_msg(
            exc_info, 'Matrix 10 is not initialized. Please CMX first.')

        # Matrix should not have changed.
        assert context.matrices[20] == matrix
        # Should not have called apply_stencil.
        assert mock_apply_stencil.call_count == 0

    def test_pde_uninitialized_matrix(self, context, mock_apply_stencil):
        stencil = open_matrix('stencil', 'ints')
        bytecodes = create_matrix_bytecodes(stencil, 10)
        bytecodes.append(Pde(10, 20))
        with raises(UninitializedVariableError) as exc_info:
            eval_(bytecodes, context)
        assert_exc_info_msg(
            exc_info, 'Matrix 20 is not initialized. Please CMX first.')

        # Stencil should not have changed.
        assert context.matrices[10] == stencil
        # Should not have called apply_stencil.
        assert mock_apply_stencil.call_count == 0
