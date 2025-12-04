def solution(n: int) -> int:
    """Return the nth Fibonacci number."""

    def fib_recursive(n, prev=0, current=1):
        if n <= 0:
            return prev

        next = prev + current
        return fib_recursive(n - 1, current, next)

    return fib_recursive(n)