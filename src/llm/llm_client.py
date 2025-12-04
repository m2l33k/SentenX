import os
import ollama
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# Load Env
env_file = find_dotenv(usecwd=True)
if env_file: load_dotenv(env_file)

class LocalLLM:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.client = None
        
        if self.github_token:
            masked = self.github_token[:4] + "..." + self.github_token[-4:]
            print(f"🟢 API Client Ready ({masked})")
            self.client = OpenAI(
                base_url="https://models.inference.ai.azure.com",
                api_key=self.github_token
            )
        else:
            print("🟠 API Client Disabled (No Token)")

    def get_response(self, model_name, system_prompt, user_prompt, force_local=False):
        try:
            # --- STRATEGY 1: GITHUB API (Only if client exists AND not forced local) ---
            if self.client and not force_local:
                real_model = model_name
                
                # Check for GPT-4o
                if "gpt-4o" in model_name.lower(): 
                    real_model = "gpt-4o"
                
                # Determine Role (GPT-4o uses 'system', o1/o3 uses 'developer')
                role_name = "system"
                if real_model.startswith("o1") or real_model.startswith("o3"):
                    role_name = "developer"

                response = self.client.chat.completions.create(
                    messages=[
                        {"role": role_name, "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=real_model,
                    temperature=0.7,
                    max_tokens=4096
                )
                return response.choices[0].message.content

            # --- STRATEGY 2: LOCAL OLLAMA ---
            else:
                clean_model = "llama3.1" # Fallback
                if "mistral" in model_name.lower(): clean_model = "mistral"
                
                messages = [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ]
                response = ollama.chat(model=clean_model, messages=messages)
                return response['message']['content']

        except Exception as e:
            print(f"❌ LLM Error: {e}")
            raise e