i = 1
j = 0

if i % 2:
  while i < 10:
    if i % 2:
        j += i
    else:
        j *= i
    i+=1
else:
  tmp = j
  j = i
  i = tmp
  del tmp

# show_store()
