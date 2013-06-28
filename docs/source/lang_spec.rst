========================
 Language Specification
========================

Variables
=========


R\ :sub:`x`
    Register with `x` from 0 to `maxint`. Registers store integers.
M\ :sub:`x`
    Matrix of data with `x` from 0 to `maxint`. Matrices store real numbers (as floats). Matrices must have odd dimensions.

Opcodes
=======

STO R\ :sub:`x` V
    Store value `V` in register R\ :sub:`x`
ADD R\ :sub:`x` V
    Add value `V` to register R\ :sub:`x`
PR R\ :sub:`x`
    Print value in register R\ :sub:`x`
CMX M\ :sub:`x` A B
    Create matrix M\ :sub:`x` with dimensions (`A`, `B`)
SMX M\ :sub:`x` ...
    Set the values of M\ :sub:`x`, it requires `A` * `B` arguments
PMX M\ :sub:`x`
    Print matrix M\ :sub:`x`
PDE M\ :sub:`x` M\ :sub:`y`
    Apply stencil M\ :sub:`x` to M\ :sub:`y` and store the result in M\ :sub:`x`
BNE R\ :sub:`x` V L
    Branch to relative location `L` if R\ :sub:`x` != `V`

Example
=======

In this example the stencil is implemented as general purpose matrix, but it could be dedicated matrix-like data structure.

A PDE solver program with this stencil language would look like:

.. If we just say it's bash, it will highlight the hashes as comments.
.. code-block:: bash

    CMX 1 100 200            # create a 100, 200 domain
    SMX 1 <20000 values>     # set the initial condition
    CMX 2 3 3                # create a 3,3 matrix (stencil)
    SMX 2 0 1 0 1 -2 1 0 1 0 # set the stencil values
    STO 1 10                 # iterate for 10 timesteps
    PDE 2 1                  # do one time step (20000 spatial locations)
    ADD 1 -1                 # one time step is done
    BNE 1 0 -1               # goto PDE, unless 10 timesteps are done
    PMX 1                    # print the final matrix
