from pytest import fixture, raises
from rply import Token

from stencil_lang.parser import parser, Context, ParseError, TwoDimArray
from stencil_lang.errors import UninitializedRegisterError

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
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('REAL', '-768.245'),
            ]), context)
            # TODO: Implementation detail, so maybe not best candidate for a
            # test.
            assert context.registers[10] == -768.245

        def test_sto_pos_int(self, context):
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('POS_INT', '32'),
            ]), context)
            assert context.registers[10] == 32

        def test_sto_neg_int(self, context):
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('NEG_INT', '-88'),
            ]), context)
            assert context.registers[10] == -88

        def test_sto_pr(self, context, capsys):
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '37'),
                ('REAL', '-452.11'),
                lit('PR'),
                ('POS_INT', '37'),
            ]), context)
            assert context.registers[37] == -452.11
            out, err = capsys.readouterr()
            assert out == '-452.11\n'
            assert err == ''

        def test_sto_add(self, context):
            parser.parse(make_token_iter([
                lit('STO'),
                ('POS_INT', '10'),
                ('NEG_INT', '-88'),
                lit('ADD'),
                ('POS_INT', '10'),
                ('REAL', '22.2'),
            ]), context)
            assert context.registers[10] == -65.8

        def test_sto_pr_add_pr(self, context, capsys):
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
            ]), context)
            assert context.registers[10] == 99.9
            out, err = capsys.readouterr()
            assert out == '45.5\n99.9\n'
            assert err == ''

        def test_add_without_sto_first(self, context):
            with raises(UninitializedRegisterError) as exc_info:
                parser.parse(make_token_iter([
                    lit('ADD'),
                    ('POS_INT', '7'),
                    ('REAL', '89.2'),
                ]), context)
            assert_exc_info_msg(
                exc_info,
                'Attempt to modify uninitialized register 7. '
                'Please STO first.')

        def test_car(self, context):
            parser.parse(make_token_iter([
                lit('CAR'),
                ('POS_INT', '22'),
                ('POS_INT', '33'),
                ('POS_INT', '11'),
            ]), context)
            assert context.arrays[22] == TwoDimArray((33, 11), [])

    class TestInvalid(object):
        def test_sto_neg_index(self, context):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    lit('STO'),
                    # STO should only take a POS_INT argument here.
                    ('NEG_INT', '-37'),
                    ('REAL', '42.4'),
                ]), context)
            assert_exc_info_msg(
                exc_info, "Unexpected `NEG_INT'")

        def test_end_of_one_line_program(self, context):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    lit('STO'),
                    ('POS_INT', '37'),
                    # STO is missing a REAL argument
                ]), context)
            assert_exc_info_msg(
                exc_info, "Unexpected `$end'")

        def test_missing_pr_arg(self, context):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    lit('STO'),
                    ('POS_INT', '37'),
                    ('REAL', '42.3'),
                    lit('PR'),
                    # PR is missing an POS_INT argument
                    lit('PR'),
                    ('POS_INT', '37'),
                ]), context)
            assert_exc_info_msg(
                exc_info, "Unexpected `PR'")


class TestTwoDimArray(object):
    class TestEquality(object):
        def test_empty(self):
            assert TwoDimArray((4, 5), []) == TwoDimArray((4, 5), [])

        def test_full(self):
            assert (TwoDimArray((2, 3), range(6)) ==
                    TwoDimArray((2, 3), range(6)))

    class TestRepr(object):
        def test_empty(self):
            assert (repr(TwoDimArray((20, 30), [])) ==
                    'TwoDimArray((20, 30), [])')

        def test_full(self):
            assert (
                repr(TwoDimArray((2, 3), [45, 26, -32.5, 11.1, 0.5, -0.2])) ==
                'TwoDimArray((2, 3), [45, 26, -32.5, 11.1, 0.5, -0.2])')
