import requests
import json

# Login (usa username, não email)
login_url = "http://localhost:8888/api/v1/auth/login"
login_data = {
    "username": "admin@sanarispro.com",
    "password": "Admin@123"
}

print("🔐 Fazendo login...")
response = requests.post(login_url, data=login_data)  # Usar data, não json
if response.status_code == 200:
    token = response.json()["access_token"]
    print("✅ Login realizado!")
    
    # Criar canal
    channel_url = "http://localhost:8888/api/chat/channels"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    channel_data = {
        "name": "Geral",
        "description": "Canal geral da clínica",
        "channel_type": "group",
        "sector": "Geral",
        "participant_ids": []
    }
    
    print("📢 Criando canal...")
    response = requests.post(channel_url, headers=headers, json=channel_data)
    
    if response.status_code == 200:
        print("✅ Canal criado com sucesso!")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erro ao criar canal: {response.status_code}")
        print(response.text)
else:
    print(f"❌ Erro no login: {response.status_code}")
    print(response.text)
