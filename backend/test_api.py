import requests

url = "http://127.0.0.1:8000/api/v1/video/create"
data = {
    "video_type": "entertainment",
    "channel": "tiktok",
    "scheduled_date": "2026-06-10",
    "raw_content": "hello",
    "style_id": "1",
    "style_name": "abc",
    "duration": "30",
    "country_code": "VN",
    "use_google_data": "false",
    "search_keyword": ""
}
# Pass files=None to force multipart, wait, passing files={} doesn't.
# We must pass something.
response = requests.post(url, data=data, files={"dummy": ("","")})
print(response.status_code)
# avoid unicode print errors
print(response.text.encode('utf-8'))
