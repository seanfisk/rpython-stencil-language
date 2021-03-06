from pytest import raises
import pytest
parametrize = pytest.mark.parametrize
from rply import Token
from rply.errors import LexingError

from stencil_lang.interpreter.lexer import lex

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

        def test_cmx(self):
            assert_lex_token_list('CMX', [lit('CMX')])

        def test_pmx(self):
            assert_lex_token_list('PMX', [lit('PMX')])

        def test_smx(self):
            assert_lex_token_list('SMX', [lit('SMX')])

        def test_smxf(self):
            assert_lex_token_list('SMXF', [lit('SMXF')])

        def test_pde(self):
            assert_lex_token_list('PDE', [lit('PDE')])

        def test_bne(self):
            assert_lex_token_list('BNE', [lit('BNE')])

        def test_pos_int(self):
            assert_lex_token_list('20', [('POS_INT', '20')])

        def test_pos_int_leading_zero(self):
            assert_lex_token_list('0020', [('POS_INT', '0020')])

        def test_neg_int(self):
            assert_lex_token_list('-78', [('NEG_INT', '-78')])

        def test_neg_int_leading_zero(self):
            assert_lex_token_list('-078', [('NEG_INT', '-078')])

        @parametrize('real', ['1.2e10', '10e2', '-9.1e-3', '5e-6'])
        def test_real_scientific_notation(self, real):
            assert_lex_token_list(real, [('REAL_SCI', real)])

        def test_filename_without_spaces(self):
            assert_lex_token_list('"file/name/withoutspaces"',
                                  [('FILENAME', '"file/name/withoutspaces"')])

        def test_filename_with_spaces(self):
            assert_lex_token_list('"file/name/with spaces"',
                                  [('FILENAME', '"file/name/with spaces"')])

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

        def test_pr_cmx_add(self):
            code = '''CMX 32 11 7
PR 11
ADD 1 2.2
'''
            assert_lex_token_list(code, [
                lit('CMX'),
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

        def test_unclosed_file_name(self):
            stream = lex('"')
            with raises(LexingError):
                next(stream)

        def test_empty_file_name(self):
            stream = lex('""')
            with raises(LexingError):
                next(stream)
