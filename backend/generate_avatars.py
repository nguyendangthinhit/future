import httpx, os, json
from dotenv import load_dotenv

load_dotenv('d:/future/backend/.env')
key = os.getenv('ECOMDY_API_KEY')

res = httpx.get('https://api.ecomdy.co/v1/avatars', headers={'Authorization': f'Bearer {key}'})
data = res.json().get('data', [])

with open('d:/future/backend/services/avatars.py', 'w', encoding='utf-8') as f:
    f.write('AVATARS = ' + json.dumps(data, indent=2, ensure_ascii=False) + '\n\ndef get_all_avatars():\n    return AVATARS\n')
print("avatars.py created successfully")
