from numpy import *
a = arange(3*4*5).reshape(3,4,5)
a.shape
# (3, 4, 5)
b = rollaxis(a,1,0) # transpose array so that axis 1 is 'rolled' before axis 0
b.shape
# (4, 3, 5)
b = rollaxis(a,0,2) # transpose array so that axis 0 is 'rolled' before axis 2
b.shape
# (4, 3, 5)

