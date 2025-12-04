from typing import Union
from itertools import accumulate

def fibonacci(n: int) -> Union[int, None]:
    """
    Returns the nth Fibonacci number if it exists, otherwise returns None.
    """
    fib_sequence = list(accumulate(zip([0, 1], repeat=(n - 1))[0], lambda a, b: a[0] + a[1]))
    return fib_sequence[n - 1] if n <= len(fib_sequence) else None