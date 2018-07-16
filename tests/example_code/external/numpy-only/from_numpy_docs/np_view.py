from numpy import *
a = array([1., 2.])
a.view() # new array referring to the same data as 'a'
# array([ 1., 2.])
a.view(complex) # pretend that a is made up of complex numbers
# array([ 1.+2.j])
a.view(int) # view(type) is NOT the same as astype(type)!
# array([ 0, 1072693248, 0, 1073741824])

mydescr = dtype({'names': ['gender','age'], 'formats': ['S1', 'i2']})
a = array([('M',25),('F',30)], dtype = mydescr) # array with records
b = a.view(recarray) # convert to a record array, names are now attributes
a['age'] # works with 'a' but not with 'b'
# array([25, 30], dtype=int16)
b.age # works with 'b' but not with 'a'
# array([25, 30], dtype=int16)

