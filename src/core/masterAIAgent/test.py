import requests

# Mixtral test (general assistant)
response = requests.post("http://localhost:8080/chat", json={
    "user_id": "demo_user",
    "input_text": "What is the weather like today?",
    "task_type": "chat"  # 'chat' uses Mixtral
})
print(response.json())
