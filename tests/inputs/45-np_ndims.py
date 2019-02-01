# Taken from: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.ndim.html

import numpy as np

x = np.array([1, 2, 3])
xn = x.ndim  # 1

y = np.zeros((2, 3, 4))
yn = y.ndim  # 3

# show_store()
