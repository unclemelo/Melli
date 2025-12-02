import requests


class LocalLLM:
    def __init__(self, url="http://localhost:1234"):
        self.url = url


    def generate(self, prompt: str, timeout=30):
    # Minimal compatible with OpenAI-like response schema
        payload = {
            "model": "local-model",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512
        }
        r = requests.post(f"{self.url}/v1/chat/completions", json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]