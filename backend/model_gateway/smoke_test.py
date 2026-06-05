"""
Smoke test cho model_gateway.

KHÔNG cần GEMINI_API_KEY / ECOMDY_API_KEY — chỉ test import + factory routing.
Chạy:
    cd d:\future\backend
    python -m model_gateway.smoke_test
"""

import os
import sys

# Ép fallback về backend không cần SDK ngoài
os.environ.setdefault("MODEL_BACKEND", "legacy")

from model_gateway import current_backend, get_llm, get_video, reset_for_tests


def test_default_backend():
    name = current_backend()
    assert name in ("legacy", "byteplus"), name
    print(f"[OK] current_backend() = {name!r}")


def test_singletons():
    a = get_llm()
    b = get_llm()
    assert a is b, "get_llm() phải là singleton"
    c = get_video()
    d = get_video()
    assert c is d, "get_video() phải là singleton"
    print(f"[OK] singletons: llm={a.provider}, video={c.provider}")


def test_switch_to_byteplus_without_key():
    """Khi bật byteplus mà chưa có key -> backend raise RuntimeError rõ ràng."""
    os.environ["MODEL_BACKEND"] = "byteplus"
    reset_for_tests()
    try:
        get_llm().generate("ping")
        assert False, "Phải raise vì thiếu key"
    except RuntimeError as e:
        assert "BYTEPLUS_SEED2_API_KEY" in str(e)
        print("[OK] thiếu key -> raise RuntimeError rõ ràng")
    finally:
        os.environ["MODEL_BACKEND"] = "legacy"
        reset_for_tests()


def test_invalid_backend_falls_back():
    os.environ["MODEL_BACKEND"] = "khong-ton-tai"
    name = current_backend()
    assert name == "legacy", name
    print(f"[OK] backend không hợp lệ -> fallback {name!r}")
    os.environ["MODEL_BACKEND"] = "legacy"
    reset_for_tests()


if __name__ == "__main__":
    test_default_backend()
    test_singletons()
    test_switch_to_byteplus_without_key()
    test_invalid_backend_falls_back()
    print("\nAll smoke tests passed.")
    sys.exit(0)
