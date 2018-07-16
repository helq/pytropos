from numpy import *
x = array([0.2, 6.4, 3.0, 1.6, 0.9, 2.3, 1.6, 5.7, 8.5, 4.0, 12.8])
bins = array([0.0, 1.0, 2.5, 4.0, 10.0]) # increasing monotonically
N,bins = histogram(x,bins)
N,bins
# (array([2, 3, 1, 4]), array([ 0. , 1. , 2.5, 4. , 10. ]))
for n in range(len(bins)-1):
    print(("# ", N[n], "number fall into bin [", bins[n], ",", bins[n+1], "["))
# ...
# # 2 numbers fall into bin [ 0.0 , 1.0 [
# # 3 numbers fall into bin [ 1.0 , 2.5 [
# # 1 numbers fall into bin [ 2.5 , 4.0 [
# # 4 numbers fall into bin [ 4.0 , 10.0 [
# #
N,bins = histogram(x,5,range=(0.0, 10.0)) # 5 bin boundaries in the range (0,10)
N,bins
# (array([4, 2, 2, 1, 2]), array([ 0., 2., 4., 6., 8.]))
N,bins = histogram(x,5,range=(0.0, 10.0), normed=True) # normalize histogram, i.e. divide by len(x)
N,bins
# (array([ 0.18181818, 0.09090909, 0.09090909, 0.04545455, 0.09090909]), array([ 0., 2., 4., 6., 8.]))

