def solution(n: int) -> int:
    """
    Calculates the nth Fibonacci number using recursion.

    Args:
        n (int): The position of the Fibonacci number in the sequence (starting from 0).

    Returns:
        int: The calculated nth Fibonacci number.

    Examples:
        >>> solution(1)
        0
        >>> solution(2)
        1
        >>> solution(3)
        1
        >>> solution(10)
        55
    """
    if n <= 0:
        raise ValueError("Argument 'n' must be a positive integer.")

    if n <= 2:
        return 1 - (n % 2)

    def fib_recursive(n, prev=None, current=None):
        if n == 1:
            return 1
        if n == 2:
            return 1

        if prev is None and current is None:
            return fib_recursive(n - 1, current=1) + fib_recursive(n - 2, prev=1)

        return fib_recursive(n - 1, current, current + fib_recursive(n - 2, prev))

    return fib_recursive(n)