# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "openai>=1.40",
#   "arize-phoenix-otel>=0.6",
#   "openinference-instrumentation-openai>=0.1",
# ]
# ///
"""
phoenix_trace_demo.py — ส่ง LLM traces เข้า Phoenix เพื่อดู cost/latency/token ต่อ request
(ใช้คู่กับคอร์ส: LAB 3 Optimize Tokens + หน้าจอ "Agent Insights" แบบในรูป GTC)

ก่อนรัน: Phoenix ต้องรันอยู่ (docker run ... arizephoenix/phoenix) ที่ :6006
รัน: uv run tools/phoenix_trace_demo.py
จากนั้นเปิดเว็บ http://localhost:6006 → เห็น traces เข้ามา
"""
import os, sys

from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI

PHOENIX = os.environ.get("PHOENIX_ENDPOINT", "http://localhost:6006")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:11434/v1")  # Ollama OpenAI-compat
MODEL = os.environ.get("MODEL", "nemotron-mini")
N = int(os.environ.get("N", "6"))

# 1) ลงทะเบียน tracer ชี้ไป Phoenix + auto-instrument OpenAI client
tracer_provider = register(project_name="dgx-spark-course", endpoint=f"{PHOENIX}/v1/traces")
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

client = OpenAI(base_url=BASE_URL, api_key="EMPTY")

PROMPTS = [
    "อธิบาย DGX Spark สั้นๆ",
    "vLLM คืออะไร",
    "NVFP4 ต่างจาก FP8 ยังไง",
    "อธิบาย continuous batching",
    "OpenShell sandbox ทำอะไร",
    "Nemotron Nano คือรุ่นไหน",
]

print(f"[phoenix] ส่ง {N} requests ไป {BASE_URL} ({MODEL}) — trace ไป {PHOENIX}")
for i in range(N):
    p = PROMPTS[i % len(PROMPTS)]
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": f"[{i}] {p}"}],
            max_tokens=80, temperature=0.7,
        )
        u = r.usage
        print(f"  #{i}: ok  prompt={u.prompt_tokens} completion={u.completion_tokens} total={u.total_tokens}")
    except Exception as e:  # noqa: BLE001
        print(f"  #{i}: ERROR {type(e).__name__}: {e}", file=sys.stderr)

print(f"\n[done] เปิด {PHOENIX} → โปรเจกต์ 'dgx-spark-course' เพื่อดู traces (latency, tokens, cost ต่อ request)")
