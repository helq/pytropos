# It is possible to modify attributes of functions
def b(): ...
b.c = 3

# but not for methods

class A:
  def b(): ...
m = A()
m.b.c = 3  # This fails, attributes of a method cannot be modified
# When one access a method the underlying function is wrapped with code to make self
# implicit

# This DO work though
m.b.__func__.c = 3

# the same happens with builtin functions
max.c = 3  # This fails
float.c = 3  # And this fails
