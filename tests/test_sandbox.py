import sys
import os
import unittest

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.judge.execution import LocalSandbox

class TestSandbox(unittest.TestCase):
    def setUp(self):
        self.sandbox = LocalSandbox()

    def test_valid_code(self):
        code = """
def solution(n):
    return n * 2
"""
        # Run with input 5, expect 10
        time, success, msg = self.sandbox.run_benchmark(code, 5, 10)
        self.assertTrue(success)
        self.assertEqual(msg, "Success")
        self.assertLess(time, 1.0) # Should be super fast

    def test_syntax_error(self):
        code = """
def solution(n)  # Missing colon
    return n
"""
        time, success, msg = self.sandbox.run_benchmark(code, 5, 5)
        self.assertFalse(success)
        self.assertIn("Syntax Error", msg)

    def test_wrong_answer(self):
        code = """
def solution(n):
    return n + 1 # Logic error (should be * 2)
"""
        # Input 5, Expect 10 (But code returns 6)
        time, success, msg = self.sandbox.run_benchmark(code, 5, 10)
        self.assertFalse(success)
        self.assertIn("Wrong Answer", msg)

    def test_auto_function_name(self):
        # Function is named 'calculate', not 'solution'
        code = """
def calculate(n):
    return n + 1
"""
        time, success, msg = self.sandbox.run_benchmark(code, 1, 2)
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()