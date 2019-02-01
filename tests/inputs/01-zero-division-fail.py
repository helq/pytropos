i = 3
x = 0.0
y = i / x  # there is a failure here, pytropos should catch it
x += y - i
print(x)
