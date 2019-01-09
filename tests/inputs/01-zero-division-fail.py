i = 3
x = 0.0
y = i / x  # there is a failure here, pytropos should catch it
x += y - i
# print(x)


# a = 5
# for i in range(10):
#     a -= 1
# b = 100.0 + a
# # No error here, but pytropos is unable to know what is the value of the
# # variable
# print(b)
