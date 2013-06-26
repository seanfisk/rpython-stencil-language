""":mod:`stencil_lang.interpreter.evaluator` -- Bytecode evaluator
"""

from rpython.rlib.jit import JitDriver
jit_driver = JitDriver(greens=['bytecodes'], reds=['context'])


def eval_(bytecodes, context):
    """Evaluate a list of bytecodes within a context.

    :param bytecodes: bytecodes to evaluate
    :type bytecodes: :class:`stencil_lang.structures.BytecodeListBox`
    :param context: the execution context
    :type context: :class:`stencil_lang.structures.Context`
    """
    context.program_length = len(bytecodes)
    while context.pc < len(bytecodes):
        jit_driver.jit_merge_point(
            bytecodes=bytecodes,
            context=context,
        )
        bytecodes[context.pc].eval(context)

        context.pc += 1
