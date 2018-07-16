from numpy import *
x = array([5., -2., 1., 0., 4., -1., 3., 10.])
select([x < 0, x == 0, x <= 5], [x-0.1, 0.0, x+0.2], default = 100.)
# array([ 5.2, -2.1, 1.2, 0. , 4.2, -1.1, 3.2, 100. ])

# This is how it works:

result = zeros_like(x)
for n in range(len(x)):
    if x[n] < 0: result[n] = x[n]-0.1 # The order of the conditions matters. The first one that
    elif x[n] == 0: result[n] = 0.0 # matches, will be 'selected'.
    elif x[n] <= 5: result[n] = x[n]+0.2
    else: result[n] = 100. # The default is used when none of the conditions match
# ...
result
# array([ 5.2, -2.1, 1.2, 0. , 4.2, -1.1, 3.2, 100. ])

