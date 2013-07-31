#!/usr/bin/env python
""":mod:`stencil_lang.main` -- Program entry point
"""

import sys

from rpython.rlib.streamio import open_file_as_stream, fdopen_as_stream

from stencil_lang import metadata
from stencil_lang.interpreter import run
from stencil_lang.errors import StencilLanguageError


def usage(argv):
    """Print program usage information.

    :param argv: command-line arguments
    :type argv: :class:`list`
    :return: the usage string
    :rtype: :class:`str`
    """
    return '''usage: %s [INPUT_FILENAME]

    INPUT_FILENAME
        stencil language source file, omit or pass '-' to read from stdin
''' % argv[0]


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

    num_argv = len(argv)
    if num_argv > 2:
        print usage(argv)
        return 1

    if num_argv == 1 or (num_argv == 2 and argv[1] == '-'):
        input_stream = fdopen_as_stream(0, 'r')
    else:
        input_stream = open_file_as_stream(argv[1])

    try:
        source_code = input_stream.readall()
    finally:
        input_stream.close()
    try:
        run(source_code)
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
    """Main for use with setuptools/distribute.

    NOT_RPYTHON
    """
    raise SystemExit(_main(sys.argv))


def target(*args):
    """Target function for use with RPython."""
    return _main, None


def jitpolicy(driver):
    """Just-in-time compilation policy for RPython.

    :param driver: jit driver
    :type driver: :class:`pypy.rlib.jit.JitDriver`
    :return: jit policy
    :rtype: :class:`pypy.jit.codewriter.policy.JitPolicy`
    """
    from rpython.jit.codewriter.policy import JitPolicy

    return JitPolicy()


if __name__ == '__main__':
    main()
