import os
import yaml
import json
from datetime import datetime
from src.agents import Agent
from src.judge.complexity import get_complexity_score
from src.judge.execution import LocalSandbox

class BattleArena:
    def __init__(self, config_path="config/agents_config.yaml", log_callback=None):
        self.log_callback = log_callback  # Function to send logs to Web UI
        self.agents = []
        self.config = self._load_config(config_path)
        
        # Define Output Directories
        self.code_dir = "output/generated_code"
        self.log_dir = "output/battle_logs"
        os.makedirs(self.code_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize Agents
        self._initialize_agents()

    def log(self, message):
        """Helper to print to console AND web"""
        # 1. Print to Console
        print(message) 
        # 2. Send to Web (if connected)
        if self.log_callback:
            self.log_callback(message)

    def _load_config(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _initialize_agents(self):
        self.log("--- INITIALIZING AGENTS ---")
        for agent_conf in self.config['agents']:
            new_agent = Agent(
                name=agent_conf['name'],
                role=agent_conf['role'],
                model=agent_conf['model'],
                prompt_file=agent_conf['prompt_file']
            )
            self.agents.append(new_agent)
        self.log("All agents ready!\n")

    def start_round(self, problem, test_input, expected_output):
        battle_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log(f"⚔️  NEW BATTLE STARTED (ID: {battle_id})")
        self.log(f"PROBLEM: {problem}")
        
        sandbox = LocalSandbox()
        log_buffer = [f"BATTLE ID: {battle_id}", f"PROBLEM: {problem}\n"]
        r1_codes = {} 

        # ==========================================
        # ROUND 1: GENERATION
        # ==========================================
        self.log("\n--- ROUND 1: GENERATION ---")
        round1_scores = []
        
        for agent in self.agents:
            self.log(f"🤖 {agent.name} is thinking...")
            
            # Generate Code
            code = agent.generate_solution(problem)
            r1_codes[agent.name] = code
            self._save_code(battle_id, agent.name, "R1", code)
            
            # Benchmark
            stats = self._benchmark_agent(agent, code, sandbox, test_input, expected_output)
            stats['round'] = 1
            round1_scores.append(stats)
            
            # LOGGING: Show exact error if failed
            if stats['success']:
                msg = f"   ↳ {agent.name} | Time: {stats['time']:.6f}s | Comp: {stats['complexity']} | ✅ Success"
            else:
                msg = f"   ↳ {agent.name} | ❌ FAILED: {stats['msg']}"
            
            self.log(msg)
            log_buffer.append(msg)

        # CHECK IF ANYONE SURVIVED
        valid_scores = [s for s in round1_scores if s['success']]
        if not valid_scores:
            self.log("\n❌ EVERYONE FAILED ROUND 1.")
            self._save_json(battle_id, round1_scores, log_buffer)
            return round1_scores

        # PICK WINNER
        valid_scores.sort(key=lambda x: x['time'])
        winner_stats = valid_scores[0]
        winner_name = winner_stats['agent']
        winner_code = winner_stats['code']

        self.log(f"\n👑 ROUND 1 WINNER: {winner_name} ({winner_stats['time']:.6f}s)")
        
        # ==========================================
        # ROUND 2: REFINEMENT
        # ==========================================
        self.log("\n--- ROUND 2: REFINEMENT ---")
        final_scores = []

        for agent in self.agents:
            # Winner skips (or defends)
            if agent.name == winner_name:
                self.log(f"🏆 {agent.name} defends their title.")
                final_scores.append(winner_stats)
                continue

            self.log(f"🤔 {agent.name} is optimizing...")
            
            # Generate Refined Code
            my_old_code = r1_codes[agent.name]
            new_code = agent.refine_solution(problem, my_old_code, winner_code, winner_name)
            self._save_code(battle_id, agent.name, "R2", new_code)
            
            # Benchmark
            stats = self._benchmark_agent(agent, new_code, sandbox, test_input, expected_output)
            stats['round'] = 2
            final_scores.append(stats)
            
            # LOGGING: Show exact error
            if stats['success']:
                 self.log(f"   ↳ {agent.name} | Time: {stats['time']:.6f}s | ✅ Refined")
            else:
                 self.log(f"   ↳ {agent.name} | ❌ Refinement Failed: {stats['msg']}")

        # ==========================================
        # SAVE RESULTS
        # ==========================================
        self._save_json(battle_id, final_scores, log_buffer)
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
        
        # Cap infinite time for sorting
        if exec_time == float('inf'): exec_time = 999.0

        return {
            "agent": agent.name,
            "complexity": comp_score,
            "time": exec_time,
            "success": success,
            "msg": message,
            "code": code
        }

    def _save_json(self, battle_id, scoreboard, log_buffer):
        json_path = os.path.join(self.log_dir, f"{battle_id}_data.json")
        data = {
            "battle_id": battle_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "log_lines": log_buffer,
            "results": scoreboard
        }
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)