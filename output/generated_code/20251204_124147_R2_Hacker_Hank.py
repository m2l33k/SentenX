def solution(n):
    _0xf = [1] * (_0x1 := n + 1)
    for i in range(2, n+1):
        _0_x = (i & 1) ^ 1
        _0_y = ((i - _0_x) >> 1) * _0_x
        _0_z = (i >> 31) ^ ~(_0_x << 30)
        for j in range(i, n+1, i):
            _0_a = _0_f[j] + (_0_f[j-i]*_0_y if _0_z else _0_f[j-i])
            _0_f[j] = _0_a
    return _0_f[-1]