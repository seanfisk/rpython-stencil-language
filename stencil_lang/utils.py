""":mod:`stencil_lang.utils` -- Various utility functions
"""


def rjust(text, width):
    """Right-justify a string. Provided because RPython lacks
    :func:`str.rjust`.

    :param text: string to justify
    :type text: :class:`str`
    :param width: width to justify
    :type width: :class:`int`
    """
    return max(width - len(text), 0) * ' ' + text


def ljust(text, width):
    """Left-justify a string. Provided because RPython lacks
    :func:`str.ljust`.

    :param text: string to justify
    :type text: :class:`str`
    :param width: width to justify
    :type width: :class:`int`
    """
    return text + max(width - len(text), 0) * ' '
