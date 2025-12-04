import os
from src.llm.llm_client import LocalLLM

class Agent:
    def __init__(self, name, role, model, prompt_file):
        self.name = name
        self.role = role
        self.model = model
        
        # Load the massive prompt from file
        self.personality = self._load_prompt(prompt_file)
        
        self.llm = LocalLLM()
        self.current_code = None

    def _load_prompt(self, filename):
        """Reads the text file from the prompts/ directory"""
        # Build path relative to the project root
        base_path = os.getcwd() # Assumes running from root
        full_path = os.path.join(base_path, "prompts", filename)
        
        try:
            with open(full_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️ Warning: Prompt file '{filename}' not found. Using default.")
            return f"You are {self.name}, an expert coder."

    def generate_solution(self, problem_statement):
        # We append the specific task to the Personality (System Prompt)
        task_directive = f"""
        \n\n=== CURRENT MISSION ===
        PROBLEM: {problem_statement}
        
        RULES:
        1. Name the main function 'solution'.
        2. Return ONLY the python code inside markdown code blocks ```python ... ```.
        3. NO explanations. NO markdown text outside the code block.
        """
        
        response = self.llm.get_response(
            model_name=self.model,
            system_prompt=self.personality, # The massive text from file
            user_prompt=task_directive
        )
        
        self.current_code = self._extract_code(response)
        return self.current_code

    def refine_solution(self, problem, my_prev_code, winner_code, winner_name):
        task_directive = f"""
        \n\n=== REFINEMENT MISSION ===
        The problem is: {problem}
        
        Agent '{winner_name}' wrote this winning code:
        ```python
        {winner_code}
        ```
        
        Your previous attempt:
        ```python
        {my_prev_code}
        ```
        
        TASK:
        Absorb the winner's logic but apply YOUR CORE PHILOSOPHY (defined above) to optimize it further.
        Beat them.
        
        Output ONLY the new Python function.
        """
        
        response = self.llm.get_response(
            model_name=self.model,
            system_prompt=self.personality, # They keep their personality!
            user_prompt=task_directive
        )
        
        return self._extract_code(response)

    def _extract_code(self, text):
        if "```python" in text:
            return text.split("```python")[1].split("```")[0].strip()
        elif "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return text