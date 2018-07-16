from numpy import *
x = array([pi, 1.e-200])
x
# array([ 3.14159265e+000, 1.00000000e-200])
set_printoptions(precision=3, suppress=True) # 3 digits behind decimal point + suppress small values
x
# array([ 3.142, 0. ])

help(set_printoptions) # see help() for keywords 'threshold','edgeitems' and 'linewidth'

