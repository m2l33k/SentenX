import ollama

class LocalLLM:
    def __init__(self):
        pass

    def get_response(self, model_name, system_prompt, user_prompt):
        """
        Sends a prompt to the local Ollama instance.
        """
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]

            print(f"   ... sending to Ollama ({model_name})...")
            
            response = ollama.chat(model=model_name, messages=messages)
            
            return response['message']['content']

        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}. Is 'ollama serve' running?"

if __name__ == "__main__":
    client = LocalLLM()
    print("Testing connection...")
    reply = client.get_response(
        model_name="llama3", 
        system_prompt="You are a helpful assistant.", 
        user_prompt="Say 'Hello World'!"
    )
    print(f"Response: {reply}")