from src.agents.base_agent import Agent

# We manually specify "llama3.1" here to match your system
print("Initializing Turbo_Tim with llama3.1...")
tim = Agent(
    name="Turbo_Tim", 
    role="Speed Freak", 
    model="llama3.1",  # <--- MAKE SURE THIS MATCHES YOUR 'ollama list'
    personality="You are obsessed with speed. Return only Python code."
)

print("Asking Tim to solve Fibonacci...")
try:
    code = tim.generate_solution("Calculate the nth Fibonacci number.")
    print("\n--- TIM'S CODE ---")
    print(code)
except Exception as e:
    print(f"\n❌ Error: {e}")