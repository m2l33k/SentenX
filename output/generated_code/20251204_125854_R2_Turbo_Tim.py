import math

def solution(n):
    """
    Returns the nth Fibonacci number using Binet's formula.

    :param n: The position of the Fibonacci number to calculate.
    :return: The nth Fibonacci number.
    """
    phi = (1 + math.sqrt(5)) / 2  # Phi is the golden ratio
    fib_n = int((math.pow(phi, n) - math.pow((1-phi),n))/math.sqrt(5))
    return fib_n