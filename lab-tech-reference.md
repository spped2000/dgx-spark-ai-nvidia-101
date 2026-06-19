# 🔧 Lab Tech Reference — ใช้อะไรบ้างในแต่ละ LAB (tools · model · prompt · คำสั่ง)
อ้างอิงจริงจากที่ validate บน DGX Spark `spark-4185` (GB10, 128GB unified, sm_121, CUDA 13, driver 580.142) · 2026-06-19/20

## 🧱 Stack รวม (services/containers ที่ใช้ทั้งคอร์ส)
| บริการ | image / binary | พอร์ต | ใช้ใน |
|---|---|---|---|
| **vLLM (NGC official)** | `nvcr.io/nvidia/vllm:26.05.post1-py3` | `:8000` | LAB 1–4 (สมองหลัก) — ✅ รันได้บน GB10 |
| Ollama | `ollama 0.23.2` (service) | `:11434` | LAB 1 (ทางเลือก/เดโมเร็ว) |
| **Phoenix** (Arize) | `arizephoenix/phoenix:latest` | `:6006` (+OTLP 4317) | LAB 2–5 (observability/trace) |
| **OpenShell** | binary `v0.0.66` (.deb) + gateway `ghcr.io/nvidia/openshell/gateway:latest` | `:8080` | LAB 5 (sandbox/policy) |
| **Open WebUI** | `ghcr.io/open-webui/open-webui:main` | `:3000` | LAB 1 (chat UI ผู้เรียน) |
| รันสคริปต์ | `uv` (PEP723 inline deps) | — | ทุก lab |

**Python deps (ผ่าน uv):** `openai`, `arize-phoenix-otel`, `openinference-instrumentation-openai`, `httpx`, `python-pptx` (สไลด์)
**โมเดลที่ใช้จริง:** `nvidia/Llama-3.1-Nemotron-Nano-8B-v1` (เสิร์ฟชื่อ **`nemotron-nano`** บน vLLM :8000) · `nemotron-mini` (NVIDIA Nemotron 4B บน Ollama) · *(ดาวน์โหลดไว้: `NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4` ตามบล็อก — ช้าสำหรับเดโม)*
> ⚠️ community image `vllm/vllm-openai` แฮงก์บน GB10 → ใช้ **NGC build** เท่านั้น

---

## LAB 1 — Serving + 30 คนพร้อมกัน
| | รายละเอียด |
|---|---|
| **Tools** | vLLM NGC (`:8000`) · Open WebUI (`:3000`) · `tools/sim_30_learners.py` (asyncio+httpx, 30 client, วัด TTFT/tok-s/GPU) |
| **Model** | `nemotron-nano` — vLLM args: `--max-model-len 4096 --gpu-memory-utilization 0.6 --max-num-seqs 16 --enforce-eager` |
| **คำสั่ง** | `BASE_URL=http://localhost:8000/v1 MODEL=nemotron-nano uv run tools/sim_30_learners.py --users 30 --max-tokens 128` |
| **Prompt** | system: *"You are a helpful teaching assistant for an NVIDIA DGX Spark beginner workshop. Answer concisely."* · user: `[learner N] อธิบายว่า DGX Spark คืออะไรแบบสั้นๆ...` |
| **ผู้เรียนทำ** | เปิด Open WebUI พิมพ์แชต (no-code) · ดู dashboard ตอน 30 คนยิงพร้อมกัน |
| **Validated** | 30/30 สำเร็จ · **~206 tok/s aggregate** · TTFT p50 0.22s · GPU 70.6GB ไม่ OOM |
| **Playbook อ้างอิง** | build.nvidia.com/spark: lm-studio (`nemotron-3-nano-omni`), nim-llm, vllm |

## LAB 2 — Reasoning Toggle (NeMo/Nemotron)
| | รายละเอียด |
|---|---|
| **Tools** | vLLM NGC (`:8000`) · Phoenix (project `dgx-spark-lab2`) · `tools/lab2_reasoning_demo.py` |
| **Model** | `nemotron-nano` (เป็น reasoning model) |
| **กลไก** | สลับด้วย **system prompt**: `"detailed thinking on"` vs `"detailed thinking off"` (ไม่ใช่ /think) |
| **คำสั่ง** | `BASE_URL=…:8000/v1 MODEL=nemotron-nano uv run tools/lab2_reasoning_demo.py` |
| **Prompt** | user: *"รถออกเดินทาง 09:00 ความเร็ว 60 กม./ชม. ระยะ 150 กม. ถึงกี่โมง? แสดงวิธีคิด"* (max_tokens 600) |
| **Validated** | OFF ~210 tok / 15s (ตอบ 11:30) · ON ~600 tok / 43s (โชว์วิธีคิด) → trace เทียบใน Phoenix |
| **สอน** | NeMo=โรงงานสร้างโมเดล · Nemotron=โมเดล · MoE active params · reasoning = ฉลาดขึ้นแต่แพง |

