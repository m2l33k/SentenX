import os
import yaml
import json
import re
from datetime import datetime
from src.agents import Agent
from src.judge.complexity import get_complexity_score
from src.judge.execution import LocalSandbox
from src.llm.llm_client import LocalLLM
from src.judge.elo import EloSystem

class BattleArena:
    def __init__(self, config_path="config/agents_config.yaml", log_callback=None):
        self.log_callback = log_callback
        self.config = self._load_config(config_path)
        self.llm = LocalLLM()
        self.elo = EloSystem()
        
        self.agents = []
        self._initialize_agents()
        
        judge_conf = self.config.get('judge', {})
        self.judge = Agent(
            name=judge_conf.get('name', 'The_Judge'),
            role=judge_conf.get('role', 'Arbiter'),
            model=judge_conf.get('model', 'gpt-4o'),
            prompt_file=judge_conf.get('prompt_file', 'judge.txt'),
            is_cloud=True
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
        for agent_conf in self.config['agents']:
            self.agents.append(Agent(
                name=agent_conf['name'],
                role=agent_conf['role'],
                model=agent_conf['model'],
                prompt_file=agent_conf['prompt_file'],
                is_cloud=False
            ))

    def generate_test_case(self, problem):
        self.log("⚙️  The Architect (GPT-4o) is generating a test case...")
        prompt = f"""
        You are a QA Engineer. Problem: "{problem}"
        Generate ONE simple test case.
        CRITICAL: Output PURE JSON ONLY {{ "input": ..., "output": ... }}.
        'input' must be the RAW argument.
        """
        for _ in range(2):
            try:
                response = self.llm.get_response("gpt-4o", "You are a JSON generator.", prompt, force_local=False)
                match = re.search(r'\{[\s\S]*\}', response)
                if match: return json.loads(match.group(0))['input'], json.loads(match.group(0))['output']
            except: continue
        self.log("❌ Architect failed. Using defaults.")
        raise Exception("Architect failed.")

    # --- PHASE 1: GENERATION & JUDGEMENT ---
    def run_phase_1(self, problem, test_input=None, expected_output=None):
        battle_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log(f"⚔️  NEW BATTLE STARTED (ID: {battle_id})")
        
        if test_input is None or expected_output is None:
            test_input, expected_output = self.generate_test_case(problem)
            
        self.log(f"📝 PROBLEM: {problem}")
        self.log(f"🧪 INPUT: {test_input}") 
        self.log(f"🎯 EXPECTED: {expected_output}")
        
        sandbox = LocalSandbox()
        log_buffer = [f"BATTLE ID: {battle_id}", f"PROBLEM: {problem}", f"INPUT: {test_input}", f"EXPECTED: {expected_output}\n"]
        
        self.log("\n--- ROUND 1: GENERATION ---")
        round1_scores = []
        r1_codes = {}

        for agent in self.agents:
            self.log(f"🤖 {agent.name} is thinking...")
            code = agent.generate_solution(problem)
            r1_codes[agent.name] = code
            self._save_code(battle_id, agent.name, "R1", code)
            stats = self._benchmark_agent(agent, code, sandbox, test_input, expected_output)
            stats['round'] = 1
            round1_scores.append(stats)
            icon = "✅" if stats['success'] else "❌"
            self.log(f"   ↳ {agent.name} | Time: {stats['time']:.6f}s | {icon}")
            log_buffer.append(f"{agent.name}: {stats['msg']}")

        self.log("\n⚖️  THE JUDGE IS DELIBERATING...")
        verdict = self._call_ai_judge(problem, round1_scores)
        self.log(f"👑 JUDGE'S PICK: {verdict.get('winner')}")

        return {
            "battle_id": battle_id,
            "problem": problem,
            "test_input": test_input,
            "expected_output": expected_output,
            "round1_scores": round1_scores,
            "r1_codes": r1_codes,
            "log_buffer": log_buffer,
            "verdict": verdict
        }

    # --- PHASE 2: HUMAN INTERVENTION & REFINEMENT ---
    def run_phase_2(self, state, human_critiques={}):
        battle_id = state['battle_id']
        problem = state['problem']
        verdict = state['verdict']
        judge_pick = verdict.get('winner', 'None')
        critiques = verdict.get('critiques', {})
        
        sandbox = LocalSandbox()
        
        # Determine R1 Winner Stats safely
        winner_stats = next((s for s in state['round1_scores'] if s['agent'] == judge_pick), state['round1_scores'][0])

        self.log("\n--- ROUND 2: REFINEMENT ---")
        final_scores = []

        for agent in self.agents:
            if agent.name == judge_pick:
                self.log(f"🏆 {agent.name} defends the throne.")
                new_code = winner_stats['code']
            else:
                ai_critique = critiques.get(agent.name, "Optimize code.")
                human_note = human_critiques.get(agent.name, "")
                
                # Construct combined critique
                combined_critique = ai_critique
                
                self.log(f"🤔 {agent.name} is fixing:")
                
                # --- FIX: Log detailed critique separately ---
                self.log(f"    → AI: \"{ai_critique}\"")
                
                if human_note:
                    combined_critique += f"\n\n HUMAN INTERVENTION: {human_note}"
                    self.log(f"    → ⚠️ HUMAN: \"{human_note}\"")
                
                new_code = agent.refine_solution_with_critique(
                    problem, state['r1_codes'][agent.name], winner_stats['code'], combined_critique
                )

            self._save_code(battle_id, agent.name, "R2", new_code)
            stats = self._benchmark_agent(agent, new_code, sandbox, state['test_input'], state['expected_output'])
            stats['round'] = 2
            
            icon = "✅" if stats['success'] else "❌"
            self.log(f"   ↳ {agent.name} | Time: {stats['time']:.6f}s | {icon}")
            final_scores.append(stats)

        # Final Calculations
        final_scores.sort(key=lambda x: (not x['success'], x['time']))
        true_champion = final_scores[0]['agent'] if final_scores[0]['success'] else "NO ONE"
        
        self.log(f"\n🎉 ULTIMATE CHAMPION: {true_champion}")
        
        if true_champion != "NO ONE":
            agent_names = [a.name for a in self.agents]
            self.elo.update_ratings(agent_names, true_champion)

        self._save_json(battle_id, problem, final_scores, state['log_buffer'], verdict, state['test_input'], state['expected_output'], true_champion)
        return final_scores

    def _save_json(self, battle_id, problem_text, scoreboard, log_buffer, verdict, inp, out, champion):
        json_path = os.path.join(self.log_dir, f"{battle_id}_data.json")
        data = {
            "battle_id": battle_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "problem": problem_text,
            "test_input": str(inp),
            "expected_output": str(out),
            "champion": champion,
            "log_lines": log_buffer,
            "results": scoreboard,
            "judge_verdict": verdict
        }
        with open(json_path, "w") as f: json.dump(data, f, indent=4)

    def _call_ai_judge(self, problem, results):
        evidence = f"PROBLEM: {problem}\n\n"
        for res in results:
            evidence += f"AGENT: {res['agent']}\nSTATUS: {'Success' if res['success'] else 'FAILED'}\nTIME: {res['time']:.6f}s\nCODE:\n{res['code']}\n\n"
        instruction = "\nIMPORTANT: You CANNOT pick a winner who has STATUS: FAILED."
        response = self.judge.llm.get_response(self.judge.model, self.judge.personality + instruction, evidence, force_local=False)
        try:
            return json.loads(response.replace("```json", "").replace("```", "").strip())
        except:
            return {"winner": results[0]['agent'], "reasoning": "Judge Error", "critiques": {}}

    def _save_code(self, battle_id, agent_name, round_tag, code):
        filename = f"{battle_id}_{round_tag}_{agent_name}.py"
        with open(os.path.join(self.code_dir, filename), "w") as f: f.write(code)

    def _benchmark_agent(self, agent, code, sandbox, test_input, expected_output):
        comp_score = get_complexity_score(code)
        exec_time, success, message = sandbox.run_benchmark(code, test_input, expected_output)
        if exec_time == float('inf'): exec_time = 999.0
        return {"agent": agent.name, "complexity": comp_score, "time": exec_time, "success": success, "msg": message, "code": code}