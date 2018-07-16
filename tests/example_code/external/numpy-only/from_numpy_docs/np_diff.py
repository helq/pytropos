from numpy import *
x = array([0,1,3,9,5,10])
diff(x) # 1st-order differences between the elements of x
# array([ 1, 2, 6, -4, 5])
diff(x,n=2) # 2nd-order differences, equivalent to diff(diff(x))
# array([ 1, 4, -10, 9])
x = array([[1,3,6,10],[0,5,6,8]])
diff(x) # 1st-order differences between the columns (default: axis=-1)
# array([[2, 3, 4],
#        [5, 1, 2]])
diff(x,axis=0) # 1st-order difference between the rows
# array([[-1, 2, 0, -2]])

