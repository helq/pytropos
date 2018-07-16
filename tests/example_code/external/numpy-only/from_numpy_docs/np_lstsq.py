from numpy import *
from numpy.random import normal
t = arange(0.0, 10.0, 0.05) # independent variable
y = 2.0 * sin(2.*pi*t*0.6) + 2.7 * cos(2.*pi*t*0.6) + normal(0.0, 1.0, len(t))

from numpy.linalg import lstsq
Nparam = 2 # we want to estimate 2 parameters: p_0 and p_1
A = zeros((len(t),Nparam), float) # one big array with all the f_i(t)
A[:,0] = sin(2.*pi*t*0.6) # f_0(t) stored
A[:,1] = cos(2.*pi*t*0.6) # f_1(t) stored
(p, residuals, rank, s) = lstsq(A,y)
p # our final estimate of the parameters using noisy data
# array([ 1.9315685 , 2.71165171])
residuals # sum of the residuals: sum((p[0] * A[:,0] + p[1] * A[:,1] - y)**2)
# array([ 217.23783374])
rank # rank of the array A
# 2
s # singular values of A
# array([ 10., 10.])

