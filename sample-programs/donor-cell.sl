CMX 0 3 3
SMXF 0 "sample-programs/matrices/stencil"
CMX 1 3 3
SMXF 1 "sample-programs/matrices/psi"

STO 0 0
ADD 0 1
PDE 0 1
BNE 0 12 -2
PMX 1