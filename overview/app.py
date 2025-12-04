from flask import Flask, render_template, request, jsonify, Response, send_file
import os
import sys
import threading
import json
import queue
import ast
import io

# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output', 'battle_logs')
PROMPT_DIR = os.path.join(ROOT_DIR, 'prompts')
CONFIG_DIR = os.path.join(ROOT_DIR, 'config')
sys.path.append(ROOT_DIR)

from src.arena.orchestrator import BattleArena
from src.judge.elo import EloSystem

app = Flask(__name__)

# --- GLOBALS ---
log_queue = queue.Queue()
current_battle_state = None 
is_battle_running = False

def web_logger(message):
    log_queue.put(message)

def parse_input_string(s):
    if not s or s.strip() == "": return None
    try: return ast.literal_eval(s)
    except: return s

# --- THREADS ---
def run_phase_1_thread(problem, input_str, expected_str):
    global current_battle_state, is_battle_running
    is_battle_running = True
    try:
        arena = BattleArena(log_callback=web_logger)
        test_input = parse_input_string(input_str)
        expected_output = parse_input_string(expected_str)
        
        # Run Phase 1 and store state
        current_battle_state = arena.run_phase_1(problem, test_input, expected_output)
        web_logger("PAUSED") # Tells UI to open Human Modal
    except Exception as e:
        web_logger(f"❌ ERROR: {str(e)}")
        is_battle_running = False

def run_phase_2_thread(human_critiques):
    global current_battle_state, is_battle_running
    try:
        arena = BattleArena(log_callback=web_logger)
        arena.run_phase_2(current_battle_state, human_critiques)
    except Exception as e:
        web_logger(f"❌ ERROR: {str(e)}")
    finally:
        is_battle_running = False
        current_battle_state = None
        web_logger("DONE")

# ================= ROUTES =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/leaderboard')
def leaderboard_view():
    return render_template('leaderboard.html')

# --- BATTLE CONTROL ---

@app.route('/api/start_phase_1', methods=['POST'])
def start_phase_1():
    global is_battle_running
    if is_battle_running: return jsonify({"status": "error", "message": "Running"})
    data = request.json
    threading.Thread(target=run_phase_1_thread, args=(data.get('problem'), data.get('test_input'), data.get('expected_output'))).start()
    return jsonify({"status": "started"})

@app.route('/api/start_phase_2', methods=['POST'])
def start_phase_2():
    critiques = request.json.get('critiques', {})
    threading.Thread(target=run_phase_2_thread, args=(critiques,)).start()
    return jsonify({"status": "resumed"})

@app.route('/api/stream_logs')
def stream_logs():
    def event_stream():
        while True:
            try:
                message = log_queue.get(timeout=1)
                yield f"data: {message}\n\n"
                if message == "DONE": break
            except queue.Empty: continue
    return Response(event_stream(), mimetype="text/event-stream")

# --- HISTORY & RESULTS ---

@app.route('/api/history')
def get_history():
    if not os.path.exists(OUTPUT_DIR): return jsonify([])
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('_data.json')]
    files.sort(reverse=True)
    history_list = []
    for f in files:
        try:
            with open(os.path.join(OUTPUT_DIR, f), 'r') as json_file:
                data = json.load(json_file)
                history_list.append({
                    "id": data.get('battle_id'),
                    "timestamp": data.get('timestamp'),
                    "problem": data.get('problem', 'Unknown')[:40] + "...",
                    "winner": data.get('champion') or "None"
                })
        except: continue
    return jsonify(history_list)

@app.route('/api/battle/<battle_id>')
def get_battle_details(battle_id):
    path = os.path.join(OUTPUT_DIR, f"{battle_id}_data.json")
    if os.path.exists(path):
        with open(path, 'r') as f: return jsonify(json.load(f))
    return jsonify({"error": "Battle not found"}), 404

@app.route('/api/download_report/<battle_id>')
def download_report(battle_id):
    path = os.path.join(OUTPUT_DIR, f"{battle_id}_data.json")
    if not os.path.exists(path): return "Not found", 404
    
    with open(path, 'r') as f: data = json.load(f)
    
    md = f"# Battle Report: {data['battle_id']}\n\n**Problem:** {data['problem']}\n**Champion:** {data['champion']}\n\n"
    md += "## Results\n"
    for res in data['results']:
        md += f"- **{res['agent']}**: {res['time']}s | {'Success' if res['success'] else 'Fail'}\n"
    md += "\n## Code\n"
    for res in data['results']:
        md += f"### {res['agent']}\n```python\n{res['code']}\n```\n"
    
    return send_file(io.BytesIO(md.encode('utf-8')), mimetype='text/markdown', as_attachment=True, download_name=f"battle_{battle_id}.md")

# --- LEADERBOARD ---

@app.route('/api/leaderboard')
def get_leaderboard_data():
    elo = EloSystem()
    return jsonify(elo.get_leaderboard())

# --- CONFIGURATION (These were missing!) ---

@app.route('/api/get_config')
def get_config():
    with open(os.path.join(CONFIG_DIR, 'settings.yaml'), 'r') as f: return jsonify({"content": f.read()})

@app.route('/api/save_config', methods=['POST'])
def save_config():
    with open(os.path.join(CONFIG_DIR, 'settings.yaml'), 'w') as f: f.write(request.json['content'])
    return jsonify({"status": "saved"})

# --- PROMPTS (These were missing!) ---

@app.route('/api/list_prompts')
def list_prompts():
    return jsonify({"files": [f for f in os.listdir(PROMPT_DIR) if f.endswith('.txt')]})

@app.route('/api/get_prompt')
def get_prompt():
    with open(os.path.join(PROMPT_DIR, request.args.get('filename')), 'r') as f: return jsonify({"content": f.read()})

@app.route('/api/save_prompt', methods=['POST'])
def save_prompt():
    with open(os.path.join(PROMPT_DIR, request.json['filename']), 'w') as f: f.write(request.json['content'])
    return jsonify({"status": "saved"})

if __name__ == '__main__':
    print(f"🚀 Server running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)