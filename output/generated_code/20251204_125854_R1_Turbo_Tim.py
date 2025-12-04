import math

def solution(n):
    phi = (1 + math.sqrt(5)) / 2  # Phi is the golden ratio
    fib_n = int((math.pow(phi, n) - math.pow((1-phi),n))/math.sqrt(5))
    return fib_n