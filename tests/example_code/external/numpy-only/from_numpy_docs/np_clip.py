from numpy import *
a = array([5,15,25,3,13])
a.clip(min=10,max=20)
# array([10, 15, 20, 10, 13])
clip(a,10,20) # this syntax also exists

