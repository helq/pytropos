from numpy import *
a = array([5,15,25])
a.ptp() # peak-to-peak = maximum - minimum
# 20
a = array([[5,15,25],[3,13,33]])
a.ptp()
# 30
a.ptp(axis=0) # peak-to-peak value for each of the 3 columns
# array([2, 2, 8])
a.ptp(axis=1) # peak-to-peak value for each of the 2 rows
# array([20, 30])

