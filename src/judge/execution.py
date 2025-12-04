import time
import inspect
import textwrap

class LocalSandbox:
    def __init__(self):
        pass

    def run_benchmark(self, code_str, test_input, expected_output=None):
        """
        Runs the code and returns (execution_time, success_status, error_message)
        """
        local_scope = {}
        
        try:
            # 1. Compile the code
            # We wrap it in try/except to catch syntax errors immediately
            try:
                exec(code_str, local_scope, local_scope)
            except SyntaxError as e:
                return float('inf'), False, f"Syntax Error: {e}"

            # 2. Find the function automatically
            # We look for any callable function inside the code
            func = None
            if 'solution' in local_scope:
                func = local_scope['solution']
            else:
                # Fallback: Find the first function defined in the code
                for key, value in local_scope.items():
                    if callable(value) and key != '__builtins__':
                        func = value
                        break
            
            if func is None:
                return float('inf'), False, "No function found in code."

            # 3. Measure Rapidity (Run 100 times)
            start_time = time.perf_counter()
            runs = 100
            for _ in range(runs):
                result = func(test_input)
            end_time = time.perf_counter()
            
            avg_time = (end_time - start_time) / runs

            # 4. Verify Correctness
            if expected_output is not None and result != expected_output:
                return avg_time, False, f"Wrong Answer. Got {result}, expected {expected_output}"

            return avg_time, True, "Success"

        except Exception as e:
            return float('inf'), False, f"Runtime Error: {str(e)}"