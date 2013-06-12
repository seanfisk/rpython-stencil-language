from pytest import fixture, raises
from rply import Token

from stencil_lang.lexer import generate_lexer


def assert_lex_token_list(lexer, code, expected_token_tuples):
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


@fixture
def lexer():
    return generate_lexer()


class TestLexer(object):
    def test_sto_pr(self, lexer):
        code = '''
STO 1 32.3
PR 2
STO 10 -0.1
PR 32
'''
        assert_lex_token_list(lexer, code, [
            ('STO', 'STO'),
            ('INDEX', '1'),
            ('REAL', '32.3'),
            ('PR', 'PR'),
            ('INDEX', '2'),
            ('STO', 'STO'),
            ('INDEX', '10'),
            ('REAL', '-0.1'),
            ('PR', 'PR'),
            ('INDEX', '32'),
        ])
