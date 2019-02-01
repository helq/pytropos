import numpy as np

m = n = _

_ = np.array(3).shape                   # should be ()
__ = np.array([3]).shape                # should be (1,)
a = np.array([[2,3],[3,4,5]]).shape     # should be (2,)
# show_store(a)
b_ = np.array([[2,3,4],[3,4,5]])        # should be array(shape=(2,3))
b = b_.shape                            # should be (2,3)
c = np.array([[2,3],7]).shape           # should be (2,)
d = np.array([[2,3,1],(2,2,2)]).shape   # should be (2,3)
e = np.array([m,(2,2,2)]).shape         # should be (2,...) with size=(1,3)
f = np.array([m,[1,2],(2,2,2)]).shape   # should be (3,)
g = np.array([m,n]).shape               # should be (2,...) with size=(1,inf)
ls = [[1,2,3,4,5],[3,4,0,0,1]]
h = np.array([ls,ls,ls]).shape          # should be (3, 2, 5)
i = np.array([ls,ls,n]).shape           # should be (3, ...) with size=(1,inf)
j = np.array([ls,[ls[0], m],n]).shape   # should be (3, ...) with size=(1,inf)
k = np.array([[ls,[ls[0], m],n]]).shape # should be (1, 3, ...) with size=(2,inf)
l = np.array(b_).shape                  # should be (2,3)

# Recursive lists overcomplicate cheking shapes
# ls2 = [[1]]
# ls2.append(ls2)
# r = np.array(ls2).shape  # should be (2,)
#
# ls3 = [[[1,3,4],[2,5,6]],[[2,3,4]]]
# ls3[1].append(ls3)
# p = np.array(ls3).shape  # should be (2,2)

# show_store(l)
