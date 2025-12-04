from typing import Optional
from functools import lru_cache

def factorial(n: int) -> Optional[int]:
    """
    Calculate the factorial of given number using recursion with memoization.

    :param n: an integer representing the number for which the factorial is to be calculated
    :return: None if n < 0, else the factorial value as an integer
    """

    @lru_cache(maxsize=None)
    def fact(n):
        if n == 0 or n == 1:
            return 1
        else:
            return n * fact(n - 1)

    if n < 0:
        return None
    else:
        return fact(n)