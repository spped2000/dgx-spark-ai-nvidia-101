# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27"]
# ///
"""
sim_30_learners.py — จำลองผู้เรียน 30 คนยิงเข้า OpenAI-compatible endpoint พร้อมกัน
(ใช้กับ DGX Spark dry-run: วัด TTFT, tokens/sec, p50/p95, success rate, GPU mem peak)

ตัวอย่าง:
  uv run sim_30_learners.py --base-url http://localhost:8000/v1 --model nvidia/Llama-3.1-Nemotron-Nano-8B-v1 \
      --users 30 --max-tokens 256 --report tools/dryrun-report.md

ทุก request เป็น streaming + stream_options.include_usage จึงได้ completion_tokens จริงจาก server.
GPU memory peak เก็บจาก nvidia-smi ระหว่างรัน (best-effort).
"""
import argparse, asyncio, json, time, statistics, subprocess, sys, os
from datetime import datetime, timezone

import httpx

DEFAULT_PROMPT = "อธิบายว่า DGX Spark คืออะไรแบบสั้น ๆ ให้คนเริ่มต้นเข้าใจใน 3 ประโยค"
SYSTEM_PROMPT = "You are a helpful teaching assistant for an NVIDIA DGX Spark beginner workshop. Answer concisely."


async def one_request(client, base_url, model, prompt, max_tokens, idx):
    """ยิง 1 request แบบ streaming, คืน dict ผล (ttft, latency, tokens, ok)."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"[learner {idx}] {prompt}"},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    t0 = time.perf_counter()
    ttft = None
    completion_tokens = 0
    text_chars = 0
    try:
        async with client.stream("POST", f"{base_url}/chat/completions", json=payload) as r:
            if r.status_code != 200:
                body = (await r.aread()).decode("utf-8", "replace")[:300]
                return {"idx": idx, "ok": False, "error": f"HTTP {r.status_code}: {body}"}
            async for line in r.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line[len("data:"):].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = chunk.get("choices") or []
                if choices:
                    delta = choices[0].get("delta", {})
                    piece = delta.get("content") or ""
                    if piece:
                        if ttft is None:
                            ttft = time.perf_counter() - t0
                        text_chars += len(piece)
                usage = chunk.get("usage")
                if usage and usage.get("completion_tokens"):
                    completion_tokens = usage["completion_tokens"]
        total = time.perf_counter() - t0
        if ttft is None:
            ttft = total
        # ถ้า server ไม่ส่ง usage ให้ประมาณ token จากความยาวข้อความ (~4 chars/token)
        if completion_tokens == 0 and text_chars:
            completion_tokens = max(1, text_chars // 4)
        gen_time = max(1e-6, total - ttft)
        return {
            "idx": idx, "ok": True, "ttft": ttft, "latency": total,
            "completion_tokens": completion_tokens, "tok_s": completion_tokens / gen_time,
        }
    except Exception as e:  # noqa: BLE001
        return {"idx": idx, "ok": False, "error": f"{type(e).__name__}: {e}"}


def gpu_mem_used_mib():
    # GB10 unified memory: --query-gpu=memory.used มัก return [N/A] → ใช้ผลรวม per-process แทน
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-compute-apps=used_memory", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip().splitlines()
        vals = [int(x) for x in out if x.strip().isdigit()]
        if vals:
            return sum(vals)
    except Exception:  # noqa: BLE001
        pass
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip().splitlines()
        vals = [int(x) for x in out if x.strip().isdigit()]
        return max(vals) if vals else None
    except Exception:  # noqa: BLE001
        return None


async def gpu_sampler(stop_evt, peaks):
    while not stop_evt.is_set():
        m = gpu_mem_used_mib()
        if m is not None:
            peaks.append(m)
        try:
            await asyncio.wait_for(stop_evt.wait(), timeout=0.5)
        except asyncio.TimeoutError:
            pass


def pctl(values, p):
    if not values:
        return 0.0
    return statistics.quantiles(values, n=100)[min(p, 99) - 1] if len(values) > 1 else values[0]


async def run_burst(client, args, label):
    """ยิง users requests พร้อมกัน (เบิร์สต์ 3-2-1) แล้วสรุปผล."""
    stop_evt = asyncio.Event()
    peaks = []
    sampler = asyncio.create_task(gpu_sampler(stop_evt, peaks))
    wall0 = time.perf_counter()
    tasks = [one_request(client, args.base_url, args.model, args.prompt, args.max_tokens, i)
             for i in range(args.users)]
    results = await asyncio.gather(*tasks)
    wall = time.perf_counter() - wall0
    stop_evt.set()
    await sampler
    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    ttfts = sorted(r["ttft"] for r in ok)
    toks = sorted(r["tok_s"] for r in ok)
    total_completion = sum(r["completion_tokens"] for r in ok)
    summary = {
        "label": label, "users": args.users, "ok": len(ok), "failed": len(bad),
        "wall_s": wall,
        "aggregate_tok_s": total_completion / wall if wall else 0,
        "ttft_p50": pctl(ttfts, 50), "ttft_p95": pctl(ttfts, 95),
        "toks_p50": pctl(toks, 50), "toks_p95": pctl(toks, 95),
        "toks_min": min(toks) if toks else 0, "toks_max": max(toks) if toks else 0,
        "gpu_peak_mib": max(peaks) if peaks else None,
        "errors": [b["error"] for b in bad][:5],
    }
    return summary


def print_summary(s):
    print(f"\n===== {s['label']} =====")
    print(f"  users={s['users']}  ok={s['ok']}  failed={s['failed']}  wall={s['wall_s']:.1f}s")
    print(f"  aggregate throughput : {s['aggregate_tok_s']:.1f} tok/s")
    print(f"  per-user tok/s       : p50={s['toks_p50']:.1f}  p95={s['toks_p95']:.1f}  min={s['toks_min']:.1f}  max={s['toks_max']:.1f}")
    print(f"  TTFT (s)             : p50={s['ttft_p50']:.2f}  p95={s['ttft_p95']:.2f}")
    if s["gpu_peak_mib"] is not None:
        print(f"  GPU mem peak         : {s['gpu_peak_mib']} MiB ({s['gpu_peak_mib']/1024:.1f} GiB)")
    if s["errors"]:
        print(f"  sample errors        : {s['errors']}")


def write_report(path, args, summaries):
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines = [
        f"# Dry-run report — {now}",
        "",
        f"- **Endpoint**: `{args.base_url}`",
        f"- **Model**: `{args.model}`",
        f"- **Users (concurrent)**: {args.users} · **max_tokens**: {args.max_tokens}",
        f"- **Host**: `{os.uname().nodename}` (NVIDIA GB10, 128GB unified)",
        "",
        "| scenario | ok/fail | wall (s) | aggregate tok/s | per-user tok/s (p50/p95/min) | TTFT p50/p95 (s) | GPU peak (GiB) |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in summaries:
        gpu = f"{s['gpu_peak_mib']/1024:.1f}" if s["gpu_peak_mib"] is not None else "n/a"
        lines.append(
            f"| {s['label']} | {s['ok']}/{s['failed']} | {s['wall_s']:.1f} | {s['aggregate_tok_s']:.1f} | "
            f"{s['toks_p50']:.1f}/{s['toks_p95']:.1f}/{s['toks_min']:.1f} | {s['ttft_p50']:.2f}/{s['ttft_p95']:.2f} | {gpu} |"
        )
    lines += ["", "> วัดด้วย `course/tools/sim_30_learners.py` บน DGX Spark จริง — ใช้แทนค่าประมาณในเอกสารคอร์ส", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n[report] เขียนผลลง {path}")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.environ.get("BASE_URL", "http://localhost:8000/v1"))
    ap.add_argument("--model", default=os.environ.get("MODEL", "nemotron-3-super"))
    ap.add_argument("--users", type=int, default=30)
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--prompt", default=DEFAULT_PROMPT)
    ap.add_argument("--api-key", default=os.environ.get("API_KEY", "EMPTY"))
    ap.add_argument("--report", default="tools/dryrun-report.md")
    args = ap.parse_args()

    headers = {"Authorization": f"Bearer {args.api_key}"}
    limits = httpx.Limits(max_connections=args.users + 5, max_keepalive_connections=args.users + 5)
    timeout = httpx.Timeout(connect=10.0, read=180.0, write=30.0, pool=10.0)
    async with httpx.AsyncClient(headers=headers, limits=limits, timeout=timeout) as client:
        print(f"[warm-up] single request to {args.base_url} ({args.model}) ...")
        warm = await one_request(client, args.base_url, args.model, args.prompt, args.max_tokens, -1)
        if not warm["ok"]:
            print(f"[FATAL] warm-up failed: {warm['error']}", file=sys.stderr)
            sys.exit(2)
        print(f"[warm-up] ok: ttft={warm['ttft']:.2f}s tok/s={warm['tok_s']:.1f}")

        summaries = []
        summaries.append(await run_burst(client, args, f"BURST x{args.users} (3-2-1 พร้อมกัน)"))
        print_summary(summaries[-1])
        # รอบสองทันทีหลังรอบแรก = วัด prefix-cache hit (system prompt เดิม)
        summaries.append(await run_burst(client, args, f"BURST x{args.users} รอบ 2 (cache warm)"))
        print_summary(summaries[-1])

    write_report(args.report, args, summaries)
    failed = sum(s["failed"] for s in summaries)
    print(f"\n[done] total failed={failed}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    asyncio.run(main())
