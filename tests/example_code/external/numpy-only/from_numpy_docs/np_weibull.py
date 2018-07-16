from numpy import *
from numpy.random import *
weibull(a=1,size=(2,3)) # I think a is the shape parameter
# array([[ 0.08303065, 3.41486412, 0.67430149],
#        [ 0.41383893, 0.93577601, 0.45431195]])
from pylab import * # histogram plot example
hist(weibull(5, (1000)), 50)

