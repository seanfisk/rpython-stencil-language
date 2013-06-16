from pytest import raises
from rply import Token
from rply.errors import LexingError

from stencil_lang.lexer import lex

from tests.helpers import lit


def assert_lex_token_list(code, expected_token_tuples):
    stream = lex(code)

    # For some reason, pytest always says there is a diff at index 0, even when
    # it occurs elsewhere in the list. Falling back to asserting in a loop.
    # expected_tokens = [
    #     Token(name, value) for name, value in expected_token_tuples]
    # assert list(lex(code)) == expected_tokens

    for name, value in expected_token_tuples:
        computed_token = next(stream)
        expected_token = Token(name, value)
        assert computed_token == expected_token

    with raises(StopIteration):
        next(stream)


class TestLexer(object):
    class TestValid(object):
        def test_sto(self):
            assert_lex_token_list('STO', [lit('STO')])

        def test_pr(self):
            assert_lex_token_list('PR', [lit('PR')])

        def test_add(self):
            assert_lex_token_list('ADD', [lit('ADD')])

        def test_car(self):
            assert_lex_token_list('CAR', [lit('CAR')])

        def test_pa(self):
            assert_lex_token_list('PA', [lit('PA')])

        def test_sar(self):
            assert_lex_token_list('SAR', [lit('SAR')])

        def test_pos_int(self):
            assert_lex_token_list('20', [('POS_INT', '20')])

        def test_pos_int_leading_zero(self):
            assert_lex_token_list('0020', [('POS_INT', '0020')])

        def test_neg_int(self):
            assert_lex_token_list('-78', [('NEG_INT', '-78')])

        def test_neg_int_leading_zero(self):
            assert_lex_token_list('-078', [('NEG_INT', '-078')])

        def test_sto_pr(self):
            code = '''STO 1 32.3
PR 2
STO 10 -0.1
PR 32
'''
            assert_lex_token_list(code, [
                lit('STO'),
                ('POS_INT', '1'),
                ('REAL', '32.3'),
                lit('PR'),
                ('POS_INT', '2'),
                lit('STO'),
                ('POS_INT', '10'),
                ('REAL', '-0.1'),
                lit('PR'),
                ('POS_INT', '32'),
            ])

        def test_pr_car_add(self):
            code = '''CAR 32 11 7
PR 11
ADD 1 2.2
'''
            assert_lex_token_list(code, [
                lit('CAR'),
                ('POS_INT', '32'),
                ('POS_INT', '11'),
                ('POS_INT', '7'),
                lit('PR'),
                ('POS_INT', '11'),
                lit('ADD'),
                ('POS_INT', '1'),
                ('REAL', '2.2'),
            ])

    class TestInvalid(object):
        def test_nothing(self):
            stream = lex('')
            with raises(StopIteration):
                next(stream)

        def test_invalid_token(self):
            stream = lex('ABCD')
            with raises(LexingError):
                next(stream)

        def test_invalid_sto(self):
            stream = lex('STO 1 hello')
            for _ in xrange(2):
                next(stream)
            with raises(LexingError):
                next(stream)

        def test_invalid_next_instruction(self):
            stream = lex('STO 1 123.3\nawesome')
            for _ in xrange(3):
                next(stream)
            with raises(LexingError):
                next(stream)

        def test_invalid_continues_to_raise_lexing_errors(self):
            stream = lex('ABCD')
            for _ in xrange(5):
                with raises(LexingError):
                    next(stream)
