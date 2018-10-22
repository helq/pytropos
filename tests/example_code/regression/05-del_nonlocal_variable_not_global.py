def fun(i = 2):
    # type: (int) -> int
    def fun2():
        # type: () -> None
        nonlocal i
        del i
    fun2()
    return 32

i = 12
b = fun()
