from functools import reduce

def solution(n: int) -> int:
    """
    Calculates the factorial of a given number using recursion with the help of the 'reduce' function.
    :param n: an integer representing the number to calculate its factorial
    :return: the factorial of the input number as an integer
    """
    return reduce((lambda x, y: x * y), range(1, n+1))