# Dry-run report — 2026-06-19 19:52 +07

- **Endpoint**: `http://localhost:11434/v1`
- **Model**: `nemotron-mini`
- **Users (concurrent)**: 30 · **max_tokens**: 128
- **Host**: `spark-4185` (NVIDIA GB10, 128GB unified)

| scenario | ok/fail | wall (s) | aggregate tok/s | per-user tok/s (p50/p95/min) | TTFT p50/p95 (s) | GPU peak (GiB) |
|---|---|---|---|---|---|---|
| BURST x30 (3-2-1 พร้อมกัน) | 30/0 | 41.5 | 79.5 | 81.2/82.5/79.0 | 22.15/39.39 | n/a |
| BURST x30 รอบ 2 (cache warm) | 30/0 | 38.8 | 79.7 | 81.4/82.7/79.7 | 18.81/36.32 | n/a |

> วัดด้วย `course/tools/sim_30_learners.py` บน DGX Spark จริง — ใช้แทนค่าประมาณในเอกสารคอร์ส
