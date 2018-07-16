from numpy import *
logspace(-2, 3, num = 6) # 6 evenly spaced pts on a logarithmic scale, from 10^{-2} to 10^3 incl.
# array([ 1.00000000e-02, 1.00000000e-01, 1.00000000e+00,
#          1.00000000e+01, 1.00000000e+02, 1.00000000e+03])
logspace(-2, 3, num = 10) # 10 evenly spaced pts on a logarithmic scale, from 10^{-2} to 10^3 incl.
# array([ 1.00000000e-02, 3.59381366e-02, 1.29154967e-01,
#          4.64158883e-01, 1.66810054e+00, 5.99484250e+00,
#          2.15443469e+01, 7.74263683e+01, 2.78255940e+02,
#          1.00000000e+03])
logspace(-2, 3, num = 6, endpoint=False) # 6 evenly spaced pts on a logarithmic scale, from 10^{-2} to 10^3 EXCL.
# array([ 1.00000000e-02, 6.81292069e-02, 4.64158883e-01,
#          3.16227766e+00, 2.15443469e+01, 1.46779927e+02])
exp(linspace(log(0.01), log(1000), num=6, endpoint=False)) # for comparison
# array([ 1.00000000e-02, 6.81292069e-02, 4.64158883e-01,
#          3.16227766e+00, 2.15443469e+01, 1.46779927e+02])

