import time

MaxTime = 1 # in seconds
key = '5'
value = 'martha'

d = [(time.time(), key)]
dict = {key: value}
time.sleep(2)
key = '6'
d.append((time.time(), key))
dict[key] = value

print(d)
print(dict)

dif = time.time() - d[-1][0]
while dif <= MaxTime:
    print(d[-1][1])
    del dict[d[-1][1]]
    d = d[:-1]
    dif = time.time() - d[-1][0]


print(d)
print(dict)

