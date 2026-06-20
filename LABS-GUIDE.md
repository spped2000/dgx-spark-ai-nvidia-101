# 📘 LABS GUIDE — คู่มือ Labs ทั้งหมด (master)
DGX Spark · AGICAFET · ทุก lab ทดสอบจริงบนเครื่อง (`spark-4185`, GB10) · bilingual TH/EN

---

## 0) วิธีเข้าใช้งาน (Access)

### บริการ + พอร์ต (เปิดในเบราว์เซอร์ได้)
| บริการ | URL | login / หมายเหตุ |
|---|---|---|
| **JupyterHub portal** (ผู้เรียน) | http://localhost:8888 | username = `student01..30` · รหัส `dgxspark2026` → ได้ **sandbox ของตัวเอง** + โน้ตบุ๊ก |
| **Open WebUI** (แชต) | http://localhost:3000 | แชตกับโมเดลบน DGX Spark (ไม่ต้องโค้ด) |
| **Grafana** (dashboard) | http://localhost:3001 | anonymous → "DGX Spark — vLLM serving" |
| **Phoenix** (traces) | http://localhost:6006 | ดู trace ของ LAB 2/4/5 |
| vLLM API (กลาง) | http://localhost:8000/v1 | model `nemotron-nano` (OpenAI-compatible) |
| NIM API | http://localhost:8002/v1 | model `meta/llama-3.1-8b-instruct` (สตาร์ตเดี่ยวเมื่อโชว์) |
| OpenShell gateway | :8080 | sandbox `lab5-ui` |

### ผู้เรียนเข้าเล่นยังไง
เปิด **http://localhost:8888** → login (`studentXX` / `dgxspark2026`) → ได้ container ส่วนตัว → ใน `~/labs` มีโน้ตบุ๊กให้ **รันเอง (Shift+Enter, no-code)**:
- `00_welcome` (LAB 1 แชต) · `01_lab2_reasoning` (LAB 2) · `02_lab3_optimize_tokens` (LAB 3) · `03_lab4_multiagent` (LAB 4) — ผู้เรียนทำเองในแซนด์บ็อกซ์ตัวเอง
- `04_lab5_secure_watch` (LAB 5) = **ดูผู้สอนสาธิตสด** (OpenShell sandbox ไม่แยกต่อคน)

### ผู้สอน (terminal) — ตั้งครั้งเดียวก่อนเดโม
```bash
cd /home/agicafet/Documents/dgx1/course
export PATH=/tmp/osx/extracted/usr/bin:$PATH          # ให้เจอ openshell (LAB5)
export BASE_URL=http://localhost:8000/v1 MODEL=nemotron-nano
docker ps   # เช็กบริการครบ: vllm-ngc :8000 · phoenix :6006 · grafana :3001 · jupyterhub :8888 · gateway :8080
```

---

## LAB 1 — Serving + "เครื่องเดียว เสิร์ฟทั้งห้อง"
- 🎯 **เอาไว้ทำอะไร:** เข้าใจว่า model ต้องถูก "served" ก่อนใช้ และ DGX Spark เครื่องเดียวรับ 30 คนพร้อมกันได้ด้วย **continuous batching**
- 🔧 **Tools:** vLLM (`:8000`) · Open WebUI (`:3000`) · `sim_30_learners.py` · Grafana (`:3001`)
- 🧠 **Model:** `nemotron-nano` (Nemotron-Nano-8B บน vLLM NGC)
- 🔄 **Flow:** เปิดแชต Open WebUI → ถามได้ → "3-2-1 ยิงพร้อมกัน 30 คน" → ดู Grafana (requests/queue/throughput พุ่ง)
- 🎬 **Scenario:** "กล่องบนโต๊ะนี้ = ChatGPT ส่วนตัวของห้อง ลองถามพร้อมกัน 30 คน เครื่องเดียวจะไหวไหม?" → ไหว (30/30, ~206 tok/s)
- ▶️ **เรียกใช้:**
  ```bash
  # ผู้เรียน: เปิด http://localhost:3000 หรือ :8888 แล้วแชต
  # ผู้สอน (จำลอง 30 คน):
  uv run tools/sim_30_learners.py --users 30 --max-tokens 128
  # เปิด http://localhost:3001 ดูกราฟพุ่งสดๆ
  ```

## LAB 2 — Reasoning Toggle (NeMo vs Nemotron)
- 🎯 **เอาไว้ทำอะไร:** แยก NeMo (โรงงานสร้างโมเดล) vs Nemotron (โมเดล) + เห็น **โหมดคิด on/off** ต่างกัน (ฉลาด↔แพง)
- 🔧 **Tools:** vLLM (`:8000`) · Phoenix project `dgx-spark-lab2` · `lab2_reasoning_demo.py`
- 🧠 **Model:** `nemotron-nano` (เป็น reasoning model)
- 🔄 **Flow:** ส่งคำถามเดียวกัน 2 ครั้ง (`detailed thinking off` → `on`) → เทียบ tokens/latency → ดู Phoenix
- 🎬 **Scenario:** "สั่งให้ AI 'คิดดังๆ ทีละขั้น' vs 'ตอบเลย' แบบไหนคุ้มกว่า?" → ON 600tok/40s (โชว์วิธีคิด) vs OFF สั้น/เร็ว
- ▶️ **เรียกใช้:**
  ```bash
  uv run tools/lab2_reasoning_demo.py        # แล้วดู http://localhost:6006 → project dgx-spark-lab2
  ```

