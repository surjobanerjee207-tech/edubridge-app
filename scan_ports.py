import requests

ports = [1234, 11434, 8000, 8080, 5000, 1235, 1236]
for port in ports:
    try:
        url = f"http://localhost:{port}/v1/models"
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            print(f"FOUND OpenAI-compatible API on port {port}")
            exit(0)
    except:
        pass
    
    try:
        url = f"http://localhost:{port}/api/tags" # Ollama style
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            print(f"FOUND Ollama-compatible API on port {port}")
            exit(0)
    except:
        pass

print("No local AI server found on common ports.")
