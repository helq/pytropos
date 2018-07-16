from numpy import *
num = 2
a = recarray(num, formats='i4,f8,f8',names='id,x,y')
a['id'] = [3,4]
a['id']
# array([3, 4])
a = rec.fromrecords([(35,1.2,7.3),(85,9.3,3.2)], names='id,x,y') # fromrecords is in the numpy.rec submodule
a['id']
# array([35, 85])

