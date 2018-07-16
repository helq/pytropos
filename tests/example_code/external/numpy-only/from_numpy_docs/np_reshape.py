from numpy import *
x = arange(12)
x.reshape(3,4) # array with 3 rows and 4 columns. 3x4=12. Total number of elements is always the same.
# array([[ 0, 1, 2, 3],
#        [ 4, 5, 6, 7],
#        [ 8, 9, 10, 11]])
x.reshape(3,2,2) # 3x2x2 array; 3x2x2 = 12. x itself does _not_ change.
# array([[[ 0, 1],
#         [ 2, 3]],
#        [[ 4, 5],
#         [ 6, 7]],
#        [[ 8, 9],
#         [10, 11]]])
x.reshape(2,-1) # 'missing' -1 value n is calculated so that 2xn=12, so n=6
# array([[ 0, 1, 2, 3, 4, 5],
#        [ 6, 7, 8, 9, 10, 11]])
x.reshape(12) # reshape(1,12) is not the same as reshape(12)
# array([0,1,2,3,4,5,6,7,8,9,10,11])
reshape(x,(2,6)) # Separate function reshape() also exists

