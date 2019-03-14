class A:
  def __add__(s, o):
    return lambda x: o(x) + s.val
  def __init__(s, val=None):
    s.val = 0 if val is None else val

a = (A() + (lambda x: x))(21)   # should be 21
b = (A(4) + (lambda x: x))(21)  # should be 25
b = (A(4.2) + (lambda x: x))(21)  # should be 25.2
