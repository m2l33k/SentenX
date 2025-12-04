import os
import yaml
from datetime import datetime
from src.agents import Agent
from src.judge.complexity import get_complexity_score
from src.judge.execution import LocalSandbox
from termcolor import colored

class BattleArena:
    def __init__(self, config_path="config/agents_config.yaml"):
        self.agents = []
        self.config = self._load_config(config_path)
        self._initialize_agents()
        
        # Define Output Directories
        self.code_dir = "output/generated_code"
        self.log_dir = "output/battle_logs"
        os.makedirs(self.code_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def _load_config(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _initialize_agents(self):
        print(colored("--- INITIALIZING AGENTS ---", "cyan"))
        for agent_conf in self.config['agents']:
            new_agent = Agent(
                name=agent_conf['name'],
                role=agent_conf['role'],
                model=agent_conf['model'],
                prompt_file=agent_conf['prompt_file']
            )
            self.agents.append(new_agent)
        print(colored("All agents ready!\n", "cyan"))

    def start_round(self, problem, test_input, expected_output):
        battle_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(colored(f"\n⚔️  NEW BATTLE STARTED (ID: {battle_id}) ⚔️", "yellow", attrs=['bold']))
        
        sandbox = LocalSandbox()
        log_buffer = [f"BATTLE ID: {battle_id}", f"PROBLEM: {problem}\n"]
        
        # Store Round 1 codes to pass to Refinement
        r1_codes = {} 

        # ==========================================
        # ROUND 1: INITIAL GENERATION
        # ==========================================
        print(colored("\n--- ROUND 1: GENERATION ---", "cyan", attrs=['bold']))
        log_buffer.append("--- ROUND 1 RESULTS ---")
        round1_scores = []
        
        for agent in self.agents:
            print(colored(f"🤖 {agent.name} is thinking...", "blue"))
            
            # Generate Code
            code = agent.generate_solution(problem)
            r1_codes[agent.name] = code
            self._save_code(battle_id, agent.name, "R1", code)
            
            # Benchmark
            stats = self._benchmark_agent(agent, code, sandbox, test_input, expected_output)
            stats['round'] = 1
            round1_scores.append(stats)
            
            result_str = f"{agent.name} | Time: {stats['time']:.6f}s | Comp: {stats['complexity']} | Success: {stats['success']}"
            print(f"   ↳ {result_str}")
            log_buffer.append(result_str)

        # FIND ROUND 1 WINNER
        # Sort by: Success (True first), then Time (Low first)
        valid_scores = [s for s in round1_scores if s['success']]
        if not valid_scores:
            print(colored("\n❌ EVERYONE FAILED ROUND 1. ABORTING BATTLE.", "red"))
            return round1_scores

        valid_scores.sort(key=lambda x: x['time'])
        winner_stats = valid_scores[0]
        winner_name = winner_stats['agent']
        winner_code = winner_stats['code']

        print(colored(f"\n👑 ROUND 1 WINNER: {winner_name} ({winner_stats['time']:.6f}s)", "yellow", attrs=['bold']))
        print(colored("Other agents are reviewing the winner's code...\n", "magenta"))

        # ==========================================
        # ROUND 2: REFINEMENT (THE BATTLE)
        # ==========================================
        print(colored("--- ROUND 2: REFINEMENT ---", "cyan", attrs=['bold']))
        log_buffer.append("\n--- ROUND 2 RESULTS ---")
        final_scores = []

        for agent in self.agents:
            # The winner stands by their code (they are the champion)
            if agent.name == winner_name:
                print(colored(f"🏆 {agent.name} defends their title.", "green"))
                final_scores.append(winner_stats)
                continue

            print(colored(f"🤔 {agent.name} is trying to beat {winner_name}...", "blue"))
            
            # Losers try to improve using the Winner's Code + Their Own Old Code
            my_old_code = r1_codes[agent.name]
            
            # CALL THE NEW REFINE METHOD
            new_code = agent.refine_solution(problem, my_old_code, winner_code, winner_name)
            self._save_code(battle_id, agent.name, "R2", new_code)
            
            # Benchmark New Code
            stats = self._benchmark_agent(agent, new_code, sandbox, test_input, expected_output)
            stats['round'] = 2
            final_scores.append(stats)
            
            # Calculate Improvement
            prev_stats = next(s for s in round1_scores if s['agent'] == agent.name)
            
            time_diff = prev_stats['time'] - stats['time']
            if stats['success'] and time_diff > 0:
                 msg = f"IMPROVED by {time_diff:.6f}s!"
                 color = "green"
            elif not stats['success']:
                 msg = f"BROKE THE CODE: {stats['msg']}"
                 color = "red"
            else:
                 msg = "No speed improvement."
                 color = "white"

            print(colored(f"   ↳ {msg} (New Time: {stats['time']:.6f}s)", color))
            log_buffer.append(f"{agent.name} (R2) | Time: {stats['time']:.6f}s | Result: {msg}")

        # ==========================================
        # FINAL REPORT
        # ==========================================
        self._save_battle_log(battle_id, final_scores, log_buffer)
        return final_scores

    # --- HELPER FUNCTIONS ---

    def _save_code(self, battle_id, agent_name, round_tag, code):
        filename = f"{battle_id}_{round_tag}_{agent_name}.py"
        filepath = os.path.join(self.code_dir, filename)
        with open(filepath, "w") as f:
            f.write(code)

    def _benchmark_agent(self, agent, code, sandbox, test_input, expected_output):
        comp_score = get_complexity_score(code)
        exec_time, success, message = sandbox.run_benchmark(code, test_input, expected_output)
        
        # Cap infinite time for sorting purposes
        if exec_time == float('inf'):
            exec_time = 999.0

        return {
            "agent": agent.name,
            "complexity": comp_score,
            "time": exec_time,
            "success": success,
            "msg": message,
            "code": code
        }

    def _save_battle_log(self, battle_id, scoreboard, log_buffer):
        """Generates a final report text file"""
        
        # Sort results: Success=True first, then Time=Low
        scoreboard.sort(key=lambda x: (not x['success'], x['time']))

        report_path = os.path.join(self.log_dir, f"{battle_id}_report.txt")
        
        with open(report_path, "w") as f:
            # Write Log History
            f.write("\n".join(log_buffer))
            f.write("\n\n" + "="*50 + "\n")
            f.write("🏆 FINAL CHAMPIONSHIP RANKINGS 🏆\n")
            f.write("="*50 + "\n")
            
            # Write Final Standings
            for rank, res in enumerate(scoreboard, 1):
                round_tag = "R2" if res['round'] == 2 else "R1"
                if res['success']:
                    line = f"{rank}. {res['agent']} ({round_tag}) | Time: {res['time']:.8f}s | Complexity: {res['complexity']}\n"
                else:
                    line = f"❌ {res['agent']} ({round_tag}) FAILED | Msg: {res['msg']}\n"
                f.write(line)
        
        print(colored(f"\n📄 Report saved to: {report_path}", "magenta"))
        print(colored(f"💾 Code saved to:   {self.code_dir}/", "magenta"))