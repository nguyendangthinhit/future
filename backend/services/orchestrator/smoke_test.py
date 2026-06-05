"""
Smoke test cho Content Factory pipeline (không cần API key thật).

Chạy:
    cd d:\future\backend
    python -m services.orchestrator.smoke_test
"""

import asyncio
import json
import os
import sys


async def main() -> int:
    # Tắt LLM judge trong QA để không gọi model
    os.environ.setdefault("MODEL_BACKEND", "legacy")
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from models.brief import Brief
    from services.orchestrator import run_full_factory

    brief = Brief(
        theme="Cà phê sữa đá Việt Nam cho giới trẻ gen-z",
        brand={
            "name": "Highlands Coffee",
            "toneOfVoice": "vui tươi, trẻ trung, relatable",
            "palette": {"primary": "#8B4513", "accent": "#FFD700", "bg": "#FFFFFF"},
            "fonts": {"display": "Montserrat", "body": "Inter"},
            "logoUrl": None,
            "voiceId": None,
            "claimsAllowed": ["tươi mỗi ngày"],
            "claimsForbidden": ["chữa khỏi", "100% hiệu quả"],
        },
        audience={"segment": "gen-z", "age": "18-25", "locale": "vi-VN"},
        platform="tiktok",
        constraints={
            "lengthSec": 20,
            "aspect": ["9:16"],
            "mustInclude": ["cà phê sữa đá"],
            "mustAvoid": ["thuốc lá"],
        },
        variantsTarget=2,
    )

    print(">> Running factory with brief:", brief.theme)
    result = await run_full_factory(brief, include_vo=False, include_video=False)
    print(f">> Done in {result.get('wall_s')}s")
    print(f">> Variants: {len(result.get('variants', []))}")
    for v in result.get("variants", []):
        qa = v.get("qa", {})
        score = qa.get("score", {})
        print(
            f"   - {v['variant_id']} ({v.get('variant_angle','')}): "
            f"hook={score.get('hook')} cta={score.get('cta')} "
            f"total={score.get('total', 'n/a')} passed={v.get('qa_passed')}"
        )
    print(">> Trace agents:", [ev["agent"] for ev in result.get("trace", [])])
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
