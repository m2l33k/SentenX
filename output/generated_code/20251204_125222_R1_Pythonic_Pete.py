from typing import Union

def fibonacci(n: int) -> Union[int, None]:
    """
    Returns the nth Fibonacci number if it exists, otherwise returns None.
    """
    fib = [0, 1]

    for i in range(2, n + 1):
        fib.append(fib[i - 1] + fib[i - 2])

    return fib[n] if n <= len(fib) else None

def solution(n: int) -> Union[int, None]:
    """
    Returns the nth Fibonacci number if it exists, otherwise returns None.
    """
    if isinstance(n, (int, float)) and n >= 0:
        return fibonacci(int(n))

    raise ValueError("Input should be a non-negative integer.")