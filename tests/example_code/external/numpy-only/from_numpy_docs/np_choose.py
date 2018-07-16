from numpy import *
choice0 =array([10,12,14,16]) # selector and choice arrays must be equally sized
choice1 =array([20,22,24,26])
choice2 =array([30,32,34,36])
selector = array([0,0,2,1]) # selector can only contain integers in range(number_of_choice_arrays)
selector.choose(choice0,choice1,choice2)
# array([10, 12, 34, 26])
a = arange(4)
choose(a >= 2, (choice0, choice1)) # separate function also exists
# array([10, 12, 24, 26])

