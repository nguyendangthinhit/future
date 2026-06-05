"""Run sample briefs end-to-end and write a demo artifact."""

from __future__ import annotations

import asyncio
import json
import os
import sys

os.environ.setdefault("MODEL_BACKEND", "legacy")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models.brief import Brief
from services.orchestrator import run_full_factory


async def demo(brief_path: str, label: str) -> dict:
    with open(brief_path, "r", encoding="utf-8") as file:
        payload = json.load(file)

    brief = Brief(**payload)
    print(f"\n=== {label} ===")
    print(f"Theme: {brief.theme}")
    print(f"Audience: {brief.audience.segment} ({brief.audience.age})")

    result = await run_full_factory(brief, include_vo=False, include_video=False)
    print(f"Wall: {result['wall_s']}s, Variants: {len(result['variants'])}")
    for variant in result["variants"]:
        score = variant.get("qa", {}).get("score", {})
        print(
            f"  - {variant['variant_id']} ({variant['variant_angle']}): "
            f"total={score.get('total')} hook={score.get('hook')} "
            f"cta={score.get('cta')} passed={variant.get('qa_passed')}"
        )

    return result


async def main() -> None:
    runs = {
        "coffee_genz": await demo(os.path.join(ROOT_DIR, "briefs", "coffee-genz.json"), "Genz Brief"),
        "coffee_millennial_mom": await demo(
            os.path.join(ROOT_DIR, "briefs", "coffee-millennial-mom.json"),
            "Millennial Mom Brief",
        ),
    }

    output_dir = os.path.join(ROOT_DIR, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "demo_briefs.json")
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(runs, file, ensure_ascii=False, indent=2)

    print(f"\nOK: both briefs ran end-to-end. Wrote {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
