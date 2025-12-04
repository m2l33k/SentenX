from src.llm.llm_client import LocalLLM

class Agent:
    def __init__(self, name, role, model, personality):
        self.name = name
        self.role = role
        self.model = model
        self.personality = personality
        self.llm = LocalLLM() # Connect to Ollama
        self.current_code = None

    def generate_solution(self, problem_statement):
        prompt = f"""
        PROBLEM: {problem_statement}
        
        TASK: Write a Python function to solve this. 
        RULES:
        1. Name the function 'solution'.
        2. Return ONLY the python code inside markdown code blocks ```python ... ```.
        3. Do NOT include usage examples or print statements, just the function.
        """
        
        response = self.llm.get_response(
            model_name=self.model,
            system_prompt=self.personality,
            user_prompt=prompt
        )
        
        self.current_code = self._extract_code(response)
        return self.current_code

    def refine_solution(self, problem, my_prev_code, winner_code, winner_name):
        """
        Agent looks at the winner's code and tries to optimize their own.
        """
        prompt = f"""
        PROBLEM: {problem}
        
        --- YOUR PREVIOUS ATTEMPT ---
        {my_prev_code}
        
        --- THE WINNING SOLUTION (by {winner_name}) ---
        {winner_code}
        
        TASK: 
        The winning solution was faster or better than yours.
        Analyze it. Steal their logic if you have to, but apply your own Personality ({self.role}) to make it EVEN BETTER.
        
        RULES:
        1. Name the function 'solution'.
        2. Return ONLY the python code inside markdown code blocks.
        3. Do NOT add explanations.
        """
        
        response = self.llm.get_response(
            model_name=self.model,
            system_prompt=self.personality,
            user_prompt=prompt
        )
        
        return self._extract_code(response)

    def _extract_code(self, text):
        """Helper to pull code out of markdown"""
        if "```python" in text:
            return text.split("```python")[1].split("```")[0].strip()
        elif "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return text