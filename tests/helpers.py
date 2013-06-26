import os.path

from stencil_lang.matrix import from_file


def lit(name):
    """Make a literal token tuple."""
    return (name, name)


def assert_exc_info_msg(exc_info, expected_msg):
    # LHS and RHS intentionally placed so diffs look correct.
    assert expected_msg == str(exc_info.value)


def fixture_path(rel_path):
    """Return the correct path to a fixture file.

    :param rel_path: relative path from the fixtures directory.
    :type rel_path: :class:`str`
    :return: path relative to the project root
    :rtype: :class:`str`
    """
    return os.path.join(os.path.dirname(__file__), 'fixtures', rel_path)


def open_matrix(matrix_type, matrix_name):
    """Read a matrix from the fixtures directory.

    :param matrix_type: stencil, before, or after
    :type matrix_type: :class:`str`
    :param matrix_name: name of the matrix file
    :type matrix_name: :class:`str`
    :return: the created matrix
    :rtype: :class:`stencil_lang.structures.Matrix`
    """
    return from_file(fixture_path(os.path.join(matrix_type, matrix_name)))
