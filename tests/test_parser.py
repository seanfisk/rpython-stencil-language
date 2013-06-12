from pytest import fixture, raises
from rply import Token

from stencil_lang.parser import generate_parser, Context, ParseError


def assert_exc_info_msg(exc_info, expected_msg):
    # LHS and RHS intentionally placed so diffs seem correct.
    assert expected_msg == str(exc_info.value)


def make_token_iter(token_tuple_list):
    return iter(Token(name, value) for name, value in token_tuple_list)


@fixture
def context():
    return Context()


@fixture
def parser():
    return generate_parser()


class TestParser(object):
    class TestInstructions(object):
        def test_sto(self, parser, context):
            parser.parse(make_token_iter([
                ('STO', 'STO'),
                ('INDEX', '10'),
                ('REAL', '-768.245'),
            ]), context)
            # TODO: Implementation detail, so maybe not best candidate for a
            # test.
            assert context.registers[10] == -768.245

        def test_sto_pr(self, parser, context, capsys):
            parser.parse(make_token_iter([
                ('STO', 'STO'),
                ('INDEX', '37'),
                ('REAL', '-452.11'),
                ('PR', 'PR'),
                ('INDEX', '37'),
            ]), context)
            assert context.registers[37] == -452.11
            out, err = capsys.readouterr()
            assert out == '-452.11\n'
            assert err == ''

    class TestErrors(object):
        def test_end_of_one_line_program(self, parser, context):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    ('STO', 'STO'),
                    ('INDEX', '37'),
                    # STO is missing a REAL argument
                ]), context)
            assert_exc_info_msg(
                exc_info, "Unexpected `$end'")

        def test_missing_pr_arg(self, parser, context):
            with raises(ParseError) as exc_info:
                parser.parse(make_token_iter([
                    ('STO', 'STO'),
                    ('INDEX', '37'),
                    ('REAL', '42.3'),
                    ('PR', 'PR'),
                    # PR is missing an INDEX argument
                    ('PR', 'PR'),
                    ('INDEX', '37'),
                ]), context)
            assert_exc_info_msg(
                exc_info, "Unexpected `PR'")
