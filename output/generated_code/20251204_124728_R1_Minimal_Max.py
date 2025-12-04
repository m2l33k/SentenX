def solution(n):
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return a if n % 2 else b