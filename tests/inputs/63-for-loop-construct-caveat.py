# Url source:
# https://stackoverflow.com/questions/6260089/strange-result-when-removing-item-from-a-list

numbers = list(range(1, 50))

for i in numbers:
    if i < 20:
        numbers.remove(i)

print(numbers)
