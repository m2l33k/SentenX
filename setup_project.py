import os
def create_structure():
    structure = [
        "config",
        "prompts",
        "src",
        "src/agents",
        "src/llm",
        "src/arena",
        "src/sandbox",
        "src/judge",
        "output/battle_logs",
        "output/generated_code",
        "tests"
    ]

    files = [
        ".env",
        "requirements.txt",
        "main.py",
        "config/agents_config.yaml",
        "src/__init__.py",
        "src/agents/__init__.py",
        "src/llm/__init__.py",
        "src/arena/__init__.py",
        "src/judge/__init__.py"
    ]
    for folder in structure:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Created folder: {folder}")

    # Create Files
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                pass 
            print(f"📄 Created file: {file}")
        else:
            print(f"⚠️ File exists (skipped): {file}")
if __name__ == "__main__":
    create_structure()
    print("\n🚀 Project Structure is ready!")