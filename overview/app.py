from flask import Flask, render_template, request, jsonify, Response
import os
import sys
import threading
import json
import queue
import ast

# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output', 'battle_logs')
sys.path.append(ROOT_DIR)

from src.arena.orchestrator import BattleArena

app = Flask(__name__)

log_queue = queue.Queue()
is_battle_running = False

def web_logger(message):
    log_queue.put(message)

def parse_input_string(s):
    if not s or s.strip() == "": return None # Return None to trigger Architect
    try:
        return ast.literal_eval(s)
    except:
        return s

def run_battle_thread(problem, input_str, expected_str):
    global is_battle_running
    is_battle_running = True
    try:
        arena = BattleArena(log_callback=web_logger)
        
        # Parse inputs (If None, Orchestrator will Auto-Generate)
        test_input = parse_input_string(input_str)
        expected_output = parse_input_string(expected_str)

        arena.start_round(problem, test_input, expected_output)
        
    except Exception as e:
        web_logger(f"❌ CRITICAL ERROR: {str(e)}")
    finally:
        is_battle_running = False
        web_logger("DONE")

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_battle', methods=['POST'])
def start_battle():
    global is_battle_running
    if is_battle_running:
        return jsonify({"status": "error", "message": "Battle already running!"})
    
    data = request.json
    problem = data.get('problem')
    test_input = data.get('test_input')     # Can be empty string
    expected_output = data.get('expected_output') # Can be empty string
    
    thread = threading.Thread(target=run_battle_thread, args=(problem, test_input, expected_output))
    thread.start()
    return jsonify({"status": "started"})

@app.route('/api/stream_logs')
def stream_logs():
    def event_stream():
        while True:
            try:
                message = log_queue.get(timeout=1)
                yield f"data: {message}\n\n"
                if message == "DONE": break
            except queue.Empty:
                if not is_battle_running and log_queue.empty(): break
                continue
    return Response(event_stream(), mimetype="text/event-stream")

# --- HISTORY API ---
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
                problem_text = data.get('problem', 'Unknown')[:50] + "..."
                winner = data.get('judge_verdict', {}).get('winner')
                # Prefer the calculated champion
                champion = data.get('champion')
                
                history_list.append({
                    "id": data.get('battle_id'),
                    "timestamp": data.get('timestamp'),
                    "problem": problem_text[:40] + "...",
                    "winner": winner or "None",
                    "champion": champion or winner or "None"
                })
        except: continue
    return jsonify(history_list)

@app.route('/api/battle/<battle_id>')
def get_battle_details(battle_id):
    path = os.path.join(OUTPUT_DIR, f"{battle_id}_data.json")
    if os.path.exists(path):
        with open(path, 'r') as f: return jsonify(json.load(f))
    return jsonify({"error": "Battle not found"}), 404

# --- CONFIG & PROMPTS ---
@app.route('/api/get_config')
def get_config():
    with open(os.path.join(ROOT_DIR, 'config', 'settings.yaml'), 'r') as f: return jsonify({"content": f.read()})

@app.route('/api/save_config', methods=['POST'])
def save_config():
    with open(os.path.join(ROOT_DIR, 'config', 'settings.yaml'), 'w') as f: f.write(request.json['content'])
    return jsonify({"status": "saved"})

@app.route('/api/list_prompts')
def list_prompts():
    prompt_dir = os.path.join(ROOT_DIR, 'prompts')
    return jsonify({"files": [f for f in os.listdir(prompt_dir) if f.endswith('.txt')]})

@app.route('/api/get_prompt')
def get_prompt():
    with open(os.path.join(ROOT_DIR, 'prompts', request.args.get('filename')), 'r') as f: return jsonify({"content": f.read()})

@app.route('/api/save_prompt', methods=['POST'])
def save_prompt():
    with open(os.path.join(ROOT_DIR, 'prompts', request.json['filename']), 'w') as f: f.write(request.json['content'])
    return jsonify({"status": "saved"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)