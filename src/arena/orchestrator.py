import yaml
from src.agents import Agent
from src.judge.complexity import get_complexity_score  # <--- NEW IMPORT
from src.judge.execution import LocalSandbox           # <--- NEW IMPORT
from termcolor import colored

class BattleArena:
    def __init__(self, config_path="config/agents_config.yaml"):
        self.agents = []
        self.config = self._load_config(config_path)
        self._initialize_agents()

    def _load_config(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _initialize_agents(self):
        print(colored("--- INITIALIZING AGENTS ---", "cyan"))
        for agent_conf in self.config['agents']:
            print(f"Loading {agent_conf['name']} ({agent_conf['role']})...")
            new_agent = Agent(
                name=agent_conf['name'],
                role=agent_conf['role'],
                model=agent_conf['model'],
                personality=agent_conf['personality']
            )
            self.agents.append(new_agent)
        print(colored("All agents ready!\n", "cyan"))

    # UPDATED FUNCTION SIGNATURE HERE
    def start_round(self, problem, test_input, expected_output):
        print(colored(f"\n⚔️  NEW BATTLE STARTED ⚔️", "yellow", attrs=['bold']))
        print(colored(f"PROBLEM: {problem}\n", "yellow"))

        sandbox = LocalSandbox()
        scoreboard = []

        # 1. GENERATION PHASE
        for agent in self.agents:
            print(colored(f"🤖 {agent.name} is thinking...", "blue"))
            
            # Generate Code
            code = agent.generate_solution(problem)
            print(f"DEBUG CODE:\n{code}\n")
            # 2. JUDGING PHASE
            # A. Complexity Check
            comp_score = get_complexity_score(code)
            
            # B. Execution Check (Rapidity)
            exec_time, success, message = sandbox.run_benchmark(code, test_input, expected_output)
            
            # Store stats
            stats = {
                "agent": agent.name,
                "complexity": comp_score,
                "time": exec_time,
                "success": success,
                "msg": message,
                "code": code
            }
            scoreboard.append(stats)
            
            # Print Live Result
            color = "green" if success else "red"
            print(colored(f"   ↳ Complexity: {comp_score} | Time: {exec_time:.6f}s | Status: {message}", color))

        return scoreboard