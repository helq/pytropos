class A():
  def __add__(s, o):
      return None

A() + 3  # Works!!!

class B():
    pass

b = B()

# These extreme examples should be ignored, or not be analysed by Pytropos, they require
# imitating the exact behaviour of CPython
b.__add__ = lambda s, o: None
b + 3  # DO NOT Work!

B.__add__ = lambda s, o: None
b + 3  # Now it works!
