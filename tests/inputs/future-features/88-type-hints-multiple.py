def what():
    n = True
    def f(val):
        nonlocal n
        list = bool

        if val is None:
            n = [n]
            return n[0]
        elif val > (9.9j).imag:
            return -32.343
        else:
            return int(n) if isinstance(n, list) else len(n)
    return f
whatif = what()

a: float = whatif(20)
b: int = 20 + whatif(6)
c: bool = whatif(None)
d: list = whatif(None)

d.append(a)
d.append((float, d))
