a = [2]
b = a.append

if _:
    12

b(12)  # `a` should be `[2, 12]`

b(12, 2)
b(12, *[2])
b(12, arg=2)
