from numpy import *
from numpy.linalg import solve

# The system of equations we want to solve for (x0,x1,x2):
# 3 * x0 + 1 * x1 + 5 * x2 = 6
# 1 * x0 + 8 * x2 = 7
# 2 * x0 + 1 * x1 + 4 * x2 = 8

a = array([[3,1,5],[1,0,8],[2,1,4]])
b = array([6,7,8])
x = solve(a,b)
print(x) # This is our solution
# [-3.28571429 9.42857143 1.28571429]

dot(a,x) # Just checking if we indeed obtain the righthand side
# array([ 6., 7., 8.])

