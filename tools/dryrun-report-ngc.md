# Dry-run report — 2026-06-19 22:49 +07

- **Endpoint**: `http://localhost:8000/v1`
- **Model**: `nemotron-nano`
- **Users (concurrent)**: 30 · **max_tokens**: 200
- **Host**: `spark-4185` (NVIDIA GB10, 128GB unified)

| scenario | ok/fail | wall (s) | aggregate tok/s | per-user tok/s (p50/p95/min) | TTFT p50/p95 (s) | GPU peak (GiB) |
|---|---|---|---|---|---|---|
| BURST x30 (3-2-1 พร้อมกัน) | 30/0 | 29.0 | 205.5 | 14.0/14.1/13.9 | 0.28/14.82 | 70.6 |
| BURST x30 รอบ 2 (cache warm) | 30/0 | 28.9 | 207.3 | 14.0/14.0/14.0 | 0.22/14.66 | 70.6 |

> วัดด้วย `course/tools/sim_30_learners.py` บน DGX Spark จริง — ใช้แทนค่าประมาณในเอกสารคอร์ส
