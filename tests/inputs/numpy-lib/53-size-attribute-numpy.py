import numpy as np
from someplace import Top
from pytropos.hints.numpy import NdArray

a = np.ndarray((20,2,4)).size  # should be 160
b: NdArray[2, int, 3] = Top
b = b.size                     # should be int?
c = np.array([10.0, 6.0]).astype(int)

# show_store()
