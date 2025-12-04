def solution(n):
    a, x = 1, 2
    while x <= n: a *= x; x += 1
    return a