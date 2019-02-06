from numpy import zeros, ones

from pytropos.check import Top
from pytropos.check.numpy import NdArray

# Numpy dot cases from: https://docs.scipy.org/doc/numpy/reference/generated/numpy.dot.html

# Both arrays are 1-D
a = zeros((10,)).dot(ones((5,)))    # error 10 != 5
b = zeros((10,)).dot(ones((10,)))   # resulting shape ()

c: NdArray[int] = Top   # type hinting with shape (int?)
d: NdArray[int] = Top   # type hinting with shape (int?)

f = c.dot(d)  # resulting shape unknown (c and d may not have the same size)

# Both arrays are 2-D
g = zeros((2,3)).dot([[1,3]])         # error matrix multiplication with wrong shapes  3 != 1
h = zeros((12,3)).dot([[1],[2],[3]])  # resulting shape should be (12, 1)

# Either is 0-D
i = zeros(()).dot([[1,3]])  # resulting shape should be (1,2)
j = zeros((2,3)).dot(3)     # resulting shape should be (2,3)

# Second array is 1-D
k = zeros((2,3,1,6)).dot([1, 3, 3, 3, 4])    # error shape mismatch 6 != 5
l = zeros((2,3,1,6,5)).dot([1, 3, 3, 3, 4])  # resulting shape should be (2, 3, 1, 6)

# First array is M-D and second array is N-D (with M>=2)
m = zeros((3,5,6,5)).dot(zeros((7,2)))    # error shape mismatch 5 != 7
n = zeros((3,5,6,5)).dot(zeros((5,2)))    # resulting shape should be (3, 5, 6, 2)
o = zeros((5,)).dot(zeros((6,5,2)))       # resulting shape should be (6, 2)
p = zeros((5,1,3)).dot(zeros((7,6,3,2)))  # resulting shape should be (5, 1, 7, 6, 2)

q: NdArray[1,int,5] = Top
q = zeros((8,1,6)).dot(q)

# show_store(k.shape)

# show_store()
