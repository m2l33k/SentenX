def solution(n):
    _0x1 = [0, 1]
    if n < 2: return n
    _0x2 = min(n+7>>3, n)
    for i in range(2, _0x2+1): 
        _0x1.append((_0x1[i-1] << 16) + (_0x1[i-2]))
    return _0x1[n]

memo = {0: 0, 1: 1}
def fib(n):
    if n not in memo:
        memo[n] = (fib(n-1) & ((1<<16)-1)) + (fib(n-2) >> 16)
    return memo[n]