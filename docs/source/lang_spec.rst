========================
 Language Specification
========================

Variables
=========


R\ :sub:`x`
    Register with `x` from 0 to `maxint`
A\ :sub:`x`
    2D array of data with `x` from 0 to `maxint`

Opcodes
=======

STO R\ :sub:`x` V
    Store value `V` in register R\ :sub:`x`
ADD R\ :sub:`x` V
    Add value `V` in register R\ :sub:`x`
BNE R\ :sub:`x` V L
    Branch to relative location `L` if register R\ :sub:`x` != `V`
CAR A\ :sub:`x` A B
    Create the array A\ :sub:`x` with dimensions set to (`A`, `B`)
SAR A\ :sub:`x` ...
    Set the values of A\ :sub:`x`, it requires `A` * `B` arguments
PDE A\ :sub:`x` A\ :sub:`y`
    Apply stencil A\ :sub:`x` to array A\ :sub:`x` (swap A\ :sub:`x` with copy when done)
PR R\ :sub:`x`
    Print register R\ :sub:`x`
PA A\ :sub:`x`
    Print array A\ :sub:`x`

Example
=======

In this example the stencil is implemented as general purpose array, but it could be dedicated array-like data structure.

A PDE solver program with this stencil language would look like:

.. If we just say it's bash, it will highlight the hashes as comments.
.. code-block:: bash

    CAR 1 100 200            # create a 100, 200 domain
    SAR 1 <20000 values>     # set the initial condition
    CAR 2 3 3                # create a 3,3 array (stencil)
    SAR 2 0 1 0 1 -2 1 0 1 0 # set the stencil values
    STO 1 10                 # iterate for 10 timesteps
    PDE 2 1                  # do one time step (20000 spatial locations)
    ADD 1 -1                 # one time step is done
    BNE 1 0 -1               # goto PDE, unless 10 timesteps are done
    PA 1                     # print the final array
