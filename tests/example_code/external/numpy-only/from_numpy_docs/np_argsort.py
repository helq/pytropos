from numpy import *
a = array([2,0,8,4,1])
ind = a.argsort() # indices of sorted array using quicksort (default)
ind
# array([1, 4, 0, 3, 2])
a[ind] # same effect as a.sort()
# array([0, 1, 2, 4, 8])
ind = a.argsort(kind='merge') # algorithm options are 'quicksort', 'mergesort' and 'heapsort'
a = array([[8,4,1],[2,0,9]])
ind = a.argsort(axis=0) # sorts on columns. NOT the same as a.sort(axis=1)
ind
# array([[1, 1, 0],
#        [0, 0, 1]])
a[ind,[[0,1,2],[0,1,2]]] # 2-D arrays need fancy indexing if you want to sort them.
# array([[2, 0, 1],
#        [8, 4, 9]])
ind = a.argsort(axis=1) # sort along rows. Can use a.argsort(axis=-1) for last axis.
ind
# array([[2, 1, 0],
#        [1, 0, 2]])
a = ones(17)
a.argsort() # quicksort doesn't preserve original order.
# array([ 0, 14, 13, 12, 11, 10, 9, 15, 8, 6, 5, 4, 3, 2, 1, 7, 16])
a.argsort(kind="mergesort") # mergesort preserves order when possible. It is a stable sort.
# array([ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
ind = argsort(a) # there is a functional form

