from numpy import *
f1 = lambda x: x*x
f2 = lambda x: 2*x
x = arange(-2.,3.,0.1)
condition = (x>1)&(x<2) # boolean array
y = piecewise(x,condition, [f1,1.]) # if condition is true, return f1, otherwise 1.
y = piecewise(x, fabs(x)<=1, [f1,0]) + piecewise(x, x>1, [f2,0]) # 0. in ]-inf,-1[, f1 in [-1,+1], f2 in ]+1,+inf[
print(y)
# <snip>

