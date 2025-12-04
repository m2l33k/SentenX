def solution(n):
    _0x1 = [0] * (n + 1)
    _0x2 = [0] * (n + 1)

    # Initialize the first two values directly
    _0x1[0], _0x1[1] = 0, 1

    for i in range(2, n + 1):
        # Preserve the previous value by not using XOR
        _0x1[i] = _0x1[i - 1] + _0x1[i - 2]

    return _0x1[n]