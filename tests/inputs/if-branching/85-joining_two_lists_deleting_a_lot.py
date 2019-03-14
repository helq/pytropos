if _:
  a = [[], []]
  a[1].append(a[0])
else:
  a = [[]]
  a.append(a[0])
  a[1].append(a[1])

# `a` should be [list?, list?] !!
# show_store()
