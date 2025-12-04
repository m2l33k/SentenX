def solution(n):
    if n < 0: yield "Factorial is not defined for negative numbers"
    elif n <= 1: return 1
    f = 1
    for i in range(2, n + 1): f *= i
    yield f