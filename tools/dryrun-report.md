# DGX Spark — Dry-run results & findings (2026-06-19)
Host: `spark-4185` · NVIDIA **GB10** · 128GB unified · sm_121 · driver 580.142 / CUDA 13.0

## ✅ VALIDATED: 30 concurrent learners on ONE DGX Spark (via Ollama)
- **Serving**: NVIDIA **`nemotron-mini`** (Nemotron 4B) on **Ollama**, OpenAI-compatible `:11434/v1`
- **Load test**: `sim_30_learners.py`, 30 concurrent users × 2 bursts (max_tokens 128)

| scenario | ok/fail | wall | aggregate tok/s | per-user tok/s (p50/p95) | TTFT p50/p95 |
|---|---|---|---|---|---|
| BURST ×30 (3-2-1 พร้อมกัน) | **30/0** | 41.5s | ~79.5 | 81.2 / 82.5 | **22.1s / 39.4s** |
| BURST ×30 รอบ 2 (cache warm) | **30/0** | 38.8s | ~79.7 | 81.4 / 82.7 | 18.8s / 36.3s |

**ไม่ OOM** (โมเดล 4B ~3.4GB บน 121GB). รายงานดิบ: [`dryrun-report-ollama.md`](dryrun-report-ollama.md)

### 🔑 Insight (ใส่ลงคอร์ส)
- เครื่องเดียว **เสิร์ฟ 30 คนพร้อมกันได้จริง (30/30)** — แต่ Ollama default parallelism ต่ำ → **เกิดคิว: คนท้ายๆ รอ ~40 วินาที** กว่าจะได้ token แรก (TTFT) ขณะที่ per-user throughput ~81 tok/s (≈ serialize)
- ตรงกับที่คอร์สสอน: *"30 คนยิงพร้อมกันบนเครื่องเดียว = ต้องมี continuous batching / เพิ่ม parallelism ไม่งั้นเกิดคิว"* → ปรับ `OLLAMA_NUM_PARALLEL` ให้สูงขึ้น หรือใช้ vLLM continuous batching, cap `max_tokens`, right-size โมเดล

## ⚠️ FINDING: generic `vllm/vllm-openai` image แฮงก์บน GB10 (sm_121)
ลอง 4 config — **ทุกตัวแฮงก์ที่ warmup forward pass แรก** (weights โหลดขึ้น GPU แล้ว 15–70GB แต่ log นิ่งหลังเลือก attention backend, ไม่ขึ้น healthy):

| # | image | model | backend | ผล |
|---|---|---|---|---|
| 1 | `vllm/vllm-openai:v0.12.0` (CUDA 12.x) | Llama-Nemotron-Nano-8B | FlashInfer | hang (ไม่มี kernel sm_121) |
| 2 | `vllm/vllm-openai:cu130-nightly` | Nemotron-3-Super-120B-A12B-**NVFP4** | FlashInfer | hang หลัง "Using FLASHINFER" (NVFP4 detect OK) |
| 3 | `cu130-nightly` | Llama-Nemotron-Nano-8B | FlashAttention v2 | hang (FA2 ไม่รองรับ Blackwell sm_121) |
| 4 | `cu130-nightly` | Llama-Nemotron-Nano-8B | **TRITON_ATTN** + enforce-eager | hang เช่นกัน |

→ **สรุป:** ไม่ใช่ปัญหา attention backend — เป็น vLLM community image รัน forward pass แรกบน GB10/sm_121 ไม่ผ่าน (ขณะที่ **Ollama รันได้** เพราะใช้ llama.cpp คนละ code path)

### ✅ คำแนะนำสำหรับ serving stack วันงาน
1. ใช้ **NVIDIA NGC official build** `nvcr.io/nvidia/vllm:<ver>` (ตาม [build.nvidia.com/spark/vllm](https://build.nvidia.com/spark/vllm) — anonymously pullable) ซึ่ง build เฉพาะ DGX Spark — *ยังไม่ได้ทดสอบในรอบนี้ ควรลองใน dry-run จริง*
2. หรือใช้ **Ollama / LM Studio** (ยืนยันแล้วว่ารันบน GB10 ได้) เป็น serving path สำหรับมือใหม่
3. **Gate:** ยืนยัน build vLLM ที่จะใช้จริง + วัดตัวเลขใหม่ ใน dry-run ก่อนวันงานเสมอ

## หมายเหตุ insight ที่ได้ระหว่างทาง (ตรงกับเอกสารคอร์ส)
- vLLM blog (DGX Spark) แนะนำ **`--max-num-seqs 4`** สำหรับ 120B — "เกิน 4 concurrent decode บน Spark bandwidth tax กินกำไร batching" + pre-warm JIT (~25s) → ยืนยันเรื่องคอขวด bandwidth/คิว
- NVFP4 ตรวจจับได้จริงบน cu130 (`Detected ModelOpt NVFP4 checkpoint`) — แค่ติด warmup hang ของ community image
