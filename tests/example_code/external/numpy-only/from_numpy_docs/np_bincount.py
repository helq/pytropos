from numpy import *
a = array([1,1,1,1,2,2,4,4,5,6,6,6]) # doesn't need to be sorted
bincount(a) # 0 occurs 0 times, 1 occurs 4 times, 2 occurs twice, 3 occurs 0 times, ...
# array([0, 4, 2, 0, 2, 1, 3])
a = array([5,4,4,2,2])
w = array([0.1, 0.2, 0.1, 0.3, 0.5])
bincount(a) # 0 & 1 don't occur, 2 occurs twice, 3 doesn't occur, 4 occurs twice, 5 once
# array([0, 0, 2, 0, 2, 1])
bincount(a, weights=w)
# array([ 0. , 0. , 0.8, 0. , 0.3, 0.1])
# 0 occurs 0 times -> result[0] = 0
# 1 occurs 0 times -> result[1] = 0
# 2 occurs at indices 3 & 4 -> result[2] = w[3] + w[4]
# 3 occurs 0 times -> result[3] = 0
# 4 occurs at indices 1 & 2 -> result[4] = w[1] + w[2]
# 5 occurs at index 0 -> result[5] = w[0]

