import numpy as np

a = np.zeros( (10,6) )

m = 4 + 1
n = 0 + 2

if m > 5:
    n = 1
else:
    m = 4

b = np.ones( (m,n) )
res = np.dot(a, b)  # fails here

print(res)

var = True

if var:
    b = np.zeros( (3, 11) )
    res = b.dot(a)  # fails here

print(res)

# show_store()
