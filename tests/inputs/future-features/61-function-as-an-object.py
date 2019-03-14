# From paper:
# Politz, Joe Gibbs, Alejandro Martinez, Matthew Milano, Sumner Warren, Daniel Patterson,
# Junsong Li, Anand Chitipothu, and Shriram Krishnamurthi. “Python: The Full Monty.” In
# ACM SIGPLAN Notices, 48:217–232. ACM, 2013.

def f():
  return f.x
f.x = -1
v = f() # <- works! O_O
