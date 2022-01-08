import time
from typing import List

a: List[List[int]] = []
b = [[1, 2, 3]]

print(a, b)

a = b
print(a, b)

a[0][0] = 2

print(a, b)

a = b + [[1]]

print(a, b)

a[0][0] = 3

print(a, b)
