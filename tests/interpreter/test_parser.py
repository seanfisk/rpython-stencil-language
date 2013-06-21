import sys

from pytest import fixture, raises
from mock import create_autospec, sentinel
from rply import Token

from stencil_lang.interpreter.parser import Parser
from stencil_lang.interpreter.stencil import apply_stencil
from stencil_lang.structures import Matrix
from stencil_lang.errors import (
    UninitializedVariableError,
    InvalidMatrixDimensionsError,
    ArgumentError,
    ParseError,
)

from tests.helpers import lit, assert_exc_info_msg, open_matrix


def make_token_iter(token_tuple_list):
    return iter(Token(name, value) for name, value in token_tuple_list)


def create_matrix_tokens(matrix, matrix_num):
    tokens = [
        lit('CAR'),
        ('POS_INT', str(matrix_num)),
        ('POS_INT', str(matrix.rows)),
        ('POS_INT', str(matrix.cols)),
        lit('SAR'),
        ('POS_INT', str(matrix_num)),
    ]
    for num in matrix.contents:
        if isinstance(num, float):
            token = ('REAL', str(num))
        elif isinstance(num, int):
            if num >= 0:
                token = ('POS_INT', str(num))
            else:
                token = ('NEG_INT', str(num))
        else:
            raise TypeError('Invalid number in matrix!')
        tokens.append(token)
    return tokens


@fixture
def mock_apply_stencil():
    return create_autospec(apply_stencil, spec_set=True)


@fixture
def parser(mock_apply_stencil):
    return Parser(mock_apply_stencil)


