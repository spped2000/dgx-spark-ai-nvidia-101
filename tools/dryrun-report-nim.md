# Dry-run report — 2026-06-20 07:10 +07

- **Endpoint**: `http://localhost:8002/v1`
- **Model**: `meta/llama-3.1-8b-instruct`
- **Users (concurrent)**: 30 · **max_tokens**: 64
- **Host**: `spark-4185` (NVIDIA GB10, 128GB unified)

| scenario | ok/fail | wall (s) | aggregate tok/s | per-user tok/s (p50/p95/min) | TTFT p50/p95 (s) | GPU peak (GiB) |
|---|---|---|---|---|---|---|
| BURST x30 (3-2-1 พร้อมกัน) | 30/0 | 10.2 | 187.9 | 25.7/26.5/25.4 | 2.73/7.67 | 56.9 |
| BURST x30 รอบ 2 (cache warm) | 30/0 | 10.4 | 184.2 | 24.5/26.3/24.0 | 2.78/7.97 | 56.9 |

> วัดด้วย `course/tools/sim_30_learners.py` บน DGX Spark จริง — ใช้แทนค่าประมาณในเอกสารคอร์ส
