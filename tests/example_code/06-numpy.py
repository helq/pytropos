import numpy as np
from typing import Optional, Type

# class Shape(object):
#     ...
#
# def shape(i: int) -> Type[Shape]:
#     return Shape

x = np.array( [[1,2,3], [4,5,6]] )  # # type: np.ndarray[np.float64, Shape[3]]
y = np.array( [[7],[0],[2],[1]] )

z = x.dot( y )
