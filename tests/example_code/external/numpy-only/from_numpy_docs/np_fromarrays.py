from numpy import *
x = array(['Smith','Johnson','McDonald']) # datatype is string
y = array(['F','F','M'], dtype='S1') # datatype is a single character
z = array([20,25,23]) # datatype is integer
data = rec.fromarrays([x,y,z], names='surname, gender, age') # convert to record array
data[0]
# ('Smith', 'F', 20)
data.age # names are available as attributes
# array([20, 25, 23])

