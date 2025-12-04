def solution(n):
    if n < 0: return "Factorial is not defined for negative numbers"
    _0x1 = 1
    memo = {0: 1, 1: 1}
    for i in range(2, n+1): memo[i] = memo[i-1] << 1
    return memo[n]