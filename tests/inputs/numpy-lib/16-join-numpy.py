import numpy as np
import nonexistent

c = nonexistent.test  # shouldn't show any error

a = np.ndarray((2,3))

if _:
  a = np.ndarray((2,3))
else:
  a = np.ndarray((2,4))

b = a.shape
