# 🚦 Serving Stack บน DGX Spark — vLLM · NIM · Triton · Ollama (validated จริง)
ทดสอบรันจริงบน `spark-4185` (GB10, 121GB) · 30 คนพร้อมกัน · 2026-06-19/20

## เทียบตัวเลขจริง (30 concurrent users, sim_30_learners.py)
| Engine | โมเดล | aggregate | per-user | TTFT p50 | GPU | จุดเด่น |
|---|---|---|---|---|---|---|
| **vLLM (NGC official)** `:8000` | Nemotron-Nano-8B | **~206 tok/s** | 14 | 0.22s | 70.6GB | ยืดหยุ่นสุด, คุม args ได้ละเอียด — ✅ ตัวหลักของคอร์ส |
| **NIM (turnkey)** `:8002` | llama-3.1-8b (FP8) | ~188 tok/s | 26 | 2.7s | 56.9GB | **one command** auto-เลือก GB10/FP8/vLLM profile เอง |
| **Ollama** `:11434` | nemotron-mini 4B | ~80 tok/s | 81 | ~40s* | 3.4GB | เบา/ติดตั้งง่าย; default parallelism ต่ำ → เกิดคิว |
| **Triton** (metrics) `:3001` | — | — | — | — | — | **control room**: Prometheus+Grafana dashboard "watch 30 of us" |
\* Ollama TTFT สูงเพราะ parallelism ต่ำ (serialize) — เพิ่ม `OLLAMA_NUM_PARALLEL` ได้

## เลือกตัวไหน?
- **vLLM** — production/ยืดหยุ่น, คุม quantization/batching เอง (NVFP4 ต้อง vLLM/TRT-LLM)
- **NIM** — เร็วสุดในการ deploy (turnkey, optimized, OpenAI-compatible) เหมาะมือใหม่/PoC — *ใช้ NGC API key + ดึงจาก nvcr.io/nim*
- **Triton** — เมื่อต้องการ metrics/observability + โฮสต์หลายโมเดล (dashboard) — NIM/vLLM expose Prometheus metrics เหมือนกัน
- **Ollama / LM Studio** — เบาสุด เดโม/เครื่องเล็ก

## ⚠️ บทเรียนสำคัญ: GPU เดียว = heavy server ทีละตัว
- vLLM ครอง 72GB → NIM ขอ 60GB → **ชน (start ไม่ได้)**. รัน heavy LLM server **ทีละตัว** หรือ **แบ่ง `gpu_memory_utilization`** ให้แต่ละตัว (เช่น 0.3 + 0.3)
- ในคอร์ส: เลือก serving engine **1 ตัว** ต่อวันงาน (แนะนำ vLLM NGC) — NIM/Triton โชว์เป็นทางเลือก/สลับเดโม

## คำสั่งสตาร์ตจริง (recipe)
```bash
# vLLM (NGC official — ตัวหลัก)
docker run -d --name vllm-ngc --gpus all --ipc=host -p 8000:8000 -e HF_TOKEN=... \
  -v ~/.cache/huggingface:/root/.cache/huggingface nvcr.io/nvidia/vllm:26.05.post1-py3 \
  vllm serve nvidia/Llama-3.1-Nemotron-Nano-8B-v1 --served-model-name nemotron-nano \
  --max-model-len 4096 --gpu-memory-utilization 0.6 --max-num-seqs 16 --enforce-eager

# NIM (turnkey — ต้อง NGC key; รันตอน GPU ว่าง)
echo "$NGC_API_KEY" | docker login nvcr.io -u '$oauthtoken' --password-stdin
docker run -d --name nim-llm-demo --gpus all --shm-size=16GB -e NGC_API_KEY=$NGC_API_KEY \
  -v ~/.cache/nim:/opt/nim/.cache -p 8002:8000 \
  nvcr.io/nim/meta/llama-3.1-8b-instruct-dgx-spark:latest

# Triton-style dashboard (Prometheus+Grafana scrape vLLM metrics)
cd tools/monitoring && docker compose up -d        # → http://localhost:3001
```
ดูตัวเลขดิบ: `tools/dryrun-report.md` (vLLM/Ollama) · `tools/dryrun-report-ngc.md` · `tools/dryrun-report-nim.md`
