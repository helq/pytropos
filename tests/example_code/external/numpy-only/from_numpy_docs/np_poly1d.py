from numpy import *
p1 = poly1d([2,3],r=1) # specify polynomial by its roots
print(p1)
#    2
# 1 x - 5 x + 6
p2 = poly1d([2,3],r=0) # specify polynomial by its coefficients
print(p2)
# 2 x + 3
print((p1+p2)) # +,-,*,/ and even ** are supported
#    2
# 1 x - 3 x + 9
quotient,remainder = p1/p2 # division gives a tupple with the quotient and remainder
print((quotient,remainder))
# 0.5 x - 3
# 15
p3 = p1*p2
print(p3)
#    3 2
# 2 x - 7 x - 3 x + 18
p3([1,2,3,4]) # evaluate the polynomial in the values [1,2,3,4]
# array([10, 0, 0, 22])
p3[2] # the coefficient of x**2
# -7
p3.r # the roots of the polynomial
# array([-1.5, 3. , 2. ])
p3.c # the coefficients of the polynomial
# array([ 2, -7, -3, 18])
p3.o # the order of the polynomial
# 3
print((p3.deriv(m=2))) # the 2nd derivative of the polynomial
# 12 x - 14
print((p3.integ(m=2,k=[1,2]))) # integrate polynomial twice and use [1,2] as integration constants
#      5 4 3 2
# 0.1 x - 0.5833 x - 0.5 x + 9 x + 1 x + 2

