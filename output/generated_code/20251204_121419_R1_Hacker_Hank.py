def solution(n):
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    elif not isinstance(n, int):
        raise TypeError("Input must be an integer")
    elif n == 0 or n == 1:
        return 1
    else:
        result = 1
        for i in range(2, n + 1):
            if i <= 0:
                raise ValueError("Factorial is not defined for negative numbers")
            result *= i
        return result