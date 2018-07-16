from numpy import *
from numpy.random import *
vonmises(mu=1,kappa=1,size=(2,3)) # Von Mises distribution mean=1.0, kappa=1
# array([[ 0.81960554, 1.37470839, -0.15700173],
#        [ 1.2974554 , 2.94229797, 0.32462307]])
from pylab import * # histogram plot example
hist(vonmises(1,1,(10000)), 50)

