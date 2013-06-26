""":mod:`stencil_lang.interpreter.evaluator` -- Bytecode evaluator
"""


def eval_(bytecodes, context):
    """Evaluate a list of bytecodes within a context.

    :param bytecodes: bytecodes to evaluate
    :type bytecodes: :class:`stencil_lang.structures.BytecodeListBox`
    :param context: the execution context
    :type context: :class:`stencil_lang.structures.Context`
    """
    for i in xrange(len(bytecodes)):
        bytecodes[i].eval(context)
