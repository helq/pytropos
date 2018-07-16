from numpy import *
a = arange(60.).reshape(3,4,5)
b = arange(24.).reshape(4,3,2)
c = tensordot(a,b, axes=([1,0],[0,1])) # sum over the 1st and 2nd dimensions
c.shape
# (5,2)
# A slower but equivalent way of computing the same:
c = zeros((5,2))
for i in range(5):
    for j in range(2):
        for k in range(3):
            for n in range(4):
                c[i,j] += a[k,n,i] * b[n,k,j]
