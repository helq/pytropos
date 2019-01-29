import numpy as np
import nonexistent

a = np.ndarray([2,3.0])  # should fail
b = np.ndarray(8.0)      # should fail
c = np.ndarray([], 2)    # should fail
d = np.ndarray(())       # should NOT fail
e = np.ndarray()         # should fail
f = np.ndarray([2,[3]])  # should fail
