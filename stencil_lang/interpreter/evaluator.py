""":mod:`stencil_lang.interpreter.evaluator` -- Bytecode evaluator
"""

from rpython.rlib.jit import JitDriver
jit_driver = JitDriver(greens=['pc', 'bytecodes'], reds=['context'])


def eval_(bytecodes, context):
    """Evaluate a list of bytecodes within a context.

    :param bytecodes: bytecodes to evaluate
    :type bytecodes: :class:`stencil_lang.structures.BytecodeListBox`
    :param context: the execution context
    :type context: :class:`stencil_lang.structures.Context`
    """
    # JIT doesn't like a for-loop based approach, so use a while loop instead.
    pc = 0
    while pc < len(bytecodes):
        jit_driver.jit_merge_point(
            pc=pc,
            bytecodes=bytecodes,
            context=context,
        )
        bytecodes[pc].eval(context)

        pc += 1
