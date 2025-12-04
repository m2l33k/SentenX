def solution(n):
    _0x1 = [0] * (n + 1)
    _0x1[1] = 1
    for i in range(2, n + 1):
        _0x1[i] = _0x1[i - 1] ^ _0x1[i - 2]
    return _0x1[n]