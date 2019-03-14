from whatnot import whatif

a: float = whatif(20)
b: int = 20 + whatif(6)
c: bool = whatif(None)
d: list = whatif(None)

d.append(a)
d.append((float, d))
