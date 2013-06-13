from pytest import raises
from rply import Token
from rply.errors import LexingError

from stencil_lang.lexer import lexer


def assert_lex_token_list(code, expected_token_tuples):
    stream = lexer.lex(code)

    # For some reason, pytest always says there is a diff at index 0, even when
    # it occurs elsewhere in the list. Falling back to asserting in a loop.
    # expected_tokens = [
    #     Token(name, value) for name, value in expected_token_tuples]
    # assert list(lexer.lex(code)) == expected_tokens

    for name, value in expected_token_tuples:
        computed_token = next(stream)
        expected_token = Token(name, value)
        assert computed_token == expected_token

    with raises(StopIteration):
        next(stream)


class TestLexer(object):
    class TestValid(object):
        def test_sto(self):
            assert_lex_token_list('STO', [('STO', 'STO')])

        def test_pos_int(self):
            assert_lex_token_list('20', [('POS_INT', '20')])

        def test_pos_int_leading_zero(self):
            assert_lex_token_list('0020', [('POS_INT', '0020')])

        def test_neg_int(self):
            assert_lex_token_list('-78', [('NEG_INT', '-78')])

        def test_neg_int_leading_zero(self):
            assert_lex_token_list('-078', [('NEG_INT', '-078')])

        def test_sto_pr(self):
            code = '''
    STO 1 32.3
    PR 2
    STO 10 -0.1
    PR 32
    '''
            assert_lex_token_list(code, [
                ('STO', 'STO'),
                ('POS_INT', '1'),
                ('REAL', '32.3'),
                ('PR', 'PR'),
                ('POS_INT', '2'),
                ('STO', 'STO'),
                ('POS_INT', '10'),
                ('REAL', '-0.1'),
                ('PR', 'PR'),
                ('POS_INT', '32'),
            ])

    class TestInvalid(object):
        def test_nothing(self):
            stream = lexer.lex('')
            with raises(StopIteration):
                next(stream)

        def test_invalid_token(self):
            stream = lexer.lex('ABCD')
            with raises(LexingError):
                next(stream)

        def test_invalid_sto(self):
            stream = lexer.lex('STO 1 hello')
            for _ in xrange(2):
                next(stream)
            with raises(LexingError):
                next(stream)

        def test_invalid_next_instruction(self):
            stream = lexer.lex('STO 1 123.3\nawesome')
            for _ in xrange(3):
                next(stream)
            with raises(LexingError):
                next(stream)

        def test_invalid_continues_to_raise_lexing_errors(self):
            stream = lexer.lex('ABCD')
            for _ in xrange(5):
                with raises(LexingError):
                    next(stream)
