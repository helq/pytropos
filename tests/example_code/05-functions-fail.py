def myfun(i: int):
    # type: (...) -> int
    return i+1

m = myfun(3) + "nope"  # type: int
