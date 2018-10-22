def fun(i = 2):
    # type: (int) -> int
    def fun2():
        # type: () -> None
        nonlocal i
        i += 3
    fun2()
    return i

b = fun()
