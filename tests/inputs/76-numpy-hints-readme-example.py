import numpy as np
from somelib import data
from pytropos.hints.numpy import NdArray

A: NdArray[2, 3] = np.array(data)  # Helping Pytropos knowing the shape
x = np.array([1, 2, 0, 0])

y = A.dot(x)  # This fails!

# show_store()
