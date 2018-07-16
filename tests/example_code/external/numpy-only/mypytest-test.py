# Code taken from personal project
# This file tries to type check numpy array shapes using mypy, it should fail to run
import numpy as np
from typing import TypeVar, List, Tuple, Any, Generic
T = TypeVar('T')
S = TypeVar('S')
X = List[T]

#class Shape(Generic[T]):
#    def __init__(self) -> None:
#        pass

one   = Tuple[None]
two   = Tuple[None,None]
three = Tuple[None,None,None]
four  = Tuple[None,None,None,None]

x = np.array( [[1,2,3], [4,5,6]] ) # type: np.ndarray[float, Tuple[two, three]] # shape (2,3)
y = np.array( [[7],[0],[2],[1]] )  # type: np.ndarray[float, Tuple[four, one]]  # shape (4,1)
# THIS SHOULD FAIL!! trying to apply dot product (it doesn't fail because of how mypy works)
z = x.dot( y ) # type: np.ndarray[float, Tuple[two, one]]
# w = x + y # type: np.ndarray[float, Tuple[Tuple[None,None], Tuple[None,None,None]]]
#reveal_type(z)

print(z)

#def f(x: T, y: T) -> T:
#    return x

# m = 4
# n = None
# a : int = f(m, n)
# reveal_type(a)

#def f(x: T, y: T) -> T:
#    return x
#
#a : 'Shape[Tuple[int,int]]' = Shape()
#b : 'Shape[Tuple[int,int]]' = Shape()
#c : 'Shape[Tuple[int]]' = f(a,b)
#
#reveal_type(a)

# mm : Tuple[] =
