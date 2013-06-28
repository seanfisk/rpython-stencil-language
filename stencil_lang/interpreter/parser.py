""":mod:`stencil_lang.interpreter.parser` --- Parsing-related classes
"""
from rply import ParserGenerator

from stencil_lang.interpreter.tokens import TOKENS
from stencil_lang.interpreter.bytecodes import *  # NOQA
from stencil_lang.structures import (
    IntBox,
    FloatBox,
    FloatListBox,
    BytecodeListBox,
)
from stencil_lang.errors import ParseError


class Parser(object):
    """Source code parser and intepreter."""
    _pg = ParserGenerator(TOKENS.keys(), cache_id=__name__)

    # Don't get taken in by illusions of any kind. For this class to translate,
    # all productions must return boxed values of some kind. If you try to
    # return raw values, translation will blow up.

    @_pg.production('main : stmt_list')
    def _main(self, p):
        return p[0]

    @_pg.production('stmt_list : stmt_list stmt')
    # A valid program can be just one statement.
    @_pg.production('stmt_list : stmt')
    def _stmt_list(self, p):
        if len(p) == 2:
            # stmt_list : stmt_list stmt
            stmt_list_box = p[0]
            stmt_bytecode_box = p[1]
            # TODO: Might have a problem with this mutating the list in the
            # future.
            stmt_list_box.get_bytecode_list().append(stmt_bytecode_box)
        else:
            # stmt_list : stmt
            stmt = p[0]
            stmt_list_box = BytecodeListBox([stmt])
        return stmt_list_box

    @_pg.production('stmt : sto')
    @_pg.production('stmt : pr')
    @_pg.production('stmt : add')
    @_pg.production('stmt : cmx')
    @_pg.production('stmt : pmx')
    @_pg.production('stmt : smx')
    @_pg.production('stmt : pde')
    @_pg.production('stmt : bne')
    def _stmt(self, p):
        return p[0]

    @_pg.production('sto : STO index int')
    def _sto(self, p):
        index = p[1].get_int()
        integer = p[2].get_int()
        return Sto(index, integer)

    @_pg.production('pr : PR index')
    def _pr(self, p):
        index = p[1].get_int()
        return Pr(index)

    @_pg.production('add : ADD index int')
    def _add(self, p):
        index = p[1].get_int()
        integer = p[2].get_int()
        return Add(index, integer)

    @_pg.production('cmx : CMX index nonneg_int nonneg_int')
    def _cmx(self, p):
        index = p[1].get_int()
        rows = p[2].get_int()
        cols = p[3].get_int()
        return Cmx(index, rows, cols)

    @_pg.production('pmx : PMX index')
    def _pmx(self, p):
        index = p[1].get_int()
        return Pmx(index)

    @_pg.production('smx : SMX index real_list')
    def _smx(self, p):
        index = p[1].get_int()
        real_list = p[2].get_float_list()
        return Smx(index, real_list)

    @_pg.production('pde : PDE index index')
    def _pde(self, p):
        stencil_index = p[1].get_int()
        matrix_index = p[2].get_int()
        return Pde(stencil_index, matrix_index)

    @_pg.production('bne : BNE index int int')
    def _bne(self, p):
        register_index = p[1].get_int()
        value = p[2].get_int()
        offset = p[3].get_int()
        return Bne(register_index, value, offset)

    # real_list must come first to parse the first real s first.
    @_pg.production('real_list : real_list real')
    @_pg.production('real_list : real')
    def _real_list(self, p):
        if len(p) == 2:
            # real_list : real_list real
            real_list_box = p[0]
            real = p[1].get_float()
            # TODO: Might have a problem with this mutating the list in the
            # future.

            # RPython likes this assigned to a variable before appending.
            real_list = real_list_box.get_float_list()
            real_list.append(real)
            return real_list_box
        # RPython likes two separate return statements.

        # real_list : real
        real = p[0].get_float()
        real_list_box = FloatListBox([real])
        return real_list_box

    @_pg.production('real : POS_INT')
    @_pg.production('real : NEG_INT')
    @_pg.production('real : REAL')
    def _real(self, p):
        # Convert integers and reals to float representation.
        return FloatBox(float(p[0].getstr()))

    @_pg.production('int : POS_INT')
    @_pg.production('int : NEG_INT')
    @_pg.production('index : POS_INT')
    @_pg.production('nonneg_int : POS_INT')
    def _int(self, p):
        return IntBox(int(p[0].getstr()))

    @_pg.error
    def _error_handler(self, token):
        # NOTE: SourcePosition is a class, but it's not actually implemented :(
        raise ParseError(token.gettokentype())

    # This has to be called outside a function because the parser must be
    # generated in Python during translation, not in RPython during runtime.
    _parser = _pg.build()

    def parse(self, text):
        """Parse and interpret using the generated parser.

        :param text: text to parse
        :type text: :class:`str`
        :return: the parsed bytecodes
        :rtype: :class:`list` of :class:`stencil_lang.structures.Bytecode`
        """
        # _parser.parse returns a boxed list of bytecodes.
        return self._parser.parse(text, state=self).get_bytecode_list()


def parse(text):
    """Parse and interpret text using the generated parser.

    :param text: text to parse
    :type text: :class:`str`
    :return: the parsed bytecodes
    :rtype: :class:`list` of :class:`stencil_lang.structures.Bytecode`
    """
    return Parser().parse(text)
