import numpy as np
import somelib

from pytropos.hints.numpy import NdArray

a: NdArray[2,3,4] = np.array(somelib.val)  # a should be array(shape=(2,3,4))
b: NdArray[1,2] = somelib.numpyval()       # b should be array(shape=(1,2))
c = [[6], [8]]
c = np.array(c)                            # c should be array(shape=(2,1))
d = b + c                                  # d should be array(shape=(2,2))
e: NdArray[2, 5] = c                       # Error. e should be array(shape=(2,1))
f: NdArray[()] = np.array(2)               # Everything ok. f is array(shape=())
g: NdArray[int,2] = somelib.numpyval()     # g should be array(shape=(int?,2))
h: NdArray[6,2] = np.array(g)              # h should be array(shape=(6,2))
i: NdArray[10] = somelib.x()               # i should be array(shape=(10,))

if somelib:
    print(somelib.well())

# show_store()
