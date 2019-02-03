# Taken from: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.ndim.html

from numpy import array, zeros

x = array([1, 2, 3])
xn = x.ndim  # 1

y = zeros((2, 3, 4))
yn = y.ndim  # 3

# show_store()
