def solution(n):
    _0x1 = 1
    for i in range(1, n+1): _0x1 <<= 1 if i&1 else 2
    return _0x1