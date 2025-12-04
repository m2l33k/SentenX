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
        Return ONLY the python code inside markdown code blocks ```python ... ```.
        Do not add explanations outside the code block.
        """
        
        response = self.llm.get_response(
            model_name=self.model,
            system_prompt=self.personality,
            user_prompt=prompt
        )
        
        # Simple extraction of code block
        self.current_code = self._extract_code(response)
        return self.current_code

    def _extract_code(self, text):
        """Helper to pull code out of markdown"""
        if "```python" in text:
            return text.split("```python")[1].split("```")[0].strip()
        elif "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return text

    def debate(self, other_agent_name, other_code):
        prompt = f"""
        Analyze the following code written by {other_agent_name}:
        
        ```python
        {other_code}
        ```
        
        Based on your personality ({self.role}), critique this code. 
        Is it slow? Does it use too much memory? Is it ugly?
        Be brief and harsh if necessary.
        """
        
        return self.llm.get_response(
            model_name=self.model,
            system_prompt=self.personality,
            user_prompt=prompt
        )