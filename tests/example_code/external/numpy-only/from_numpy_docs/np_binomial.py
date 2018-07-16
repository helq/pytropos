from numpy import *
from numpy.random import *
binomial(n=100,p=0.5,size=(2,3)) # binomial distribution n trials, p= success probability
# array([[38, 50, 53],
#        [56, 48, 54]])
from pylab import * # histogram plot example
hist(binomial(100,0.5,(1000)), 20)

