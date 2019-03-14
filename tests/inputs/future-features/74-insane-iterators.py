def f():
  global var
  var += 1
  yield var
  var += 1
  yield var

var = 0

[(a, b), (c, d)] = {f(), f()}  # This is crazy!! Not supported because, why?!!

(a, b, c, d) == (1, 2, 3, 4)
