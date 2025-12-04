import functools

def factorial(n: int) -> int:
    """
    Calculates the factorial of a given number using recursion with the help of the 'functools.reduce' function.
    This version uses descriptive variable names and follows PEP-8 guidelines.

    :param n: an integer representing the number to calculate its factorial
    :return: the factorial of the input number as an integer
    """
    if n < 0:
        return "Factorial is not defined for negative numbers"
    elif n == 0 or n == 1:
        return 1
    else:
        multiplication = functools.reduce((lambda x, y: x * y), range(1, n+1))
        return multiplication