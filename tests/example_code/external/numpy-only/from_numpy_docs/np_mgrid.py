from numpy import *
m = mgrid[1:3,2:5] # rectangular mesh grid with x-values [1,2] and y-values [2,3,4]
print(m)
# [[[1 1 1]
#   [2 2 2]]
#  [[2 3 4]
#   [2 3 4]]]
m[0,1,2] # x-value of grid point with index coordinates (1,2)
# 2
m[1,1,2] # y-value of grid point with index coordinates (1,2)
# 4

