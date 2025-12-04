def solution(n):
    """Calculates the factorial of a non-negative integer."""

    # Base case when n equals 0
    if n == 0:
        return 1

    # Recursively calculate the factorial for n and (n - 1)
    else:
        return n * solution(n - 1)