## LAB 3 — Optimize Tokens (prefix cache / quantization)
| | รายละเอียด |
|---|---|
| **Tools** | vLLM NGC (`:8000`, prefix caching) · `tools/lab3_prefix_cache_demo.py` (httpx streaming วัด TTFT + prompt_tokens) |
| **Model** | `nemotron-nano` |
| **กลไก** | ส่ง **system prompt ยาว ~843 tokens เดิม 2 รอบ** → วัด TTFT (รอบ 2 = cache hit) |
| **คำสั่ง** | `BASE_URL=…:8000/v1 MODEL=nemotron-nano uv run tools/lab3_prefix_cache_demo.py` |
| **Prompt** | system: *"You are a DGX Spark assistant. Context: DGX Spark is ... (ซ้ำ ×25 ≈ 843 tok)"* · user: *"สรุป DGX Spark 1 ประโยค"* (max_tokens 32) |
| **Validated** | **TTFT 328 ms → 104 ms (−68%)** เมื่อ prefix ถูกแคช |
| **สอน** | quantization NVFP4/FP8 (ต้อง TRT-LLM/NIM) · prefix/KV cache · Context Rot · "cost per token = KPI" |

## LAB 4 — Harnessing / Multi-Agent
| | รายละเอียด |
|---|---|
| **Tools** | vLLM NGC (`:8000`) · Phoenix (project `dgx-spark-lab4`) · `tools/lab4_multiagent_demo.py` (manual OTel spans ต่อ agent) |
| **Model** | `nemotron-nano` (ทุก agent ใช้ตัวเดียวกัน คนละบทบาท) |
| **Agents** | `orchestrator` → `coding-agent` → `reviewer-agent` → `orchestrator (final)` (แต่ละตัว = span kind=AGENT) |
| **คำสั่ง** | `BASE_URL=…:8000/v1 MODEL=nemotron-nano uv run tools/lab4_multiagent_demo.py` |
| **Prompts (system ต่อ agent)** | orchestrator: *"break the task and delegate to a coder then a reviewer"* · coding-agent: *"write ONLY the requested function, clean and correct"* · reviewer: *"list concrete issues/edge-cases (n<2, even, efficiency)"* · task: *"เขียนฟังก์ชัน Python is_prime(n)"* |
| **Validated** | trace `orchestrator-turn` มีลูก coding-agent + reviewer-agent (เห็นทีม) |
| **สอน** | agent = LLM + tools เป็นลูป · multi-agent = orchestrator→specialists · skills/tools (MCP) · NeMo Agent Toolkit / AI-Q blueprint |

## LAB 5 — Secure & Sandbox (NemoClaw + OpenShell)
| | รายละเอียด |
|---|---|
| **Tools** | OpenShell `v0.0.66` (binary + gateway `:8080`) · sandbox **`lab5-ui`** · `openshell` CLI (`sandbox`/`policy`/`term`) · Phoenix (`dgx-spark-sandbox-live`, `dgx-spark-course-agent`) · `tools/phoenix_sandbox_live.py` + `phoenix_agent_demo.py` |
| **Model** | (สมอง agent) `nemotron-nano` บน vLLM `:8000` |
| **Images** | gateway `ghcr.io/nvidia/openshell/gateway:latest` · sandbox base `ghcr.io/nvidia/openshell-community/sandboxes/base:latest` · supervisor `ghcr.io/nvidia/openshell/supervisor:latest` |
| **gateway.toml** | `compute_drivers=["docker"]` · `disable_tls=true` · `[gateway_jwt]` (signing จาก `generate-certs`) · `[auth] allow_unauthenticated_users=true` · publish gateway `0.0.0.0:8080` (ให้ sandbox callback ถึงบน Linux) |
| **policy.yaml** | `network_policies.github_api` → endpoint `api.github.com:443` `protocol: rest` `enforcement: enforce` `access: read-only` · `binaries: /usr/bin/curl` |
| **คำสั่งหลัก** | `openshell sandbox create --name lab5-ui --keep --no-auto-providers` · `openshell policy set/get <sb> --policy policy.yaml` · `openshell policy update <sb> --add-allow host:443:POST:/path` · `openshell term` (TUI) |
| **Demo (in-sandbox)** | `curl https://api.github.com/zen` (GET) · `curl -X POST .../issues` (POST) · `curl https://example.com` (host นอก policy) |
| **Validated** | GET→200 ✅ · POST→`policy_denied` L7 ❌ · example.com→403 ❌ · **add-allow → POST ผ่านสด (ไม่ restart)** · agent trace ใน Phoenix เห็น tool โดน block |
| **สอน** | deny-by-default · policy authoring/signing · sandbox isolation · audit log (OCSF) · signed skills (github.com/NVIDIA/skills) |

---

## สคริปต์ทั้งหมดใน `tools/` (รันด้วย `uv run`)
`sim_30_learners.py` (load test) · `run_dryrun.sh` (serve+sim — ⚠️ อย่ารันถ้ามี vllm-ngc ครอง :8000 อยู่) · `lab2_reasoning_demo.py` · `lab3_prefix_cache_demo.py` · `lab4_multiagent_demo.py` · `phoenix_trace_demo.py` (LLM tracing) · `phoenix_agent_demo.py` (agent+sandbox→Phoenix) · `phoenix_sandbox_live.py` (พิมพ์คำสั่งโดนบล็อกสด) · `phoenix_chat_live.py` (แชตสด) · `build_pptx.py` (สไลด์)
ดู [tools/lab-demos.md](tools/lab-demos.md) (ดัชนีต่อ lab) · [tools/observability.md](tools/observability.md) (Phoenix/TUI) · [tools/dryrun-report.md](tools/dryrun-report.md) (recipe + ผลจริง) · [demo-runbook.md](demo-runbook.md) (สคริปต์เดโมสด)
