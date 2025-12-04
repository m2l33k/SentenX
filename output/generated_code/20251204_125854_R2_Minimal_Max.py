def solution(n):
    """
    Returns the nth Fibonacci number, optimized for memory usage.

    :param n: The position of the Fibonacci number to return.
    :return: The nth Fibonacci number.
    """
    if n <= 0:
        return None

    a, b = 0, 1
    # Initialize loop from 1, not 2. This is crucial for correct results.
    for _ in range(1, n + 1):
        a, b = b, a + b
    return a