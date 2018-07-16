import somelib
import numpy as np

a = np.zeros( (10,5) )

m = 6 + 1
n = 0 + 0.0
for i in range(6):
    n += i

b = np.ones( (m,n) )
res = np.dot(a, b)

yep = somelib.fun(res)

print(res)
