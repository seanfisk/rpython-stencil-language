""":mod:`stencil_lang.interpreter.stencil` -- Stencil application
"""

from stencil_lang.structures import Matrix


def _make_halo(matrix, num_row_layers, num_col_layers):
    """Make a halo matrix out of the given matrix.

    :param matrix: matrix to which to add the halo
    :type matrix: :class:`stencil_lang.structures.Matrix`
    :param num_row_layers: number of border rows to add
    :type num_row_layers: :class:`int`
    :param num_col_layers: number of border columns to add
    :type num_col_layers: :class:`int`
    :return: the halo matrix (which includes the original)
    :rtype: :class:`stencil_lang.structures.Matrix`
    """
    halo = Matrix(matrix.rows + 2 * num_row_layers,
                  matrix.cols + 2 * num_col_layers,
                  [])
    for r in xrange(-num_row_layers, matrix.rows + num_row_layers):
        for c in xrange(-num_col_layers, matrix.cols + num_col_layers):
            halo.contents.append(matrix.__getitem__((r, c)))
    return halo


def apply_stencil(stencil, matrix):
    """Apply the stencil to the matrix.

    :param stencil: stencil to apply
    :type stencil: :class:`stencil_lang.structures.Matrix`
    :param matrix: matrix to which to apply the stencil
    :type matrix: :class:`stencil_lang.structures.Matrix`
    :return: the generated matrix
    :rtype: :class:`stencil_lang.structures.Matrix`
    """
    num_row_layers = (stencil.rows - 1) / 2
    num_col_layers = (stencil.cols - 1) / 2
    halo = _make_halo(matrix, num_row_layers, num_col_layers)
    new_matrix = Matrix(matrix.rows, matrix.cols, [])
    for r in xrange(matrix.rows):
        for c in xrange(matrix.cols):
            new_value = halo[r + num_row_layers, c + num_col_layers]
            for st_r in xrange(stencil.rows):
                for st_c in xrange(stencil.cols):
                    new_value += stencil[st_r, st_c] * halo[r + st_r, c + st_c]
            new_matrix.contents.append(new_value)
    return new_matrix
