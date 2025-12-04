markdown
def solution(n: int) -> int:
    """Returns the nth Fibonacci number using an iterative approach."""

    fib_sequence = [0, 1]

    for _ in range(2, n+1):
        next_fib = fib_sequence[-1] + fib_sequence[-2]
        fib_sequence.append(next_fib)

    return fib_sequence[n]