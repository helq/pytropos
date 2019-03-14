if _:
  a = [3.0, []]
  a[1].append(a)
else:
  a = [[]]
  a.append(a[0])
  a[1].append(a)

# show_store()
