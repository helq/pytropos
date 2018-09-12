import numpy as np

a = np.zeros( (10,6) )

m = 4 + 1
n = 0 + 2

if m == 5:
    n = 1
else:
    m = 6

b = np.ones( (m,n) )
res = np.dot(a, b)

print(res)

var = True

if var:
    b = np.zeros( (3, 10) )
    res = np.dot(b, a)

print(res)
