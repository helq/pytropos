from numpy import *
x = array([1,2,3,4,5])
y = array([6, 11, 18, 27, 38])
polyfit(x,y,2) # fit a 2nd degree polynomial to the data, result is x**2 + 2x + 3
# array([ 1., 2., 3.])
polyfit(x,y,1) # fit a 1st degree polynomial (straight line), result is 8x-4
# array([ 8., -4.])

