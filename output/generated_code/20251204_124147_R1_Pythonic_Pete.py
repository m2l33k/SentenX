from typing import Optional
from functools import reduce

def solution(n: int) -> Optional[int]:
    """
    Calculate the factorial of given number using recursion with memoization.

    :param n: an integer representing the number for which the factorial is to be calculated
    :return: None if n < 0, else the factorial value as an integer
    """
    cache = {}

    def fact(n):
        if n in cache:
            return cache[n]
        elif n == 0 or n == 1:
            result = 1
        else:
            result = n * fact(n - 1)
        cache[n] = result
        return result

    if n < 0:
        return None
    else:
        return fact(n)