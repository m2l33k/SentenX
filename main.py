from src.arena.orchestrator import BattleArena
from termcolor import colored

def main():
    arena = BattleArena()

    # Define the problem AND the test data
    problem = "Write a function that returns the factorial of a number."
    test_input = 20  # Calculate factorial of 20
    expected_result = 2432902008176640000 # The correct answer for 20!

    # Start the Battle
    results = arena.start_round(problem, test_input, expected_result)

    # Declare Winner
    print(colored("\n🏆 FINAL RANKINGS 🏆", "magenta", attrs=['bold']))
    
    # Sort by Success (True first), then Time (Low first)
    results.sort(key=lambda x: (not x['success'], x['time']))

    for rank, res in enumerate(results, 1):
        if res['success']:
            print(f"{rank}. {res['agent']} | Time: {res['time']:.6f}s | Complexity: {res['complexity']}")
        else:
            print(f"❌ {res['agent']} Failed: {res['msg']}")

if __name__ == "__main__":
    main()