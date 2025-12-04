from flask import Flask, render_template, request
import os
import json
import sys

# Setup paths (Go up one level to find output folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # /overview
ROOT_DIR = os.path.dirname(BASE_DIR)                  # /code_arena_ai
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output', 'battle_logs')

app = Flask(__name__)

@app.route('/')
def index():
    # 1. Find all JSON files in output/battle_logs
    battles = []
    if os.path.exists(OUTPUT_DIR):
        files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('_data.json')]
        files.sort(reverse=True) # Newest first
        
        for f in files:
            battles.append(f.replace('_data.json', ''))
    
    # 2. Get selected battle (or default to newest)
    selected_id = request.args.get('id')
    current_data = None
    
    if not selected_id and battles:
        selected_id = battles[0]
    
    if selected_id:
        file_path = os.path.join(OUTPUT_DIR, f"{selected_id}_data.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                current_data = json.load(f)

    return render_template('index.html', battles=battles, current_battle=current_data, selected_id=selected_id)

if __name__ == '__main__':
    print(f"👀 Watching folder: {OUTPUT_DIR}")
    app.run(debug=True, port=5000)