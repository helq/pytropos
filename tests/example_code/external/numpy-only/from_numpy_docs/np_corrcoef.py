from numpy import *
T = array([1.3, 4.5, 2.8, 3.9]) # temperature measurements
P = array([2.7, 8.7, 4.7, 8.2]) # corresponding pressure measurements
print((corrcoef([T,P]))) # correlation matrix of temperature and pressure
# [[ 1. 0.98062258]
#  [ 0.98062258 1. ]]
rho = array([8.5, 5.2, 6.9, 6.5]) # corresponding density measurements
data = column_stack([T,P,rho])
print((corrcoef([T,P,rho]))) # correlation matrix of T,P and rho
# [[ 1. 0.98062258 -0.97090288]
#  [ 0.98062258 1. -0.91538464]
#  [-0.97090288 -0.91538464 1. ]]

