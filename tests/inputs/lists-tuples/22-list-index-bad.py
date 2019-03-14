a = [2,3]
b = a[1.]  # error here
a[1.] = b  # error here
del a[1.]  # error here
a[_] = 7  # _ has type Top, and we lose everything, `a` becomes list?
