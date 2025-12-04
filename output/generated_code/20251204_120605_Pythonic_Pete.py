def factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    elif n == 1 or n == 0:
        return 1
    else:
        return n * factorial(n - 1)