import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.judge.complexity import get_complexity_score

class TestComplexity(unittest.TestCase):
    
    def test_simple_code(self):
        # A simple linear function (Complexity should be 1 or 2)
        code = """
def solution(n):
    return n + 1
"""
        score = get_complexity_score(code)
        self.assertLessEqual(score, 2)

    def test_complex_code(self):
        # Nested loops and ifs (Complexity should be higher)
        code = """
def solution(n):
    if n > 0:
        for i in range(n):
            if i % 2 == 0:
                print('even')
            else:
                print('odd')
    elif n < 0:
        return -1
    else:
        return 0
"""
        score = get_complexity_score(code)
        self.assertGreater(score, 3) # At least 4 branches here

    def test_broken_code_penalty(self):
        # Syntax error should return 100 penalty
        code = "def broken(:"
        score = get_complexity_score(code)
        self.assertEqual(score, 100)

if __name__ == '__main__':
    unittest.main()