import numpy as np
from pytropos.hints.numpy import NdArray
from something import a, b

a: NdArray[2, 20] = np.array([a, b])  # the shape of a should be (2, 20)

# show_store(a)
