import httpx, os, json
from dotenv import load_dotenv
load_dotenv('d:/future/backend/.env')
key = os.getenv('ECOMDY_API_KEY')
res = httpx.get('https://api.ecomdy.co/v1/avatars', headers={'Authorization': f'Bearer {key}'})
data = res.json()['data']

print(f"TỔNG SỐ: {len(data)} avatars\n")
print(f"{'#':<3} {'Tên':<22} {'Giới tính':<10} {'Tuổi':<10} {'Vùng':<18} {'Bối cảnh':<28} {'Ngành'}")
print("-" * 120)

for i, a in enumerate(data):
    def get_tag(tag_type):
        for t in a.get("tag_groups", []):
            if t["tag_type"] == tag_type:
                return ", ".join(t["tags"])
        return "?"
    
    print(f"{i+1:<3} {a['avatar_name']:<22} {get_tag('gender'):<10} {get_tag('age'):<10} {get_tag('region'):<18} {get_tag('scene'):<28} {get_tag('industry')}")

print("\n\nLINK XEM TRƯỚC (Thumbnail):")
print("-" * 80)
for i, a in enumerate(data):
    print(f"{i+1}. {a['avatar_name']}: {a['avatar_thumbnail']}")
