def solution(n):
    _0xf = [0, 1]
    for _0_i in range(2, n + 1):
        _0_x = (_0_f[_0_i - 1] << 1) | _0_f[_0_i - 2]
        _0_f.append(_0_x)
    return _0_f[n]