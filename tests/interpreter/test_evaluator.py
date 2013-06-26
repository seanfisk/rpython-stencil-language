from mock import create_autospec, sentinel

from stencil_lang.structures import Bytecode
from stencil_lang.interpreter.evaluator import eval_


def test_evaluator():
    # [...] * 10 would create a list of the same instance; that is not what we
    # want.
    bytecodes = [create_autospec(Bytecode, spec_set=True) for _ in xrange(10)]
    eval_(bytecodes, sentinel.context)
    for bytecode in bytecodes:
        bytecode.eval.assert_called_once_with(sentinel.context)
