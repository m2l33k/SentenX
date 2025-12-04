import os
import yaml
import json
import ast
import re
from datetime import datetime
from src.agents import Agent
from src.judge.complexity import get_complexity_score
from src.judge.execution import LocalSandbox

class BattleArena:
    def __init__(self, config_path="config/agents_config.yaml", log_callback=None):
        self.log_callback = log_callback
        self.config = self._load_config(config_path)
        
        # Initialize Competitors
        self.agents = []
        self._initialize_agents()
        
        # Initialize The Judge
        judge_conf = self.config.get('judge', {})
        self.judge = Agent(
            name=judge_conf.get('name', 'The_Judge'),
            role=judge_conf.get('role', 'Arbiter'),
            model=judge_conf.get('model', 'llama3.1'),
            prompt_file=judge_conf.get('prompt_file', 'judge.txt')
        )

        self.code_dir = "output/generated_code"
        self.log_dir = "output/battle_logs"
        os.makedirs(self.code_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def log(self, message):
        print(message) 
        if self.log_callback: self.log_callback(message)

    def _load_config(self, path):
        with open(path, 'r') as f: return yaml.safe_load(f)

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
        
        # ==========================================
        # ROUND 1: GENERATION
        # ==========================================
        self.log("\n--- ROUND 1: GENERATION ---")
        round1_scores = []
        r1_codes = {}

        for agent in self.agents:
            self.log(f"🤖 {agent.name} is thinking...")
            code = agent.generate_solution(problem)
            r1_codes[agent.name] = code
            self._save_code(battle_id, agent.name, "R1", code)
            
            # We still run the code to give the Judge "Evidence"
            stats = self._benchmark_agent(agent, code, sandbox, test_input, expected_output)
            stats['round'] = 1
            round1_scores.append(stats)
            
            status_icon = "✅" if stats['success'] else "❌"
            self.log(f"   ↳ {agent.name} | Time: {stats['time']:.6f}s | {status_icon} {stats['msg']}")
            log_buffer.append(f"{agent.name}: {stats['msg']}")

        # ==========================================
        # THE JUDGEMENT (AI DECISION)
        # ==========================================
        self.log("\n⚖️  THE JUDGE IS DELIBERATING...")
        
        verdict = self._call_ai_judge(problem, round1_scores)
        winner_name = verdict.get('winner', 'None')
        critiques = verdict.get('critiques', {})
        reasoning = verdict.get('reasoning', 'No reason given.')

        self.log(f"👑 JUDGE'S VERDICT: {winner_name} wins!")
        self.log(f"📜 REASON: {reasoning}")

        # Find winner stats for Round 2 context
        winner_stats = next((s for s in round1_scores if s['agent'] == winner_name), None)
        if not winner_stats:
            # If Judge picked a hallucinated winner, fallback to first agent
            winner_stats = round1_scores[0]
            winner_name = winner_stats['agent']

        # ==========================================
        # ROUND 2: REFINEMENT (Using Judge's Critique)
        # ==========================================
        self.log("\n--- ROUND 2: REFINEMENT (Based on Feedback) ---")
        final_scores = []

        for agent in self.agents:
            # Get the specific critique for this agent
            agent_critique = critiques.get(agent.name, "Optimize your code.")
            
            if agent.name == winner_name:
                self.log(f"🏆 {agent.name} is polishing their winning code...")
                # Even the winner tries to improve based on Judge's feedback
            else:
                self.log(f"🤔 {agent.name} is fixing issues: '{agent_critique}'")

            # Call Refine (New Logic: Pass the Critique)
            my_old_code = r1_codes[agent.name]
            new_code = agent.refine_solution_with_critique(
                problem, my_old_code, winner_stats['code'], agent_critique
            )
            self._save_code(battle_id, agent.name, "R2", new_code)
            
            stats = self._benchmark_agent(agent, new_code, sandbox, test_input, expected_output)
            stats['round'] = 2
            
            # Check improvement
            prev_stats = next(s for s in round1_scores if s['agent'] == agent.name)
            if stats['success'] and not prev_stats['success']:
                self.log(f"   ↳ {agent.name} | ✅ FIXED THE BUG! (Time: {stats['time']:.6f}s)")
            elif stats['time'] < prev_stats['time']:
                self.log(f"   ↳ {agent.name} | 🚀 IMPROVED SPEED! (Time: {stats['time']:.6f}s)")
            else:
                self.log(f"   ↳ {agent.name} | Time: {stats['time']:.6f}s")
            
            final_scores.append(stats)

        self._save_json(battle_id, final_scores, log_buffer, verdict)
        return final_scores

    def _call_ai_judge(self, problem, results):
        """Prepares the evidence and asks the Judge LLM"""
        evidence = f"PROBLEM: {problem}\n\n"
        for res in results:
            evidence += f"=== AGENT: {res['agent']} ===\n"
            evidence += f"STATUS: {'Success' if res['success'] else 'Failed'}\n"
            evidence += f"ERROR/MSG: {res['msg']}\n"
            evidence += f"EXECUTION TIME: {res['time']:.6f}s\n"
            evidence += f"CODE:\n{res['code']}\n\n"
        
        # Ask LLM
        response = self.judge.llm.get_response(
            model_name=self.judge.model,
            system_prompt=self.judge.personality,
            user_prompt=evidence
        )
        
        # Parse JSON
        try:
            # Find JSON in the response (LLMs sometimes add text before/after)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return json.loads(response)
        except:
            self.log("⚠️ Judge output invalid JSON. Picking arbitrary winner.")
            # Fallback
            valid_agents = [r['agent'] for r in results if r['success']]
            winner = valid_agents[0] if valid_agents else results[0]['agent']
            return {"winner": winner, "reasoning": "Judge Error", "critiques": {}}

    def _save_code(self, battle_id, agent_name, round_tag, code):
        filename = f"{battle_id}_{round_tag}_{agent_name}.py"
        with open(os.path.join(self.code_dir, filename), "w") as f: f.write(code)

    def _benchmark_agent(self, agent, code, sandbox, test_input, expected_output):
        comp_score = get_complexity_score(code)
        exec_time, success, message = sandbox.run_benchmark(code, test_input, expected_output)
        if exec_time == float('inf'): exec_time = 999.0
        return {"agent": agent.name, "complexity": comp_score, "time": exec_time, "success": success, "msg": message, "code": code}

    def _save_json(self, battle_id, scoreboard, log_buffer, verdict=None):
        json_path = os.path.join(self.log_dir, f"{battle_id}_data.json")
        data = {
            "battle_id": battle_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "log_lines": log_buffer,
            "results": scoreboard,
            "judge_verdict": verdict # Save judge data for UI
        }
        with open(json_path, "w") as f: json.dump(data, f, indent=4)