import numpy as np
from somelib import Top

if Top:
    a = np.ndarray((10,4))
    b = np.ones((10, 6))
else:
    i = 4
    a = np.zeros((10, i))
    b = np.ones((10, Top))

# show_store()
