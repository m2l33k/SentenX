import math

def solution(n):
    return math.comb(n+1, n) - math.comb(n-1, n)