from mock import create_autospec, sentinel, MagicMock
from pytest import fixture

from stencil_lang.structures import Bytecode, Context
from stencil_lang.interpreter.evaluator import eval_


@fixture
def context():
    return Context(sentinel.apply_stencil)


class TestEvaluator(object):
    def test_calls_eval(self, context):
        # [...] * 10 would create a list of the same instance; that is not what
        # we want.

        # Just test a simple serial program without branches. Branches are
        # tested more in `test_bytecodes.py'.
        bytecodes = [
            create_autospec(Bytecode, spec_set=True) for _ in xrange(10)]
        eval_(bytecodes, context)
        for bytecode in bytecodes:
            bytecode.eval.assert_called_once_with(context)

    def test_sets_program_length(self, context):
        bytecodes = [MagicMock()] * 10
        eval_(bytecodes, context)
        assert context.program_length == 10
