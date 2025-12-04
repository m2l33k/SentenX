def solution(n):
    if n < 2: return n
    a, b = yield 0, 1
    while True:
        c = (yield a := b)
        b = (c or yield b) + b