# Dry-run report — 2026-06-20 07:32 +07

- **Endpoint**: `http://localhost:8000/v1`
- **Model**: `nemotron-nano`
- **Users (concurrent)**: 30 · **max_tokens**: 128
- **Host**: `spark-4185` (NVIDIA GB10, 128GB unified)

| scenario | ok/fail | wall (s) | aggregate tok/s | per-user tok/s (p50/p95/min) | TTFT p50/p95 (s) | GPU peak (GiB) |
|---|---|---|---|---|---|---|
| BURST x30 (3-2-1 พร้อมกัน) | 30/0 | 18.4 | 208.8 | 14.3/14.4/14.1 | 0.28/9.37 | 72.1 |
| BURST x30 รอบ 2 (cache warm) | 30/0 | 18.2 | 210.9 | 14.3/14.5/14.3 | 0.19/9.33 | 72.1 |

> วัดด้วย `course/tools/sim_30_learners.py` บน DGX Spark จริง — ใช้แทนค่าประมาณในเอกสารคอร์ส
