import sys

from pytest import raises
from rply import Token

from stencil_lang.interpreter.parser import parse
from stencil_lang.interpreter.bytecodes import *  # NOQA
from stencil_lang.errors import ParseError

from tests.helpers import lit, assert_exc_info_msg


def mkiter(token_tuple_list):
    return iter(Token(name, value) for name, value in token_tuple_list)


class TestParser(object):
    class TestSto(object):
        def test_pos_int(self):
            assert parse(mkiter([
                lit('STO'),
                ('POS_INT', '10'),
                ('POS_INT', '32'),
            ])) == [
                Sto(10, 32),
            ]

        def test_neg_int(self):
            assert parse(mkiter([
                lit('STO'),
                ('POS_INT', '10'),
                ('NEG_INT', '-88'),
            ])) == [
                Sto(10, -88),
            ]

        def test_sto_neg_index(self):
            with raises(ParseError) as exc_info:
                parse(mkiter([
                    lit('STO'),
                    # STO should only take a POS_INT argument here.
                    ('NEG_INT', '-37'),
                    ('REAL', '42.4'),
                ]))
            assert_exc_info_msg(exc_info, "Unexpected `NEG_INT'")

        def test_end_of_one_line_program(self):
            with raises(ParseError) as exc_info:
                parse(mkiter([
                    lit('STO'),
                    ('POS_INT', '37'),
                    # STO is missing a REAL argument
                ]))
            assert_exc_info_msg(exc_info, "Unexpected `$end'")

        def test_large_integer(self):
            # This doesn't test RPython's capabilities, since it's not running
            # translated.
            int_str = '9%d' % sys.maxint
            assert parse(mkiter([
                lit('STO'),
                ('POS_INT', '31'),
                ('POS_INT', int_str),
            ])) == [
                Sto(31, int(int_str)),
            ]

        def test_small_integer(self):
            # This doesn't test RPython's capabilities, since it's not running
            # translated.
            int_str = '-9%d' % sys.maxint
            assert parse(mkiter([
                lit('STO'),
                ('POS_INT', '31'),
                ('POS_INT', int_str),
            ])) == [
                Sto(31, int(int_str)),
            ]

    class TestPr(object):
        def test_sto_pr(self, capsys):
            assert parse(mkiter([
                lit('STO'),
                ('POS_INT', '37'),
                ('NEG_INT', '-452'),
                lit('PR'),
                ('POS_INT', '37'),
            ])) == [
                Sto(37, -452),
                Pr(37),
            ]

        def test_missing_arg(self):
            with raises(ParseError) as exc_info:
                parse(mkiter([
                    lit('STO'),
                    ('POS_INT', '37'),
                    ('POS_INT', '45'),
                    lit('PR'),
                    # PR is missing a POS_INT argument
                    lit('PR'),
                    ('POS_INT', '37'),
                ]))
            assert_exc_info_msg(exc_info, "Unexpected `PR'")


class TestAdd(object):
    def test_sto_add(self):
        assert parse(mkiter([
            lit('STO'),
            ('POS_INT', '10'),
            ('NEG_INT', '-88'),
            lit('ADD'),
            ('POS_INT', '10'),
            ('POS_INT', '22'),
        ])) == [
            Sto(10, -88),
            Add(10, 22),
        ]


class TestCmx(object):
    def test_positive_matrix_index(self):
        assert parse(mkiter([
            lit('CMX'),
            ('POS_INT', '22'),
            ('POS_INT', '33'),
            ('POS_INT', '11'),
        ])) == [
            Cmx(22, 33, 11)
        ]

    def test_negative_matrix_index(self):
        with raises(ParseError) as exc_info:
            parse(mkiter([
                lit('CMX'),
                ('NEG_INT', '-22'),
                ('POS_INT', '20'),
                ('POS_INT', '20'),
            ]))
        assert_exc_info_msg(exc_info, "Unexpected `NEG_INT'")

    def test_neg_dimension(self):
        with raises(ParseError) as exc_info:
            parse(mkiter([
                lit('CMX'),
                ('POS_INT', '11'),
                ('POS_INT', '12'),
                ('NEG_INT', '-13'),
            ]))
        assert_exc_info_msg(exc_info, "Unexpected `NEG_INT'")


class TestPmx(object):
    def test_pmx(self, capsys):
            assert parse(mkiter([
                lit('CMX'),
                ('POS_INT', '40'),
                ('POS_INT', '22'),
                ('POS_INT', '78'),
                lit('PMX'),
                ('POS_INT', '40'),
            ])) == [
                Cmx(40, 22, 78),
                Pmx(40),
            ]


class TestSmx(object):
    def test_cmx_smx(self):
        parse(mkiter([
            lit('CMX'),
            ('POS_INT', '31'),
            ('POS_INT', '2'),
            ('POS_INT', '3'),
            lit('SMX'),
            ('POS_INT', '31'),
            # Contents
            ('REAL', '-13.4'),
            ('POS_INT', '9876'),
            ('REAL_SCI', '45.234e4'),
            ('POS_INT', '-42'),
            ('REAL', '34.8'),
            ('REAL_SCI', '-88.2e-2'),
        ])) == [
            Cmx(31, 2, 3),
            Smx(31, [-13.4, 9876, 45.234e4, -42, 34.8, -88.2e-2])
        ]


class TestSmxf(object):
    def test_cmx_smx(self):
        parse(mkiter([
            lit('CMX'),
            ('POS_INT', '31'),
            ('POS_INT', '3'),
            ('POS_INT', '3'),
            lit('SMXF'),
            ('POS_INT', '31'),
            ('FILENAME', '"a/random/file name"')
        ])) == [
            Cmx(31, 2, 3),
            Smxf(31, 'a/random/file name'),
        ]


class TestPde(object):
    def test_pde(self):
        parse(mkiter([
            lit('PDE'),
            ('POS_INT', '10'),
            ('POS_INT', '20'),
        ])) == [
            Pde(10, 20),
        ]


class TestBne(object):
    def test_bne_neg_offset(self):
        parse(mkiter([
            lit('BNE'),
            ('POS_INT', '1'),
            ('POS_INT', '72'),
            ('NEG_INT', '-10'),
        ])) == [
            Bne(1, 72, -10),
        ]

    def test_bne_pos_offset(self):
        parse(mkiter([
            lit('BNE'),
            ('POS_INT', '1'),
            ('POS_INT', '72'),
            ('POS_INT', '10'),
        ])) == [
            Bne(1, 72, 10),
        ]

    def test_bne_real_register_index(self):
        with raises(ParseError) as exc_info:
            parse(mkiter([
                lit('BNE'),
                ('REAL', '-21.2'),
                ('POS_INT', '81'),
                ('POS_INT', '32'),
            ]))
        assert_exc_info_msg(exc_info, "Unexpected `REAL'")

    def test_bne_real_register_value(self):
        with raises(ParseError) as exc_info:
            parse(mkiter([
                lit('BNE'),
                ('POS_INT', '81'),
                ('REAL', '-21.2'),
                ('POS_INT', '32'),
            ]))
        assert_exc_info_msg(exc_info, "Unexpected `REAL'")

    def test_bne_real_offset(self):
        with raises(ParseError) as exc_info:
            parse(mkiter([
                lit('BNE'),
                ('POS_INT', '81'),
                ('POS_INT', '32'),
                ('REAL', '-21.2'),
            ]))
        assert_exc_info_msg(exc_info, "Unexpected `REAL'")
