from numpy import *
x = arange(10.)
y = x**2
y.tofile("myfile.dat") # binary format
y.tofile("myfile.txt", sep=' ', format = "%e") # ascii format, one row, exp notation, values separated by 1 space
y.tofile("myfile.txt", sep='\n', format = "%e") # ascii format, one column, exponential notation

