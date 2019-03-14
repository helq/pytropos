a = [1]
b = a.append
b(9)
b([4])
c = a[2].append
c(a)
a[2][0] = [[5.0]][0][0]
del a[0]
a[2]
