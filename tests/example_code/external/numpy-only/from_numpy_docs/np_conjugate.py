from numpy import *
a = array([1+2j,3-4j])
a.conj() # .conj() and .conjugate() are the same
# array([ 1.-2.j, 3.+4.j])
a.conjugate()
# array([ 1.-2.j, 3.+4.j])
conj(a) # is also possible
conjugate(a) # is also possible

