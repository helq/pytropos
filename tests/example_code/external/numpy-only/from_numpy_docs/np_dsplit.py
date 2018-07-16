from numpy import *
a = array([[1,2],[3,4]])
b = dstack((a,a,a,a))
b.shape # stacking in depth: for k in (0,..,3): b[:,:,k] = a
# (2, 2, 4)
c = dsplit(b,2) # split, depth-wise, in 2 equal parts
print((c[0].shape, c[1].shape)) # for k in (0,1): c[0][:,:,k] = a and c[1][:,:,k] = a
# (2, 2, 2) (2, 2, 2)
d = dsplit(b,[1,2]) # split before [:,:,1] and before [:,:,2]
print((d[0].shape, d[1].shape, d[2].shape)) # for any of the parts: d[.][:,:,k] = a
# (2, 2, 1) (2, 2, 1) (2, 2, 2)

