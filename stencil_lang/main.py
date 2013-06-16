#!/usr/bin/env python
""":mod:`stencil_lang.main` -- Program entry point
"""

import os
import sys

from stencil_lang import metadata
from stencil_lang.lexer import lex
from stencil_lang.parser import parse, Context
from stencil_lang.errors import StencilLanguageError


def usage(argv):
    """Print program usage information.

    :param argv: command-line arguments
    :type argv: :class:`list`
    :return: the usage string
    :rtype: :class:`str`
    """
    return 'usage: %s INPUT_FILENAME' % argv[0]


def _main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    :return: exit code
    :rtype: :class:`int`
    """
    author_strings = []
    for i in xrange(len(metadata.authors)):
        author_strings.append(
            'Author: %s <%s>' % (metadata.authors[i], metadata.emails[i]))

    # We can't use argparse, so we do some old-school argument parsing.
    if '-h' in argv or '--help' in argv:
        print usage(argv)
        # RPython doesn't support named specifiers.
        print '''
%s %s

%s
URL: <%s>
''' % (metadata.project, metadata.version,
       '\n'.join(author_strings), metadata.url)
        return 0

    if '-V' in argv or '--version' in argv:
        print '%s %s' % (metadata.project, metadata.version)
        return 0

    if len(argv) != 2:
        print usage(argv)
        return 1

    input_filename = argv[1]

    input_fp = os.open(input_filename, os.O_RDONLY, 0777)

    source_code_list = []
    while True:
        read = os.read(input_fp, 4096)
        if len(read) == 0:
            break
        source_code_list.append(read)
    os.close(input_fp)

    source_code = ''.join(source_code_list)
    stream = lex(source_code)
    default_context = Context()
    try:
        parse(stream, default_context)
    except StencilLanguageError as error:
        # The purpose of this except block is two-fold:
        #
        # * Don't print tracebacks for interpreter errors. Tracebacks shouldn't
        #   be shown to the user.
        # * RPython doesn't honor most magic methods including __str__ and
        #   __repr__, so error messages aren't shown to the user when using the
        #   translated executable. Only the exception name is shown.

        # TODO: This should print to stderr.
        print '%s: %s' % (error.name, error.__str__())

    return 0


def main():
    """Main for use with setuptools/distribute."""
    raise SystemExit(_main(sys.argv))


def target(*args):
    """Target function for use with RPython."""
    return _main, None


def jitpolicy(driver):
    """Define a JIT policy for PyPy.

    :param driver: jit driver
    :type driver: :class:`pypy.rlib.jit.JitDriver`
    :return: jit policy
    :rtype: :class:`pypy.jit.codewriter.policy.JitPolicy`
    """
    try:
        # PyPy >= 2.0-beta2
        from rpython.jit.codewriter.policy import JitPolicy
    except ImportError:
        # PyPy <= 2.0-beta1
        from pypy.jit.codewriter.policy import JitPolicy

    return JitPolicy()


if __name__ == '__main__':
    main()
