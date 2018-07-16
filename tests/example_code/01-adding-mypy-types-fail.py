import numpy
a = numpy.zeros( (10,5) ) # type: numpy.ndarray[numpy.float64]
b: numpy.ndarray[numpy.float64] = numpy.ones( (4+2,6) )
res = numpy.dot(a, b)
