from pytest import fixture, raises
from rply import Token

from stencil_lang.parser import parser, Context, ParseError


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
                ('STO', 'STO'),
                ('POS_INT', '10'),
                ('REAL', '-768.245'),
            ]), context)
            # TODO: Implementation detail, so maybe not best candidate for a
            # test.
            assert context.registers[10] == -768.245

        def test_sto_pos_int(self, context):
            parser.parse(make_token_iter([
                ('STO', 'STO'),
                ('POS_INT', '10'),
                ('POS_INT', '32'),
            ]), context)
            assert context.registers[10] == 32

        def test_sto_neg_int(self, context):
            parser.parse(make_token_iter([
                ('STO', 'STO'),
                ('POS_INT', '10'),
                ('NEG_INT', '-88'),
            ]), context)
            assert context.registers[10] == -88

        def test_sto_pr(self, context, capsys):
            parser.parse(make_token_iter([
                ('STO', 'STO'),
                ('POS_INT', '37'),
                ('REAL', '-452.11'),
                ('PR', 'PR'),
                ('POS_INT', '37'),
            ]), context)
            assert context.registers[37] == -452.11
            out, err = capsys.readouterr()
            assert out == '-452.11\n'
            assert err == ''

    class TestInvalid(object):
        def test_sto_neg_index(self, context):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    ('STO', 'STO'),
                    # STO should only take a POS_INT argument here.
                    ('NEG_INT', '-37'),
                    ('REAL', '42.4'),
                ]), context)
            assert_exc_info_msg(
                exc_info, "Unexpected `NEG_INT'")

        def test_end_of_one_line_program(self, context):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    ('STO', 'STO'),
                    ('POS_INT', '37'),
                    # STO is missing a REAL argument
                ]), context)
            assert_exc_info_msg(
                exc_info, "Unexpected `$end'")

        def test_missing_pr_arg(self, context):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    ('STO', 'STO'),
                    ('POS_INT', '37'),
                    ('REAL', '42.3'),
                    ('PR', 'PR'),
                    # PR is missing an POS_INT argument
                    ('PR', 'PR'),
                    ('POS_INT', '37'),
                ]), context)
            assert_exc_info_msg(
                exc_info, "Unexpected `PR'")