## LAB 3 — Optimize Tokens (Pillar 1)
- 🎯 **เอาไว้ทำอะไร:** ทำให้เร็ว/ถูกลง — quantization (NVFP4/FP8), **prefix/KV cache**, "cost per token = KPI"
- 🔧 **Tools:** vLLM (prefix caching) · `lab3_prefix_cache_demo.py` · Phoenix/Grafana (cost/latency)
- 🧠 **Model:** `nemotron-nano`
- 🔄 **Flow:** ส่ง system prompt ยาว "เดิม" 2 รอบ → วัด TTFT (รอบ 2 = cache hit)
- 🎬 **Scenario:** "ถามคำถามที่ context เดิมซ้ำ ทำไมครั้งที่สองเร็วขึ้นเยอะ?" → TTFT **328→104 ms (−68%)**
- ▶️ **เรียกใช้:**
  ```bash
  uv run tools/lab3_prefix_cache_demo.py
  ```

## LAB 4 — Harnessing / Multi-Agent (Pillar 2)
- 🎯 **เอาไว้ทำอะไร:** agent = LLM + tools เป็นลูป · **multi-agent** = orchestrator สั่ง specialists (ทำงานเป็นทีม)
- 🔧 **Tools:** vLLM (`:8000`) · Phoenix project `dgx-spark-lab4` · `lab4_multiagent_demo.py`
- 🧠 **Model:** `nemotron-nano` (ทุก agent ใช้ตัวเดียวกัน คนละบทบาท)
- 🔄 **Flow:** `orchestrator` แตกงาน → `coding-agent` เขียน `is_prime()` → `reviewer-agent` ชี้ edge case → `final` → ดู span tree ใน Phoenix
- 🎬 **Scenario:** "งานนึงไม่พึ่ง AI ตัวเดียว ให้มันทำงานเป็นทีม: หัวหน้า/คนเขียน/คนตรวจ" → งานดีเพราะมีคนตรวจ
- ▶️ **เรียกใช้:**
  ```bash
  uv run tools/lab4_multiagent_demo.py       # ดู http://localhost:6006 → project dgx-spark-lab4 (กาง trace เห็นทีม)
  ```

## LAB 5 — Secure & Sandbox (NemoClaw + OpenShell, Pillar 3) ⭐
- 🎯 **เอาไว้ทำอะไร:** ปล่อย agent รันคำสั่งเอง = อันตราย → **OpenShell sandbox** คุมด้วย policy (deny-by-default + audit)
- 🔧 **Tools:** OpenShell (gateway `:8080`, sandbox `lab5-ui`, `openshell` CLI + `term` TUI) · Phoenix · `phoenix_sandbox_live.py` · `phoenix_agent_demo.py`
- 🧠 **Model:** `nemotron-nano` (สมอง agent)
- 🔄 **Flow:** ยิง `curl` ใน sandbox → GET ผ่าน/POST โดน 403 (policy_denied L7) → ผู้สอนเพิ่มกฎสด → POST ผ่าน → ดู audit
- 🎬 **Scenario:** "ลองสั่งให้ AI แหกกฎสดๆ — POST/ออกเน็ตมั่ว โดน sandbox บล็อกทันที แล้วเปิดสิทธิ์ทีละกฎ"
- ▶️ **เรียกใช้:**
  ```bash
  # พิมพ์คำสั่งสด → เห็น ALLOWED/BLOCKED ทันที + trace Phoenix
  uv run tools/phoenix_sandbox_live.py
  #   ตัวอย่างพิมพ์: curl -sS https://api.github.com/zen        (✅)
  #                 curl -sS -X POST .../issues -d '{}'         (❌ blocked)
  #                 /ask ลองโพสต์ไป slack                        (agent คิดคำสั่ง)
  # เพิ่มกฎสด (อีก terminal):
  openshell policy update lab5-ui --add-allow 'api.github.com:443:POST:/repos/octocat/hello-world/issues' --wait
  openshell term            # TUI dashboard (sandbox/policy/logs)
  # agent อัตโนมัติ (GTC-style) → Phoenix project dgx-spark-course-agent:
  uv run tools/phoenix_agent_demo.py
  ```
  📄 policy ตั้ง/เพิ่มยังไง: [labs/LAB5-policy-guide.md](labs/LAB5-policy-guide.md)

---

## 🔌 Serving stack (เสริม LAB 1/3) — vLLM · NIM · Triton
- **vLLM** (`:8000`) = ตัวหลัก · **NIM** (`:8002`) = turnkey (one command, auto FP8/GB10) · **Triton dashboard** (`:3001`) = control room
- เทียบตัวเลข + recipe: [serving-stack.md](serving-stack.md) · ⚠️ GPU เดียวรัน heavy server ทีละตัว
- รัน NIM เดี่ยว (โชว์): `docker stop vllm-ngc && docker start nim-llm-demo` → ready → `curl :8002/v1/chat/completions ...` → เสร็จแล้ว `docker stop nim-llm-demo && docker start vllm-ngc`

## 📚 เอกสารเชิงลึก
- [demo-runbook.md](demo-runbook.md) — สคริปต์เดโมสด (hook/scenario/timing/fallback ต่อ lab)
- [lab-tech-reference.md](lab-tech-reference.md) — tools/model/prompt/คำสั่ง ละเอียด
- [tools/lab-demos.md](tools/lab-demos.md) — ดัชนีสคริปต์ต่อ lab · [tools/observability.md](tools/observability.md) — Phoenix/TUI
- [portal/README.md](portal/README.md) — provision 30 บัญชี · [tools/dryrun-report.md](tools/dryrun-report.md) — ผลจริง + recipe
