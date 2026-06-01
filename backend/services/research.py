import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor

from services.serper import search_google
from services.agents.scriptwriter import get_model


def _get_depth_config(duration: int) -> tuple:
    if duration <= 30:
        return (3, 4, 200)
    elif duration <= 60:
        return (5, 6, 400)
    elif duration <= 120:
        return (7, 9, 600)
    else:
        return (9, 12, 800)


def _plan_subqueries(topic: str, focus_points: str, num_queries: int) -> list[str]:
    model = get_model()
    if not model:
        return [topic]

    prompt = f"""Bạn là trợ lý nghiên cứu. Hãy phân rã chủ đề sau thành {num_queries} câu truy vấn Google Search khác nhau để thu thập kiến thức toàn diện.

Chủ đề: {topic}
Góc nhìn/trọng tâm user muốn: {focus_points}

Yêu cầu:
- Mỗi query phải bao phủ một khía cạnh khác nhau (vd: giai đoạn, cơ chế, thành phần, thời gian, điều kiện...)
- Query bằng tiếng Việt, ngắn gọn, phù hợp Google Search
- Trả về JSON array of strings, KHÔNG giải thích gì thêm

Ví dụ cho "cây dừa": ["vòng đời cây dừa từ hạt đến ra quả", "cơ chế vận chuyển nước trong thân dừa", "thành phần dinh dưỡng nước dừa", "thời gian hình thành cơm dừa", "điều kiện khí hậu cây dừa phát triển"]

Trả về JSON array:"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        queries = json.loads(text)
        if isinstance(queries, list) and len(queries) > 0:
            return queries[:num_queries]
    except Exception as e:
        print(f"Research planner error: {e}")

    return [topic]


def _search_all_sync(queries: list[str]) -> str:
    results = []
    for q in queries:
        snippet = search_google(q, num_results=8)
        if snippet:
            results.append(f"[Query: {q}]\n{snippet}")
    return "\n\n".join(results)


async def _search_all(queries: list[str]) -> str:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=min(len(queries), 5)) as executor:
        futures = [
            loop.run_in_executor(executor, search_google, q, 8)
            for q in queries
        ]
        snippets = await asyncio.gather(*futures, return_exceptions=True)

    results = []
    for q, snippet in zip(queries, snippets):
        if isinstance(snippet, Exception):
            continue
        if snippet:
            results.append(f"[Query: {q}]\n{snippet}")
    return "\n\n".join(results)


def _synthesize(topic: str, focus_points: str, raw_snippets: str, target_stages: int, max_words: int) -> dict:
    model = get_model()
    if not model:
        return _mock_brief(topic, focus_points, target_stages)

    prompt = f"""Bạn là nhà nghiên cứu nội dung video. Dựa trên dữ liệu tìm kiếm bên dưới, hãy tổng hợp thành một bản tóm tắt có cấu trúc cho video giải trí/giáo dục.

CHỦ ĐỀ: {topic}
TRỌNG TÂM USER MUỐN: {focus_points}
SỐ GIAI ĐOẠN MỤC TIÊU: {target_stages}
ĐỘ DÀI TỐI ĐA: {max_words} từ tổng cộng

DỮ LIỆU TÌM KIẾM:
{raw_snippets}

YÊU CẦU:
- Chia nội dung thành {target_stages} giai đoạn/bước theo trình tự thời gian hoặc logic
- Mỗi giai đoạn có title ngắn gọn + detail 1-3 câu (mức trung bình, không quá học thuật, không quá sơ sài)
- Thêm 3-5 key_facts thú vị (con số, thời gian, so sánh bất ngờ)
- duration_hint: khoảng thời gian thực tế của giai đoạn đó (nếu áp dụng được)

Trả về JSON theo format sau, KHÔNG giải thích gì thêm:
{{
  "topic": "{topic}",
  "summary": "1-2 câu tóm tắt toàn bộ quá trình",
  "stages": [
    {{"id": 1, "title": "Tên giai đoạn", "detail": "Mô tả 1-3 câu", "duration_hint": "khoảng thời gian thực tế"}},
    ...
  ],
  "key_facts": ["fact 1", "fact 2", ...]
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        result = json.loads(text)
        if "stages" in result:
            return result
    except Exception as e:
        print(f"Research synthesizer error: {e}")

    return _mock_brief(topic, focus_points, target_stages)


def _mock_brief(topic: str, focus_points: str, target_stages: int) -> dict:
    stages = []
    for i in range(min(target_stages, 5)):
        stages.append({
            "id": i + 1,
            "title": f"Giai đoạn {i + 1} của {topic}",
            "detail": f"Mô tả chi tiết giai đoạn {i + 1}. {focus_points[:50] if focus_points else ''}",
            "duration_hint": f"{i * 2}-{i * 2 + 3} đơn vị thời gian",
        })
    return {
        "topic": topic,
        "summary": f"Tóm tắt quá trình {topic} (mock data — cần API key để có dữ liệu thật)",
        "stages": stages,
        "key_facts": [
            f"Fact 1 về {topic}",
            f"Fact 2 về {topic}",
            f"Fact 3 về {topic}",
        ],
    }


async def run_research(topic: str, focus_points: str, duration: int) -> dict:
    num_queries, target_stages, max_words = _get_depth_config(duration)

    try:
        queries = _plan_subqueries(topic, focus_points, num_queries)
        raw_snippets = await _search_all(queries)
        brief = _synthesize(topic, focus_points, raw_snippets, target_stages, max_words)
        return brief
    except Exception as e:
        print(f"Research pipeline error: {e}")
        return _mock_brief(topic, focus_points, target_stages)


def run_research_sync(topic: str, focus_points: str, duration: int) -> dict:
    num_queries, target_stages, max_words = _get_depth_config(duration)

    try:
        queries = _plan_subqueries(topic, focus_points, num_queries)
        raw_snippets = _search_all_sync(queries)
        brief = _synthesize(topic, focus_points, raw_snippets, target_stages, max_words)
        return brief
    except Exception as e:
        print(f"Research pipeline error (sync): {e}")
        return _mock_brief(topic, focus_points, target_stages)
