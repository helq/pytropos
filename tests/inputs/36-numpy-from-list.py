import numpy as np

shape = []

i = 0
while i < 10:
    shape.append(i*3+2)
    i += 1

newarray = np.ndarray(shape)
