from numpy import *
x = array([[1,2,3],[4,5,6]])
x.shape
# (2, 3)
y = array([[1,2],[3,4],[5,6]])
y.shape
# (3, 2)
dot(x,y) # matrix multiplication (2,3) x (3,2) -> (2,2)
# array([[22, 28],
#        [49, 64]])

import numpy
if id(dot) == id(numpy.core.multiarray.dot): # A way to know if you use fast blas/lapack or not.
    print("Not using blas/lapack!")

