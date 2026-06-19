#!/usr/bin/env bash
# run_dryrun.sh — สตาร์ท vLLM (official DGX Spark recipe) แล้วจำลองผู้เรียน 30 คน
# อิง: https://vllm.ai/blog/2026-06-01-vllm-dgx-spark  +  build.nvidia.com/spark/vllm
# สำคัญ: ต้องใช้อิมเมจ CUDA 13 (cu130) เท่านั้น — generic vLLM (cu12x) ไม่มี kernel sm_121 ของ GB10 (จะ hang)
# ใช้: bash tools/run_dryrun.sh   (รันจากโฟลเดอร์ course/)
set -euo pipefail

IMAGE="${IMAGE:-vllm/vllm-openai:cu130-nightly}"      # หรือ NGC: nvcr.io/nvidia/vllm:26.05.post1-py3
MODEL="${MODEL:-nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4}"
SERVED="${SERVED:-nemotron-3-super}"
NAME="${NAME:-vllm-dryrun}"
USERS="${USERS:-30}"
MAXTOK="${MAXTOK:-256}"
MAXSEQS="${MAXSEQS:-4}"        # blog: เกิน 4 บน DGX Spark bandwidth tax กินกำไร batching
MAXLEN="${MAXLEN:-8192}"
PORT="${PORT:-8000}"
HF_CACHE="${HF_CACHE:-$HOME/.cache/huggingface}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"   # course/

echo "==> [1/4] starting vLLM ($IMAGE / $MODEL, max-num-seqs=$MAXSEQS)"
docker rm -f "$NAME" >/dev/null 2>&1 || true
mkdir -p "$HF_CACHE"
docker run -d --name "$NAME" --gpus all --ipc=host -p "${PORT}:8000" \
  -v "${HF_CACHE}:/root/.cache/huggingface" \
  ${HF_TOKEN:+-e HF_TOKEN=$HF_TOKEN} \
  "$IMAGE" \
  "$MODEL" \
    --served-model-name "$SERVED" \
    --trust-remote-code \
    --max-model-len "$MAXLEN" \
    --gpu-memory-utilization 0.85 \
    --max-num-seqs "$MAXSEQS" \
    --reasoning-parser nemotron_v3 \
    --enable-auto-tool-choice \
    --tool-call-parser qwen3_coder

echo "==> [2/4] waiting for /health (NVFP4 download + load + JIT, อาจ 10-20 นาทีครั้งแรก) ..."
for i in $(seq 1 300); do
  if curl -fsS -m3 "http://localhost:${PORT}/health" >/dev/null 2>&1; then echo "    healthy after ~$((i*6))s"; break; fi
  if ! docker ps --format '{{.Names}}' | grep -q "^${NAME}$"; then
    echo "    [FATAL] container exited:"; docker logs --tail 50 "$NAME" 2>&1 | sed 's/\x1b\[[0-9;]*m//g'; exit 2; fi
  sleep 6
done
curl -fsS -m3 "http://localhost:${PORT}/health" >/dev/null 2>&1 || { echo "[FATAL] not healthy in time"; exit 2; }

echo "==> [2.5] pre-warm JIT (กัน ~25s cold-start ของ request แรก)"
curl -s -m120 "http://localhost:${PORT}/v1/chat/completions" -H 'Content-Type: application/json' \
  -d "{\"model\":\"$SERVED\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":8}" >/dev/null || true

echo "==> [3/4] running 30-learner simulation"
cd "$HERE"
uv run tools/sim_30_learners.py \
  --base-url "http://localhost:${PORT}/v1" --model "$SERVED" \
  --users "$USERS" --max-tokens "$MAXTOK" --report tools/dryrun-report.md || true

echo "==> [4/4] done. container '$NAME' ยังรันอยู่. หยุดด้วย: docker rm -f $NAME"
