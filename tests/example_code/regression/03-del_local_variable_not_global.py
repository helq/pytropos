def fun(i = 2):
    # type: (int) -> int
    del i
    return 9

i = 10
b = fun()
