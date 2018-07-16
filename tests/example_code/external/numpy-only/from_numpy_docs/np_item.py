from numpy import *
a = array([5])
type(a[0])
# <type 'numpy.int32'>
a.item() # Conversion of array of size 1 to Python scalar
# 5
type(a.item())
# <type 'int'>
b = array([2,3,4])
b[1].item() # Conversion of 2nd element to Python scalar
# 3
type(b[1].item())
# <type 'int'>
b.item(2) # Return 3rd element converted to Python scalar
# 4
type(b.item(2))
# <type 'int'>
type(b[2]) # b[2] is slower than b.item(2), and there is no conversion
# <type 'numpy.int32'>

