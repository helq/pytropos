from numpy import *
from numpy.random import *
gumbel(loc=0.0,scale=1.0,size=(2,3)) # Gumbel distribution location=0.0, scale=1.0
# array([[-1.25923601, 1.68758144, 1.76620507],
#        [ 1.96820048, -0.21219499, 1.83579566]])
from pylab import * # histogram plot example
hist(gumbel(0,1,(1000)), 50)

