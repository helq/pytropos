from numpy import *
linspace(0,5,num=6) # 6 evenly spaced numbers between 0 and 5 incl.
# array([ 0., 1., 2., 3., 4., 5.])
linspace(0,5,num=10) # 10 evenly spaced numbers between 0 and 5 incl.
# array([ 0. , 0.55555556, 1.11111111, 1.66666667, 2.22222222,
#         2.77777778, 3.33333333, 3.88888889, 4.44444444, 5. ])
linspace(0,5,num=10,endpoint=False) # 10 evenly spaced numbers between 0 and 5 EXCL.
# array([ 0. , 0.5, 1. , 1.5, 2. , 2.5, 3. , 3.5, 4. , 4.5])
stepsize = linspace(0,5,num=10,endpoint=False,retstep=True) # besides the usual array, also return the step size
stepsize
# (array([ 0. , 0.5, 1. , 1.5, 2. , 2.5, 3. , 3.5, 4. , 4.5]), 0.5)
myarray, stepsize = linspace(0,5,num=10,endpoint=False,retstep=True)
stepsize
# 0.5