class TestParser(object):
    class TestSto(object):
        def test_real(self, parser):
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('REAL', '-768.245'),
            ]))
            # TODO: Implementation detail, so maybe not best candidate for a
            # test.
            assert parser.registers[10] == -768.245

        def test_pos_int(self, parser):
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('POS_INT', '32'),
            ]))
            assert parser.registers[10] == 32

        def test_neg_int(self, parser):
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('NEG_INT', '-88'),
            ]))
            assert parser.registers[10] == -88

        def test_sto_neg_index(self, parser):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    lit('STO'),
                    # STO should only take a POS_INT argument here.
                    ('NEG_INT', '-37'),
                    ('REAL', '42.4'),
                ]))
            assert_exc_info_msg(exc_info, "Unexpected `NEG_INT'")

        def test_end_of_one_line_program(self, parser):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    lit('STO'),
                    ('POS_INT', '37'),
                    # STO is missing a REAL argument
                ]))
            assert_exc_info_msg(exc_info, "Unexpected `$end'")

        def test_large_integer(self, parser):
            # This doesn't test RPython's capabilities, since it's not running
            # translated.
            int_str = '9%d' % sys.maxint
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '31'),
                ('POS_INT', int_str),
            ]))
            assert parser.registers[31] == int(int_str)

        def test_small_integer(self, parser):
            # This doesn't test RPython's capabilities, since it's not running
            # translated.
            int_str = '-9%d' % sys.maxint
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '31'),
                ('POS_INT', int_str),
            ]))
            assert parser.registers[31] == int(int_str)

    class TestPr(object):
        def test_sto_pr(self, parser, capsys):
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '37'),
                ('REAL', '-452.11'),
                lit('PR'),
                ('POS_INT', '37'),
            ]))
            out, err = capsys.readouterr()
            assert out == '-452.11\n'
            assert err == ''

        def test_uninitialized(self, parser, capsys):
            with raises(UninitializedVariableError) as exc_info:
                parser.parse(make_token_iter([
                    lit('PR'),
                    ('POS_INT', '6'),
                ]))
            assert_exc_info_msg(
                exc_info, 'Register 6 is not initialized. Please STO first.')
            # Should not have printed anything.
            out, err = capsys.readouterr()
            assert out == ''
            assert err == ''

        def test_missing_arg(self, parser):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    lit('STO'),
                    ('POS_INT', '37'),
                    ('REAL', '42.3'),
                    lit('PR'),
                    # PR is missing an POS_INT argument
                    lit('PR'),
                    ('POS_INT', '37'),
                ]))
            assert_exc_info_msg(exc_info, "Unexpected `PR'")

    class TestAdd(object):
        def test_sto_add(self, parser):
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('NEG_INT', '-88'),
                lit('ADD'),
                ('POS_INT', '10'),
                ('REAL', '22.2'),
            ]))
            assert parser.registers[10] == -65.8

        def test_sto_pr_add_pr(self, parser, capsys):
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('REAL', '45.5'),
                lit('PR'),
                ('POS_INT', '10'),
                lit('ADD'),
                ('POS_INT', '10'),
                ('REAL', '54.4'),
                lit('PR'),
                ('POS_INT', '10'),
            ]))
            assert parser.registers[10] == 99.9
            out, err = capsys.readouterr()
            assert out == '45.5\n99.9\n'
            assert err == ''

        def test_uninitialized(self, parser):
            with raises(UninitializedVariableError) as exc_info:
                parser.parse(make_token_iter([
                    lit('ADD'),
                    ('POS_INT', '7'),
                    ('REAL', '89.2'),
                ]))
            assert_exc_info_msg(
                exc_info,
                'Register 7 is not initialized. Please STO first.')

    class TestCar(object):
        def test_internals(self, parser):
            parser.parse(make_token_iter([
                lit('CAR'),
                ('POS_INT', '22'),
                ('POS_INT', '33'),
                ('POS_INT', '11'),
            ]))
            assert parser.matrices[22] == Matrix(33, 11, [])

        def test_negative_matrix_index(self, parser):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    lit('CAR'),
                    ('NEG_INT', '-22'),
                    ('POS_INT', '20'),
                    ('POS_INT', '20'),
                ]))
            assert_exc_info_msg(exc_info, "Unexpected `NEG_INT'")

        def test_neg_dimension(self, parser):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    lit('CAR'),
                    ('POS_INT', '11'),
                    ('POS_INT', '12'),
                    ('NEG_INT', '-13'),
                ]))
            assert_exc_info_msg(exc_info, "Unexpected `NEG_INT'")

        def test_zero_rows(self, parser):
            with raises(InvalidMatrixDimensionsError) as exc_info:
                parser.parse(make_token_iter([
                    lit('CAR'),
                    ('POS_INT', '11'),
                    ('POS_INT', '0'),
                    ('POS_INT', '32'),
                ]))
            assert_exc_info_msg(
                exc_info, "Invalid positive dimensions for matrix 11: (0, 32)")

        def test_zero_cols(self, parser):
            with raises(InvalidMatrixDimensionsError) as exc_info:
                parser.parse(make_token_iter([
                    lit('CAR'),
                    ('POS_INT', '11'),
                    ('POS_INT', '7'),
                    ('POS_INT', '0'),
                ]))
            assert_exc_info_msg(
                exc_info, "Invalid positive dimensions for matrix 11: (7, 0)")

    class TestPa(object):
        def test_empty(self, parser, capsys):
            parser.parse(make_token_iter([
                lit('CAR'),
                ('POS_INT', '40'),
                ('POS_INT', '22'),
                ('POS_INT', '78'),
                lit('PA'),
                ('POS_INT', '40'),
            ]))
            out, err = capsys.readouterr()
            # Should call __str__ and add a newline.
            assert out == 'Unpopulated matrix of dimensions (22, 78)\n'
            assert err == ''

        def test_uninitialized(self, parser, capsys):
            with raises(UninitializedVariableError) as exc_info:
                parser.parse(make_token_iter([
                    lit('PA'),
                    ('POS_INT', '20'),
                ]))
            assert_exc_info_msg(
                exc_info,
                'Matrix 20 is not initialized. Please CAR first.')
            # Should not have printed anything.
            out, err = capsys.readouterr()
            assert out == ''
            assert err == ''

        def test_pa_one_row_matrix(self, parser, capsys):
            parser.parse(make_token_iter([
                lit('CAR'),
                ('POS_INT', '22'),
                ('POS_INT', '1'),
                ('POS_INT', '4'),
                lit('SAR'),
                ('POS_INT', '22'),
                ('REAL', '23.2'),
                ('REAL', '-42.11'),
                ('REAL', '54.001'),
                ('REAL', '7.11'),
                lit('PA'),
                ('POS_INT', '22'),
            ]))
            out, err = capsys.readouterr()
            assert out == '[[23.2 -42.11 54.001 7.11]]\n'
            assert err == ''

        def test_pa_one_col_matrix(self, parser, capsys):
            parser.parse(make_token_iter([
                lit('CAR'),
                ('POS_INT', '22'),
                ('POS_INT', '4'),
                ('POS_INT', '1'),
                lit('SAR'),
                ('POS_INT', '22'),
                ('REAL', '23.2'),
                ('REAL', '-42.11'),
                ('REAL', '54.001'),
                ('REAL', '7.11'),
                lit('PA'),
                ('POS_INT', '22'),
            ]))
            out, err = capsys.readouterr()
            assert '''[[23.2]
 [-42.11]
 [54.001]
 [7.11]]
''' == out
            assert err == ''

        def test_car_sar_pa(self, parser, capsys):
            parser.parse(make_token_iter([
                lit('CAR'),
                ('POS_INT', '31'),
                ('POS_INT', '2'),
                ('POS_INT', '3'),
                lit('SAR'),
                ('POS_INT', '31'),
                # Contents
                ('REAL', '-13.4'),
                ('POS_INT', '9876'),
                ('REAL', '45.234'),
                ('POS_INT', '-42'),
                ('REAL', '34.8'),
                ('REAL', '-88.2'),
                lit('PA'),
                ('POS_INT', '31'),
            ]))
            out, err = capsys.readouterr()
            assert '''[[-13.4 9876 45.234]
 [-42 34.8 -88.2]]
''' == out
            assert err == ''

    class TestSar(object):
        def test_car_sar(self, parser):
            parser.parse(make_token_iter([
                lit('CAR'),
                ('POS_INT', '31'),
                ('POS_INT', '2'),
                ('POS_INT', '3'),
                lit('SAR'),
                ('POS_INT', '31'),
                # Contents
                ('REAL', '-13.4'),
                ('POS_INT', '9876'),
                ('REAL', '45.234'),
                ('POS_INT', '-42'),
                ('REAL', '34.8'),
                ('REAL', '-88.2'),
            ]))
            assert parser.matrices[31] == Matrix(2, 3, [
                -13.4, 9876, 45.234, -42, 34.8, -88.2
            ])

        def test_incorrect_number_of_arguments(self, parser):
            with raises(ArgumentError) as exc_info:
                parser.parse(make_token_iter([
                    lit('CAR'),
                    ('POS_INT', '31'),
                    ('POS_INT', '2'),
                    ('POS_INT', '3'),
                    lit('SAR'),
                    ('POS_INT', '31'),
                    # Contents
                    ('REAL', '-13.4'),
                    ('POS_INT', '9876'),
                    ('REAL', '45.234'),
                    ('POS_INT', '-42'),
                    ('REAL', '34.8'),
                    # Missing one
                ]))
            assert_exc_info_msg(
                exc_info, 'Takes exactly 6 arguments (5 given)')

        def test_uninitialized(self, parser):
            with raises(UninitializedVariableError) as exc_info:
                parser.parse(make_token_iter([
                    lit('SAR'),
                    ('POS_INT', '7'),
                    # We don't know how large an uninitialized matrix is, so
                    # there isn't even a "right" amount of arguments we could
                    # give here.
                    ('POS_INT', '1'),
                    ('POS_INT', '10'),
                    ('POS_INT', '71'),
                    ('NEG_INT', '-32'),
                ]))
            assert_exc_info_msg(
                exc_info,
                'Matrix 7 is not initialized. Please CAR first.')

    class TestPde(object):
        def test_car_sar_pde(self, parser, mock_apply_stencil):
            mock_apply_stencil.return_value = sentinel.transformed_matrix

            stencil = open_matrix('stencil', 'ints')
            matrix = open_matrix('before', 'ints')
            tokens = create_matrix_tokens(stencil, 10)
            tokens += create_matrix_tokens(matrix, 20)
            tokens += [
                lit('PDE'),
                ('POS_INT', 10),
                ('POS_INT', 20),
            ]
            parser.parse(make_token_iter(tokens))

            # Stencil should not have changed.
            assert parser.matrices[10] == stencil
            # Matrix should have been swapped with the transformed matrix.
            assert parser.matrices[20] == sentinel.transformed_matrix

            mock_apply_stencil.assert_called_once_with(stencil, matrix)

        def test_pde_uninitialized_stencil(self, parser, mock_apply_stencil):
            matrix = open_matrix('before', 'ints')
            tokens = create_matrix_tokens(matrix, 20)
            tokens += [
                lit('PDE'),
                ('POS_INT', 10),
                ('POS_INT', 20),
            ]
            with raises(UninitializedVariableError) as exc_info:
                parser.parse(make_token_iter(tokens))
            assert_exc_info_msg(
                exc_info, 'Matrix 10 is not initialized. Please CAR first.')

            # Matrix should not have changed.
            assert parser.matrices[20] == matrix
            # Should not have called apply_stencil.
            assert mock_apply_stencil.call_count == 0

        def test_pde_uninitialized_matrix(self, parser, mock_apply_stencil):
            stencil = open_matrix('stencil', 'ints')
            tokens = create_matrix_tokens(stencil, 10)
            tokens += [
                lit('PDE'),
                ('POS_INT', 10),
                ('POS_INT', 20),
            ]
            with raises(UninitializedVariableError) as exc_info:
                parser.parse(make_token_iter(tokens))
            assert_exc_info_msg(
                exc_info, 'Matrix 20 is not initialized. Please CAR first.')

            # Stencil should not have changed.
            assert parser.matrices[10] == stencil
            # Should not have called apply_stencil.
            assert mock_apply_stencil.call_count == 0
