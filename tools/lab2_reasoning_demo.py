# /// script
# requires-python = ">=3.10"
# dependencies = ["openai>=1.40", "arize-phoenix-otel>=0.6", "openinference-instrumentation-openai>=0.1"]
# ///
"""
LAB 2 — Reasoning toggle (Nemotron): "detailed thinking on" vs "off"
โชว์โมเดลเดียวกัน เปิด/ปิดโหมดคิด → ต่างกันที่ความยาว/เวลา/คุณภาพ. traces → Phoenix 'dgx-spark-lab2'
รัน: BASE_URL=http://localhost:8000/v1 MODEL=nemotron-nano uv run tools/lab2_reasoning_demo.py
"""
import os, time
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000/v1")
MODEL = os.environ.get("MODEL", "nemotron-nano")
tp = register(project_name="dgx-spark-lab2", endpoint=f"{os.environ.get('PHOENIX_ENDPOINT','http://localhost:6006')}/v1/traces")
OpenAIInstrumentor().instrument(tracer_provider=tp)
client = OpenAI(base_url=BASE_URL, api_key="EMPTY")

Q = "รถออกเดินทาง 09:00 ด้วยความเร็วคงที่ 60 กม./ชม. ระยะทาง 150 กม. จะถึงกี่โมง? แสดงวิธีคิด"
for label, sysmsg in [("🟢 thinking OFF", "detailed thinking off"), ("🔵 thinking ON", "detailed thinking on")]:
    t0 = time.perf_counter()
    r = client.chat.completions.create(
        model=MODEL, max_tokens=600, temperature=0.3,
        messages=[{"role": "system", "content": sysmsg}, {"role": "user", "content": Q}])
    dt = time.perf_counter() - t0
    u = r.usage
    ans = r.choices[0].message.content
    print(f"\n===== {label} ({sysmsg}) =====")
    print(f"  completion_tokens={u.completion_tokens}  latency={dt:.1f}s")
    print("  " + ans.strip().replace("\n", "\n  ")[:700])
print("\n[done] เทียบได้: ON สร้าง token เยอะ/ช้ากว่า (โชว์วิธีคิด) · OFF สั้น/เร็ว → Phoenix project 'dgx-spark-lab2'")
