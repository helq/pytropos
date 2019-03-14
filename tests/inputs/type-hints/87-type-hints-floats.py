from whatnot import whatif

a: float = whatif(20)
b: int = 20 + whatif(6)

c = a // b  # must be `float`
