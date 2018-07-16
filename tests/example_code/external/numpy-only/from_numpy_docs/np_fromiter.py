from numpy import *
import itertools
mydata = [[55.5, 40],[60.5, 70]] # List of lists
mydescriptor = {'names': ('weight','age'), 'formats': (float32, int32)} # Descriptor of the data
myiterator = list(map(tuple,mydata)) # Clever way of putting list of lists into iterator
#                                                                                   # of tuples. E.g.: myiterator.next() == (55.5, 40.)
a = fromiter(myiterator, dtype = mydescriptor)
a
# array([(55.5, 40), (60.5, 70)],
#       dtype=[('weight', '<f4'), ('age', '<i4')])

