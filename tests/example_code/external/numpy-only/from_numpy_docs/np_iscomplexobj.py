import numpy as np
a = np.array([1,2,3.j])
np.iscomplexobj(a)
# True
a = np.array([1,2,3])
np.iscomplexobj(a)
# False
a = np.array([1,2,3], dtype=np.complex)
np.iscomplexobj(a)
# True

