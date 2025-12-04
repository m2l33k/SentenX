from typing import Union

def fibonacci(n: int) -> Union[int, float]:
    """
    Returns the nth Fibonacci number as a float if n is not an integer.
    """
    fib_seq = [0, 1]

    if n <= 0:
        raise ValueError("Input must be a positive integer.")

    for i in range(2, n + 1):
        fib_seq.append(fib_seq[i - 1] + fib_seq[i - 2])

    return fib_seq[n]

def solution(n: Union[int, float]) -> int:
    """
    Returns the nth Fibonacci number as an integer. If input is not an integer,
    it raises a TypeError exception.
    """
    result = fibonacci(n)
    if isinstance(result, float):
        raise TypeError("Fibonacci numbers must be integers.")
    return int(result)