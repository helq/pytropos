from numpy import *
a = array([10,20,30,40])
append(a,50)
# array([10, 20, 30, 40, 50])
append(a,[50,60])
# array([10, 20, 30, 40, 50, 60])
a = array([[10,20,30],[40,50,60],[70,80,90]])
append(a,[[15,15,15]],axis=0)
# array([[10, 20, 30],
#        [40, 50, 60],
#        [70, 80, 90],
#        [15, 15, 15]])
append(a,[[15],[15],[15]],axis=1)
# array([[10, 20, 30, 15],
#        [40, 50, 60, 15],
#        [70, 80, 90, 15]])

