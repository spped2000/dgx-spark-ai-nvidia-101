# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "openai>=1.40",
#   "arize-phoenix-otel>=0.6",
#   "openinference-instrumentation-openai>=0.1",
# ]
# ///
"""
phoenix_chat_live.py — แชตสดในเทอร์มินอล แล้วทุกข้อความโผล่ใน Phoenix แบบ real-time
(เหมาะกับ live demo: พิมพ์ → ดูคำตอบสตรีม → สลับไปหน้า Phoenix เห็น trace ใหม่ทันที)

ต้องมี: Phoenix(:6006) + endpoint LLM (vLLM NGC :8000 หรือ Ollama :11434)
รันสด (ในเทอร์มินอลคุณ):
  PATH=$HOME/.local/bin:$PATH \
    uv run /home/agicafet/Documents/dgx1/course/tools/phoenix_chat_live.py
ออก: พิมพ์ exit / quit / Ctrl-D
"""
import os, sys

from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI

PHOENIX = os.environ.get("PHOENIX_ENDPOINT", "http://localhost:6006")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000/v1")   # vLLM NGC; Ollama=http://localhost:11434/v1
MODEL = os.environ.get("MODEL", "nemotron-nano")                     # Ollama=nemotron-mini
PROJECT = os.environ.get("PROJECT", "dgx-spark-live")

tp = register(project_name=PROJECT, endpoint=f"{PHOENIX}/v1/traces")
OpenAIInstrumentor().instrument(tracer_provider=tp)
client = OpenAI(base_url=BASE_URL, api_key="EMPTY")

print(f"\n  LLM: {MODEL} @ {BASE_URL}")
print(f"  Phoenix: {PHOENIX}  → project '{PROJECT}'  (เปิดทิ้งไว้ดู trace โผล่สดๆ)")
print("  พิมพ์ข้อความแล้ว Enter — ทุกข้อความ = 1 trace ใน Phoenix. ออก: exit / Ctrl-D\n")

history = [{"role": "system",
            "content": "You are a helpful NVIDIA DGX Spark workshop assistant. Answer concisely in the user's language."}]

while True:
    try:
        msg = input("คุณ> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nbye 👋"); break
    if not msg:
        continue
    if msg.lower() in ("exit", "quit", "ออก"):
        print("bye 👋"); break
    history.append({"role": "user", "content": msg})
    try:
        stream = client.chat.completions.create(
            model=MODEL, messages=history, max_tokens=400, temperature=0.6, stream=True)
        print("AI > ", end="", flush=True)
        full = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                tok = chunk.choices[0].delta.content
                print(tok, end="", flush=True); full += tok
        print(f"\n  ↳ trace → Phoenix '{PROJECT}'\n")
        history.append({"role": "assistant", "content": full})
    except Exception as e:  # noqa: BLE001
        print(f"\n  [error] {type(e).__name__}: {e}\n", file=sys.stderr)
        history.pop()
