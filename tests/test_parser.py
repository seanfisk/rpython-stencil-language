from pprint import isreadable

from pytest import fixture, raises
from rply import Token

from stencil_lang.parser import parse, Context, ParseError, TwoDimArray
from stencil_lang.errors import (
    UninitializedVariableError,
    InvalidArrayDimensionsError,
    ArgumentError,
)

from tests.helpers import lit


def assert_exc_info_msg(exc_info, expected_msg):
    # LHS and RHS intentionally placed so diffs seem correct.
    assert expected_msg == str(exc_info.value)


def make_token_iter(token_tuple_list):
    return iter(Token(name, value) for name, value in token_tuple_list)


@fixture
def context():
    return Context()


class TestParser(object):
    class TestValid(object):
        def test_sto_real(self, context):
            parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('REAL', '-768.245'),
            ]), context)
            # TODO: Implementation detail, so maybe not best candidate for a
            # test.
            assert context.registers[10] == -768.245

        def test_sto_pos_int(self, context):
            parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('POS_INT', '32'),
            ]), context)
            assert context.registers[10] == 32

        def test_sto_neg_int(self, context):
            parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('NEG_INT', '-88'),
            ]), context)
            assert context.registers[10] == -88

        def test_sto_pr(self, context, capsys):
            parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '37'),
                ('REAL', '-452.11'),
                lit('PR'),
                ('POS_INT', '37'),
            ]), context)
            out, err = capsys.readouterr()
            assert out == '-452.11\n'
            assert err == ''

        def test_pr_uninitialized(self, context, capsys):
            with raises(UninitializedVariableError) as exc_info:
                parse(make_token_iter([
                    lit('PR'),
                    ('POS_INT', '6'),
                ]), context)
            assert_exc_info_msg(
                exc_info, 'Register 6 is not initialized. Please STO first.')
            # Should not have printed anything.
            out, err = capsys.readouterr()
            assert out == ''
            assert err == ''

        def test_sto_add(self, context):
            parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('NEG_INT', '-88'),
                lit('ADD'),
                ('POS_INT', '10'),
                ('REAL', '22.2'),
            ]), context)
            assert context.registers[10] == -65.8

        def test_sto_pr_add_pr(self, context, capsys):
            parse(make_token_iter([
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
            ]), context)
            assert context.registers[10] == 99.9
            out, err = capsys.readouterr()
            assert out == '45.5\n99.9\n'
            assert err == ''

        def test_add_uninitialized(self, context):
            with raises(UninitializedVariableError) as exc_info:
                parse(make_token_iter([
                    lit('ADD'),
                    ('POS_INT', '7'),
                    ('REAL', '89.2'),
                ]), context)
            assert_exc_info_msg(
                exc_info,
                'Register 7 is not initialized. Please STO first.')

        def test_car(self, context):
            parse(make_token_iter([
                lit('CAR'),
                ('POS_INT', '22'),
                ('POS_INT', '33'),
                ('POS_INT', '11'),
            ]), context)
            assert context.arrays[22] == TwoDimArray(33, 11, [])

        def test_pa_empty(self, context, capsys):
            parse(make_token_iter([
                lit('CAR'),
                ('POS_INT', '40'),
                ('POS_INT', '22'),
                ('POS_INT', '78'),
                lit('PA'),
                ('POS_INT', '40'),
            ]), context)
            out, err = capsys.readouterr()
            # Should call TwoDimArray.__str__ and add a newline.
            assert out == 'Unpopulated array of dimensions (22, 78)\n'
            assert err == ''

        def test_pa_uninitialized_array(self, context, capsys):
            with raises(UninitializedVariableError) as exc_info:
                parse(make_token_iter([
                    lit('PA'),
                    ('POS_INT', '20'),
                ]), context)
            assert_exc_info_msg(
                exc_info,
                'Array 20 is not initialized. Please CAR first.')
            # Should not have printed anything.
            out, err = capsys.readouterr()
            assert out == ''
            assert err == ''

        def test_sar(self, context):
            parse(make_token_iter([
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
            ]), context)
            assert context.arrays[31] == TwoDimArray(2, 3, [
                -13.4, 9876, 45.234, -42, 34.8, -88.2
            ])

        def test_sar_incorrect_number_of_arguments(self, context):
            with raises(ArgumentError) as exc_info:
                parse(make_token_iter([
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
                ]), context)
            assert_exc_info_msg(
                exc_info, 'Takes exactly 6 arguments (5 given)')

        def test_car_sar_pa(self, context, capsys):
            parse(make_token_iter([
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
            ]), context)
            out, err = capsys.readouterr()
            assert out == '''[[-13.4 9876 45.234]
[-42 34.8 -88.2]]
'''
            assert err == ''

        def test_sar_uninitialized(self, context):
            with raises(UninitializedVariableError) as exc_info:
                parse(make_token_iter([
                    lit('SAR'),
                    ('POS_INT', '7'),
                    # We don't know how large an uninitialized array is, so
                    # there isn't even a "right" amount of arguments we could
                    # give here.
                    ('POS_INT', '1'),
                    ('POS_INT', '10'),
                    ('POS_INT', '71'),
                    ('NEG_INT', '-32'),
                ]), context)
            assert_exc_info_msg(
                exc_info,
                'Array 7 is not initialized. Please CAR first.')

    class TestInvalid(object):
        def test_sto_neg_index(self, context):
            with raises(ParseError) as exc_info:
                parse(make_token_iter([
                    lit('STO'),
                    # STO should only take a POS_INT argument here.
                    ('NEG_INT', '-37'),
                    ('REAL', '42.4'),
                ]), context)
            assert_exc_info_msg(exc_info, "Unexpected `NEG_INT'")

        def test_end_of_one_line_program(self, context):
            with raises(ParseError) as exc_info:
                parse(make_token_iter([
                    lit('STO'),
                    ('POS_INT', '37'),
                    # STO is missing a REAL argument
                ]), context)
            assert_exc_info_msg(exc_info, "Unexpected `$end'")

        def test_missing_pr_arg(self, context):
            with raises(ParseError) as exc_info:
                parse(make_token_iter([
                    lit('STO'),
                    ('POS_INT', '37'),
                    ('REAL', '42.3'),
                    lit('PR'),
                    # PR is missing an POS_INT argument
                    lit('PR'),
                    ('POS_INT', '37'),
                ]), context)
            assert_exc_info_msg(exc_info, "Unexpected `PR'")

        def test_car_neg_dimension(self, context):
            with raises(ParseError) as exc_info:
                parse(make_token_iter([
                    lit('CAR'),
                    ('POS_INT', '11'),
                    ('POS_INT', '12'),
                    ('NEG_INT', '-13'),
                ]), context)
            assert_exc_info_msg(exc_info, "Unexpected `NEG_INT'")

        def test_car_zero_rows(self, context):
            with raises(InvalidArrayDimensionsError) as exc_info:
                parse(make_token_iter([
                    lit('CAR'),
                    ('POS_INT', '11'),
                    ('POS_INT', '0'),
                    ('POS_INT', '32'),
                ]), context)
            assert_exc_info_msg(
                exc_info, "Invalid positive dimensions for array 11: (0, 32)")

        def test_car_zero_cols(self, context):
            with raises(InvalidArrayDimensionsError) as exc_info:
                parse(make_token_iter([
                    lit('CAR'),
                    ('POS_INT', '11'),
                    ('POS_INT', '7'),
                    ('POS_INT', '0'),
                ]), context)
            assert_exc_info_msg(
                exc_info, "Invalid positive dimensions for array 11: (7, 0)")


