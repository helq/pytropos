from numpy import *
x = array([0.2, 6.4, 3.0, 1.6])
bins = array([0.0, 1.0, 2.5, 4.0, 10.0]) # monotonically increasing
d = digitize(x,bins) # in which bin falls each value of x?
d
# array([1, 4, 3, 2])
for n in range(len(x)):
    print((bins[d[n]-1], "<=", x[n], "<", bins[d[n]]))
# ...
# 0.0 <= 0.2 < 1.0
# 4.0 <= 6.4 < 10.0
# 2.5 <= 3.0 < 4.0
# 1.0 <= 1.6 < 2.5

