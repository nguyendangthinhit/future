import requests, os

def search_google(keyword: str, num_results: int = 5) -> str:
    """Tìm kiếm Google và trả về tóm tắt kết quả dạng text"""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key or api_key == "your_serper_key_here":
        print("Warning: SERPER_API_KEY is not set. Returning mock search data.")
        return f"- Mock result 1 for {keyword}\n- Mock result 2 for {keyword}"

    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    body = {"q": keyword, "num": num_results, "gl": "vn", "hl": "vi"}
    
    try:
        response = requests.post(url, json=body, headers=headers)
        data = response.json()
        
        results = data.get("organic", [])
        summary = "\n".join([
            f"- {r.get('title', '')}: {r.get('snippet', '')}"
            for r in results[:5]
        ])
        return summary
    except Exception as e:
        print(f"Serper API error: {e}")
        return ""
