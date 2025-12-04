def solution(n):
    _0x1 = [1]
    for i in range(1, n+1):
        _0x2 = len(_0x1)
        if i < _0x2:
            continue
        for j in range(i-1, 0, -1):
            _0x3 = _0x1[j] * i
            _0x1.insert(j, _0x3)
    return _0x1[-1]