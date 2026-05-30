import os
import json
from datetime import datetime

# Nếu muốn crawl thật có thể cài `pytrends`: pip install pytrends
# from pytrends.request import TrendReq

TARGET_COUNTRIES = ["VN", "US", "TH", "ID", "JP", "KR", "PH", "BR", "GB", "IN"]

def fetch_trends_for_countries(countries: list = None):
    """
    Kéo dữ liệu trending cho các quốc gia truyền vào.
    Mặc định hỗ trợ danh sách 10 quốc gia phổ biến.
    """
    if countries is None:
        countries = TARGET_COUNTRIES
        
    print(f"Đang kéo dữ liệu trending cho {len(countries)} quốc gia: {', '.join(countries)}")
    
    # Ở đây chúng ta sẽ giả lập kết quả trả về của Pytrends.
    # Trong thực tế, bạn có thể khởi tạo:
    # pt = TrendReq(hl='en-US', tz=360)
    # top_searches = pt.trending_searches(pn='vietnam') 
    
    topics = []
    
    # Dữ liệu mẫu (Mock data) tượng trưng cho top keywords
    mock_trends = {
        "VN": ["Review quán cafe mới", "Cách giảm cân tại nhà", "Du lịch Đà Lạt"],
        "US": ["Tech news 2026", "Healthy breakfast recipes", "Aesthetic room decor"],
        "TH": ["Món ăn đường phố Thái", "Phim hài Thái Lan", "Mỹ phẩm nội địa Thái"],
        "ID": ["Nasi Goreng review", "Cảnh đẹp Bali", "Mẹo chăm sóc da"],
        "JP": ["Anime mới nhất", "Văn hóa trà đạo", "Công nghệ Robot"],
        "KR": ["Idol Kpop comeback", "Mukbang đồ cay", "Skincare Hàn Quốc"],
        "PH": ["Tiktok dance trend", "Jollibee mukbang", "Du lịch biển"],
        "BR": ["Lễ hội Carnival", "Bóng đá đường phố", "Nhạc Funk thịnh hành"],
        "GB": ["Premier League highlights", "Trà chiều kiểu Anh", "Thời trang London"],
        "IN": ["Phim Bollywood hot", "Món ăn đường phố Ấn", "Cricket news"]
    }
    
    for country in countries:
        trends = mock_trends.get(country, [f"Top trend in {country}"])
        for idx, t in enumerate(trends):
            topics.append({
                "country_code": country,
                "topic": t,
                "rank": idx + 1
            })
            
    # Ghi vào file trending_live.json
    output_path = os.path.join(os.path.dirname(__file__), "../data/trending_live.json")
    
    data = {
        "last_updated": datetime.now().isoformat(),
        "topics": topics
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("Đã cập nhật trending_live.json thành công!")
    return data

if __name__ == "__main__":
    fetch_trends_for_countries()