class TestTwoDimArray(object):
    class TestEquality(object):
        def test_empty(self):
            assert TwoDimArray(4, 5, []) == TwoDimArray(4, 5, [])

        def test_full(self):
            assert (TwoDimArray(2, 3, range(6)) ==
                    TwoDimArray(2, 3, range(6)))

        def test_readable(self):
            assert isreadable(TwoDimArray(2, 4, range(11)))

    class TestRepr(object):
        def test_empty(self):
            assert (repr(TwoDimArray(20, 30, [])) ==
                    'TwoDimArray(20, 30, [])')

        def test_full(self):
            assert (
                repr(TwoDimArray(2, 3, [45, 26, -32.5, 11.1, 0.5, -0.2])) ==
                'TwoDimArray(2, 3, [45, 26, -32.5, 11.1, 0.5, -0.2])')

    class TestStr(object):
        def test_empty(self):
            assert (str(TwoDimArray(4, 5, [])) ==
                    'Unpopulated array of dimensions (4, 5)')

        def test_full_small(self):
            # Typical assert order reversed for a nicer multiline diff.
            assert '''[[0 1 2]
[3 4 5]]''' == str(TwoDimArray(2, 3, range(6)))

        def test_full_big(self):
            # Typical assert order reversed for a nicer multiline diff.
            assert '''[[45 26]
[-32.5 11]
[-42.5 73.2000001]
[11.1 -0.2]]''' == str(TwoDimArray(4, 2, [
                45, 26, -32.5, 11, -42.5, 73.2000001, 11.1, -0.2]))
