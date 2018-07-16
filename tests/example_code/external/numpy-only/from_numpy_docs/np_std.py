from numpy import *
a = array([1.,2,7])
a.std() # normalized by N (not N-1)
# 2.6246692913372702
a = array([[1.,2,7],[4,9,6]])
a.std()
# 2.793842435706702
a.std(axis=0) # standard deviation of each of the 3 columns
# array([ 1.5, 3.5, 0.5])
a.std(axis=1) # standard deviation of each of the 2 columns
# array([ 2.62466929, 2.05480467])

