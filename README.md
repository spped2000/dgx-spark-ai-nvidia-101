# DGX Spark — AI Nvidia 101 / Agent Enterprise · Facilitator Pack
**AGICAFET · เสาร์ 20 มิ.ย. 2026 · 10:00–16:00 · Cleverse Rama9 · ~30 คน · onsite · 100% no-code**

ชุดเอกสารเตรียมสอนคอร์ส 1 วันสำหรับมือใหม่ ที่ทุก demo รันจาก **DGX Spark จริง 1 เครื่อง** (GB10, 128GB unified) แชร์กัน 30 คนผ่านบัญชีรีโมตที่ pre-provision ไว้ — เนื้อหาสองภาษา (ไทย + ศัพท์/คำสั่งอังกฤษ)

> แกนคอร์ส: **"Agent = Model + Harness"** → เช้าปูพื้นฐาน NVIDIA AI Stack, บ่ายลงมือ 3 เสาหลัก **Optimize Tokens / Harnessing / Secure & Sandbox**, ปิดท้าย GTC Taipei 2026 recap + ของแจก + certificate

> 🔗 **Repo:** https://github.com/spped2000/dgx-spark-ai-nvidia-101 · 🧪 **ทดสอบ live บน DGX Spark จริง (`spark-4185`, GB10) แล้ว:** dry-run 30 คน (Ollama + vLLM NGC) · LAB 5 OpenShell ครบวงจร · Phoenix observability (ดูสรุปด้านล่าง)

---

## 📁 สารบัญไฟล์ (Contents)
| ไฟล์ | ใช้ทำอะไร |
|---|---|
| [agenda.md](agenda.md) | กำหนดการตามเวลา 12 บล็อก (10:00–16:00) + น้ำหนักเวลา |
| [slides-outline.md](slides-outline.md) | Outline สไลด์ 12 โมดูล (bilingual) + key message + analogy |
| [labs/LAB1-serving-lmstudio-concurrency.md](labs/LAB1-serving-lmstudio-concurrency.md) | LM Studio first-win → shared endpoint → "30 คนยิงพร้อมกัน" |
| [labs/LAB2-nemo-nemotron-reasoning.md](labs/LAB2-nemo-nemotron-reasoning.md) | NeMo vs Nemotron + reasoning toggle (MoE) |
| [labs/LAB3-optimize-tokens.md](labs/LAB3-optimize-tokens.md) | Pillar 1: quantization / caching / cost-per-token / Context Rot |
| [labs/LAB4-harnessing-multiagent.md](labs/LAB4-harnessing-multiagent.md) | Pillar 2: multi-agent orchestration + MCP tool-use |
| [labs/LAB5-secure-sandbox-openshell.md](labs/LAB5-secure-sandbox-openshell.md) | Pillar 3: NemoClaw + OpenShell sandbox/policy/audit |
| [runbook.md](runbook.md) | Facilitator runbook นาทีต่อนาที + failure recovery |
| [infra-setup-checklist.md](infra-setup-checklist.md) | เตรียมเครื่อง/โมเดล/เครือข่าย + 🔒 dry-run hard gate |
| [logistics.md](logistics.md) | อีเมลก่อนเรียน, GTC recap, certificate, giveaway, marketing |
| [labs/LAB5-policy-guide.md](labs/LAB5-policy-guide.md) | OpenShell policy & rules: `set` vs `update`, presets, L7 allow/deny + เดโมเพิ่มกฎสด |
| [slides/](slides/) | **deck.pptx (76 สไลด์)** + deck.md (Marp) + slides.json + build_pptx.py |
| [tools/](tools/) | sim_30_learners.py (load test) · dryrun-report*.md (ผลจริง) · run_dryrun.sh · **observability.md** · phoenix_*.py (live demos) |

**ลำดับอ่านแนะนำสำหรับผู้สอน:** README → agenda → runbook → labs (1→5) → infra-setup-checklist → logistics

---

## 🚦 ก่อนวันงาน "ต้องทำ" (Pre-event must-do)
1. 🔒 **Dry-run hard gate (1 วันก่อน)** — 30 บัญชี login + ยิง prompt พร้อมกัน, **วัด tok/s & TTFT จริง**, ยืนยัน **ไม่ OOM**, รันทุก lab ครบ (ดู [infra-setup-checklist.md](infra-setup-checklist.md))
2. **กรอกตัวเลขจริง** ลงช่อง `___` ในทุกไฟล์ (tok/s, TTFT, $/token) — ตัวเลขในเอกสารตอนนี้เป็นช่วงคาดการณ์ (~12 worst / ~30–46 ปกติ) ยังไม่ยืนยัน
3. **ยืนยันทุก URL ว่า resolve จริง** — โดยเฉพาะ NemoClaw `nvidia.com/nemoclaw.sh` ที่ยังไม่ยืนยัน
4. 🔴 **ห้ามรัน `curl … | bash` สดต่อหน้าผู้เรียน** จาก URL ที่ยังไม่ยืนยัน — รันเฉพาะตอน dry-run; วันงานใช้ของที่ติดตั้งไว้แล้ว
5. **ล็อกโมเดลที่แชร์ 1 ตัว** (Nemotron Nano/7–9B FP8/NVFP4) กันคนสลับโหลดตัวที่สอง = OOM
6. **เตรียม asset offline + คลิป/สกรีนช็อตสำรอง** (วิดีโอ Physical AI, GTC recap, ภาพ 403/policy_denied/audit ของ LAB 5)
7. **สรุปถ้อยคำ certificate** (Certificate of Completion โดย AGICAFET — *สอนโดย* NVIDIA Certified Professional, ไม่ใช่ NVIDIA ออก cert ให้ผู้เรียน) + ยืนยันใช้ชื่อ vLLM Singapore ได้

