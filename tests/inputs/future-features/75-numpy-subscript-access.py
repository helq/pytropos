import numpy as np

a = [[2,3,4],
     [1,4,6],
     [1,4,6],
     [1,4,6],
     [1,4,6]]

a.append((3, 4, 5))

a = np.array([a, a])  # .reshape(1, 2, 6, 3)
b = a[0,0,0]  # A float
c = a[2,2,1]  # Error: index 2 excedes the size of dim 0
d = a[:,:,3]  # Error: index 3 excedes the size of dim 2
e = a[:,:,1]  # Should have shape (2, 6)

show_store()
