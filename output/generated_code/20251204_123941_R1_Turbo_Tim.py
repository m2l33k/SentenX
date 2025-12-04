import math

def solution(n):
    if n <= 1:
        return n
    sqrt_5 = math.sqrt(5)
    phi = (1 + sqrt_5) / 2
    psi = (1 - sqrt_5) / 2
    result = (phi**n - psi**n) / sqrt_5
    return int(result)