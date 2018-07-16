from numpy import *
a = array([10, 20, 30, 40])
condition = (a > 15) & (a < 35)
condition
# array([False, True, True, False], dtype=bool)
a.compress(condition)
# array([20, 30])
a[condition] # same effect
# array([20, 30])
compress(a >= 30, a) # this form also exists
# array([30, 40])
b = array([[10,20,30],[40,50,60]])
b.compress(b.ravel() >= 22)
# array([30, 40, 50, 60])
x = array([3,1,2])
y = array([50, 101])
b.compress(x >= 2, axis=1) # illustrates the use of the axis keyword
# array([[10, 30],
#        [40, 60]])
b.compress(y >= 100, axis=0)
# array([[40, 50, 60]])

