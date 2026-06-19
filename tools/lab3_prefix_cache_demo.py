# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27"]
# ///
"""
LAB 3 — Optimize Tokens: prefix caching hit (TTFT ลดเมื่อ prefix เดิมถูกแคช)
ส่ง prompt ที่มี system-prompt ยาว "เดิม" 2 รอบ → วัด TTFT: รอบ 2 ควรเร็วกว่า (cache hit)
รัน: BASE_URL=http://localhost:8000/v1 MODEL=nemotron-nano uv run tools/lab3_prefix_cache_demo.py
"""
import os, time, json, httpx

BASE = os.environ.get("BASE_URL", "http://localhost:8000/v1")
MODEL = os.environ.get("MODEL", "nemotron-nano")
# system prompt ยาว (shared prefix) — ยิ่งยาวยิ่งเห็นผล cache ชัด
LONG_CTX = ("You are a DGX Spark workshop assistant. Context: " + ("DGX Spark is a personal AI supercomputer built on the GB10 Grace Blackwell superchip with 128GB unified LPDDR5x memory at ~273 GB/s. " * 25))


def ttft_once(question: str):
    payload = {"model": MODEL, "messages": [
        {"role": "system", "content": LONG_CTX},
        {"role": "user", "content": question}],
        "max_tokens": 32, "temperature": 0.0, "stream": True,
        "stream_options": {"include_usage": True}}
    t0 = time.perf_counter(); ttft = None; ptoks = 0; cached = None
    with httpx.Client(timeout=60) as c:
        with c.stream("POST", f"{BASE}/chat/completions", json=payload) as r:
            for line in r.iter_lines():
                if not line.startswith("data:"):
                    continue
                d = line[5:].strip()
                if d == "[DONE]":
                    break
                try:
                    ch = json.loads(d)
                except Exception:
                    continue
                if ch.get("choices") and ch["choices"][0].get("delta", {}).get("content") and ttft is None:
                    ttft = time.perf_counter() - t0
                if ch.get("usage"):
                    ptoks = ch["usage"].get("prompt_tokens", 0)
                    pd = ch["usage"].get("prompt_tokens_details") or {}
                    cached = pd.get("cached_tokens")
    return ttft or (time.perf_counter() - t0), ptoks, cached


print(f"prefix ยาว ~{len(LONG_CTX)//4} tokens (system prompt เดียวกันทั้ง 2 รอบ)\n")
t1, p1, c1 = ttft_once("สรุป DGX Spark 1 ประโยค")
print(f"รอบ 1 (cold): TTFT={t1*1000:.0f} ms  prompt_tokens={p1}  cached_tokens={c1}")
t2, p2, c2 = ttft_once("สรุป DGX Spark 1 ประโยค (อีกครั้ง)")
print(f"รอบ 2 (warm): TTFT={t2*1000:.0f} ms  prompt_tokens={p2}  cached_tokens={c2}")
if t2 < t1:
    print(f"\n✅ prefix cache hit: TTFT ลด {(1-t2/t1)*100:.0f}% (รอบ 2 เร็วกว่า เพราะ prefix เดิมถูกแคช)")
else:
    print("\nℹ️ TTFT ไม่ลด — ตรวจว่า server เปิด --enable-prefix-caching (vLLM V1 มักเปิด default)")
