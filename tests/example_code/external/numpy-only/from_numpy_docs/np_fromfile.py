from numpy import *
y = array([2.,4.,6.,8.])
y.tofile("myfile.dat") # binary format
y.tofile("myfile.txt", sep='\n', format = "%e") # ascii format, one column, exponential notation
fromfile('myfile.dat', dtype=float)
# array([ 2., 4., 6., 8.])
fromfile('myfile.txt', dtype=float, sep='\n')
# array([ 2., 4., 6., 8.])