---

## 🧪 ผล Dry-run จริงบน DGX Spark (วัด 2026-06-19) — ดู [tools/dryrun-report.md](tools/dryrun-report.md)
- ✅ **30 คนพร้อมกันบนเครื่องเดียวได้จริง (30/30, ไม่ OOM)** — วัดด้วย [tools/sim_30_learners.py](tools/sim_30_learners.py)
  - **Ollama** (nemotron-mini 4B): aggregate ~80 tok/s · TTFT คนท้ายๆ ~40s (parallelism ต่ำ → เกิดคิว = บทเรียน)
  - **vLLM NGC official** (`nvcr.io/nvidia/vllm`, Nemotron-Nano-8B): **~206 tok/s aggregate** (continuous batching จริง) · TTFT p50 0.22s · GPU 70.6GB → ยืนยัน "vLLM = workhorse"
- ✅ **LAB 5 OpenShell** validated live ครบ 7 step (curl 403 → policy → GET ผ่าน/POST บล็อก L7) + **เพิ่มกฎสด** (`policy update --add-allow` → POST บล็อก→ผ่าน ไม่ต้อง restart)
- ✅ **Phoenix observability** + GTC-style agent trace (tool โดน sandbox บล็อก) + live demo พิมพ์สด → [tools/observability.md](tools/observability.md)
- ⚠️ **Finding:** `vllm/vllm-openai` (community image) **แฮงก์ที่ warmup บน GB10/sm_121** → ใช้ **NGC official build** (ทดสอบแล้วผ่าน) หรือ Ollama/LM Studio + วัดใหม่ใน dry-run เสมอ

## ✅ ข้อเท็จจริงหลัก (Verified quick-reference)
- **DGX Spark** = GB10 (Grace + Blackwell), **128GB LPDDR5x unified @ ~273 GB/s**, sm_121, FP8/NVFP4 native, **ไม่มี MIG** → คอขวด = memory bandwidth
- **Serving**: **vLLM = ตัวหลัก** (OpenAI-compatible, continuous batching) · NIM = ทางเลือกสำเร็จรูป · **Triton** = dashboard/metrics · **TensorRT-LLM** (จำเป็นต่อ NVFP4), **NeMo / Ray / Dynamo** = ระดับแนวคิด/สเกลขึ้น cluster บนเครื่องเดียว
- **NemoClaw + OpenShell** = ของจริงจาก GTC 2026 → เสา Secure & Sandbox; **ภาพ diagram บนโปสเตอร์ = สไลด์ OpenShell** (OpenShell ยัง **ALPHA**)
- **Nemotron 3**: Nano 30B-A3B (เหมาะ Spark/มือใหม่) · Super 120B-A12B · Ultra 550B-A55B (A = active params, MoE)

## ⚠️ Accuracy guardrails (เคารพทุกไฟล์)
- เด็ค GTC 2026 เป็น **forward-dated** → ชื่อ/วันผลิตภัณฑ์พูดว่า **"ตามที่ประกาศในงาน"** ไม่ใช่ของชิปแล้ว
- กรอบ **"DGX Spark เครื่องเดียวต่อ 30 คน" เป็นมุมการสอนของเรา** ไม่ใช่คำแนะนำของ NVIDIA
- **Vera Rubin ไม่อยู่ในรูป GTC ชุดนี้** → ถ้าพูดให้ระบุเป็นข่าวแยก
- ตัวเลข performance/ราคา = **วัด/ยืนยัน offline ก่อน** ค่อยอ้างในสื่อ

## 📚 แหล่งอ้างอิงที่ใช้สร้าง pack นี้
- NVIDIA DGX Spark Playbooks — `github.com/NVIDIA/dgx-spark-playbooks`, `build.nvidia.com/spark/*` (lm-studio, nim-llm, vllm, trt-llm, nvfp4-quantization)
- `github.com/NVIDIA/OpenShell` · `github.com/NVIDIA/NemoClaw` · `github.com/NVIDIA/skills` · `huggingface.co/nvidia`
- รูปจริงจากงาน `ref_nvidia_gtc/` (20 ใบ) + เด็คเซสชัน `ref_nvidia_gtc_pdf/` (8 ไฟล์: STW61015/61023/61026/61028/61029/61050/61064/61099)
