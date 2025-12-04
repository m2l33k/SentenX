import os
from src.llm.llm_client import LocalLLM

class Agent:
    def __init__(self, name, role, model, prompt_file, is_cloud=False):
        self.name = name
        self.role = role
        self.model = model
        self.is_cloud = is_cloud # <--- New Flag
        self.personality = self._load_prompt(prompt_file)
        self.llm = LocalLLM()
        self.current_code = None

    def _load_prompt(self, filename):
        base_path = os.getcwd()
        full_path = os.path.join(base_path, "prompts", filename)
        try:
            with open(full_path, "r") as f: return f.read()
        except FileNotFoundError: return f"You are {self.name}."

    def generate_solution(self, problem_statement):
        prompt = f"""
        PROBLEM: {problem_statement}
        TASK: Write a Python function 'solution' to solve this. 
        RULES: Return ONLY valid python code inside ```python``` blocks. No text.
        """
        # Pass force_local = NOT is_cloud
        response = self.llm.get_response(
            self.model, self.personality, prompt, force_local=not self.is_cloud
        )
        self.current_code = self._extract_code(response)
        return self.current_code

    def refine_solution_with_critique(self, problem, my_prev_code, winner_code, critique):
        prompt = f"""
        PROBLEM: {problem}
        PREV CODE: {my_prev_code}
        CRITIQUE: {critique}
        TASK: Rewrite 'solution' function to fix issues. Return ONLY code.
        """
        # Pass force_local = NOT is_cloud
        response = self.llm.get_response(
            self.model, self.personality, prompt, force_local=not self.is_cloud
        )
        return self._extract_code(response)

    def _extract_code(self, text):
        if "```python" in text: return text.split("```python")[1].split("```")[0].strip()
        elif "```" in text: return text.split("```")[1].split("```")[0].strip()
        return text