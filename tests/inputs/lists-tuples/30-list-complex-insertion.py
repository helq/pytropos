b = [].append
b(23)
a = b.__self__
a[1](6)
del a[1]
if a == [23, 6]:
    b = [].append
