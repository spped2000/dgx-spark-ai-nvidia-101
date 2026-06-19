# Slides Outline — DGX Spark: AI NVIDIA 101 / Agent Enterprise

> คอร์ส onsite 1 วัน · เสาร์ 20 มิ.ย. 2026 · 10:00–16:00 · Cleverse Rama9 · ~30 คน · no-code · DGX Spark จริง 1 เครื่อง
> สอนโดย NVIDIA Certified Professional · partner: vLLM Singapore
>
> **วิธีอ่านไฟล์นี้:** แต่ละโมดูลมี (1) ชื่อโมดูลเป็นหัวข้ออังกฤษ (slide heading) (2) bullet สไลด์ 5–9 ข้อ — เล่าเป็นภาษาไทย แต่คงศัพท์เทคนิค/ชื่อผลิตภัณฑ์/คำสั่งเป็นอังกฤษ (3) **Key message** 1 ประโยคไทยที่ต้องจำ (4) **Analogy** 1 อันสำหรับคนไม่มีพื้น
>
> **กติกาความถูกต้อง (อ่านก่อนพูด):** เด็คนี้อิง GTC 2026 (forward-dated) → ชื่อ/วันผลิตภัณฑ์ให้พูดว่า "ตามที่ประกาศในงาน". ตัวเลข performance/ราคา = ต้องวัดจริงใน dry-run ก่อนพูด. OpenShell = ALPHA. ห้ามรัน `curl … | bash` สดจาก URL ที่ยังไม่ยืนยัน. certificate = "สอนโดย NVIDIA Certified Professional" ไม่ใช่ออก NVIDIA cert ให้ผู้เรียน.

---

## สไลด์แกน (ฉายเปิดคอร์ส + อ้างกลับทุก pillar)

### Module 0 — "Agent = Model + Harness" (The Spine of the Day)

- วันนี้ทุกอย่างห้อยอยู่บนสมการเดียว: **Agent = Model + Harness** (จาก GTC deck STW61015) — โมเดลคือ "สมอง", Harness คือ "ร่างกาย + กฎ" ที่ทำให้สมองทำงานจริงได้
- **Harness** คือลูปการทำงาน 4 จังหวะ: **CONTEXT → OBSERVE → REASON → ACT** แล้ววนซ้ำ — agent ไม่ใช่ตอบครั้งเดียวจบ แต่ "สังเกต–คิด–ลงมือ" เป็นวง
- รอบลูปนั้นถูกล้อมด้วย 5 ชั้น: **Prompt / Orchestration / Memory / Tools & Skills / Security & Governance** — แต่ละชั้นคือสิ่งที่เราจะแตะในแต่ละ pillar
- แผนที่เชื่อม 3 เสาหลักของวันนี้กับสมการ:
  - **Pillar 1 "Optimize Tokens"** = ฝั่ง cost/latency ของ **Model**
  - **Pillar 2 "Harnessing"** = ตัว **Harness** เอง (ลูป + Tools/Orchestration/Memory)
  - **Pillar 3 "Secure & Sandbox"** = กล่อง **Security & Governance** ที่ครอบ Harness
- 4 หลักคิด **Agent Factory** ที่จะอ้างซ้ำทั้งวัน: (1) **distributed** (2) **data gravity** — เอาโมเดลไปหา data ไม่ใช่ลาก data ออก (3) **security by default** (4) **cost per token = KPI ใหม่**
- ทุกครั้งที่ขึ้น pillar ใหม่ เราจะกลับมาที่สไลด์นี้แล้วชี้ว่า "ตอนนี้เรากำลังแตะชิ้นไหนของสมการ"

> **Key message (TH):** จำสมการเดียวพอ — Agent = Model + Harness; ทุกเรื่องวันนี้คือการปรับชิ้นใดชิ้นหนึ่งของสมการนี้
>
> **Analogy (TH):** Model = พนักงานเก่ง ๆ คนหนึ่ง; Harness = ออฟฟิศ + ขั้นตอนงาน + กฎความปลอดภัย ที่ทำให้พนักงานคนนั้นทำงานให้บริษัทได้จริง ไม่ใช่แค่ฉลาดอยู่คนเดียว

---

## ช่วงเช้า — ปูพื้นฐาน NVIDIA AI Stack

### Module 1 — "What Is This Box?" (DGX Spark Hardware)

- กล่องตรงหน้า = **DGX Spark** สถาปัตยกรรม **GB10** = **Grace ARM CPU + Blackwell GPU** อยู่ในชิปเดียว
- หัวใจคือ **128GB LPDDR5x unified memory** — CPU กับ GPU **ใช้ memory ก้อนเดียวกัน** ไม่ต้องก๊อปข้อมูลไปมา (เร็วและประหยัด)
- สเปกที่ต้องจำ: bandwidth ~**273 GB/s**, compute capability **sm_121**, รองรับ **FP8 / NVFP4** แบบ native, **ไม่มี MIG** (แบ่งการ์ดด้วย container + time-slicing แทน)
- คอขวดจริงของเครื่องนี้คือ **memory bandwidth ไม่ใช่ความจุ** — จำประโยคนี้ไว้ เพราะมันอธิบายทุกอย่างที่เราจะเจอใน lab ช่วงบ่าย
- ภาพสเกล 3 ระดับ: **small (กล่องนี้) → desktop workstation → datacenter cluster** — โค้ดเดียวกันสเกลข้ามได้ เริ่มเรียนรู้ที่กล่องเล็กสุดได้เลย
- จุดเด่นต่อมือใหม่: เครื่องเดียวรันโมเดลใหญ่ระดับ 30B ได้ เพราะ unified memory 128GB เกือบทั้งก้อนเหลือไว้ให้โมเดล + KV cache
- ฉาย dashboard ของเครื่องจริงให้ดูสด — GPU utilization, memory usage — ทุก demo วันนี้รันจากกล่องนี้กล่องเดียว

> **Key message (TH):** DGX Spark = ซูเปอร์คอมพิวเตอร์ AI ขนาดตั้งโต๊ะที่ใช้ memory ก้อนเดียว 128GB ร่วมกัน และคอขวดอยู่ที่ความเร็ว memory ไม่ใช่ความจุ
>
> **Analogy (TH):** unified memory เหมือนครัวที่เชฟ (CPU) กับเตา (GPU) ใช้โต๊ะเตรียมอาหารตัวเดียวกัน ไม่ต้องวิ่งส่งจานข้ามห้อง; แต่ประตูครัว (bandwidth) กว้างเท่าเดิม ถ้าออเดอร์เข้าพร้อมกัน 30 จานก็ต้องต่อคิวที่ประตู

### Module 2 — "Serving Stack: Who Does What, Honestly"

- ปัญหาวันนี้: **30 คนต้องใช้ DGX Spark เครื่องเดียวพร้อมกัน** → ต้องมี serving stack ที่ถูกต้อง ไม่ใช่ให้ทุกคนโหลดโมเดลคนละตัว
- **vLLM = ตัวหลัก (workhorse)** — มี **PagedAttention** + **continuous batching** ทำให้ 1 GPU เสิร์ฟหลายคนพร้อมกันได้ และเป็น **OpenAI-compatible API** (ต่อง่าย)
- **NIM** = endpoint สำเร็จรูปจาก NVIDIA (container เดียวจบ) เป็นทางเลือกแทน vLLM ที่ติดตั้งง่ายกว่า — endpoint เป็น `/v1/chat/completions` พอร์ต 8000
- ส่วนประกอบเสริม (พูดอย่างซื่อสัตย์ว่าอันไหนหลัก อันไหนแค่แนวคิด):
  - **Triton** = dashboard (Prometheus → Grafana) โชว์ metrics สด + โฮสต์หลายโมเดล → supporting
  - **TensorRT-LLM** = engine แรงสุด + จำเป็นต่อ **NVFP4** → demo-concept (build engine มี friction)
  - **NeMo** = ฝั่ง train/customize โมเดล (ไม่เกี่ยว concurrency) → concept
  - **Ray Serve** = router/replica หลาย GPU → บนเครื่องเดียวเป็น concept
  - **NVIDIA Dynamo** = "inference OS" ระดับ datacenter (disaggregated prefill/decode) ต้องมี **GPU ≥ 2** → whiteboard "สเกลขึ้น cluster" เท่านั้น
- คำสั่ง vLLM ตัวอย่าง (ฉายให้เห็น ไม่ต้องพิมพ์เอง):
  ```
  vllm serve <model> --gpu-memory-utilization 0.85 --max-num-seqs 32 \
    --max-model-len 4096-8192 --kv-cache-dtype fp8
  ```
- กฎเหล็กของห้องนี้: **โมเดลเดียวที่แชร์ทั้งห้อง** — ห้ามโหลดโมเดลที่สองพร้อมกัน (OOM + แย่ง bandwidth)

> **Key message (TH):** vLLM คือพระเอกที่ทำให้ GPU ตัวเดียวเสิร์ฟทั้งห้องได้ ส่วน Dynamo คือเรื่องของ cluster หลายการ์ด — วันนี้เราอยู่บนเครื่องเดียว
>
> **Analogy (TH):** vLLM continuous batching เหมือนพนักงานเสิร์ฟเก่ง ๆ ที่รับออเดอร์หลายโต๊ะพร้อมกันแล้วเดินรอบเดียวเสิร์ฟทุกโต๊ะ ไม่ใช่จ้างพนักงาน 30 คนมาเสิร์ฟคนละโต๊ะ (ซึ่งครัวเล็ก ๆ รับไม่ไหว)

### Module 3 — "First Win with LM Studio + Shared Endpoint" (รองรับ LAB 1)

- เป้าหมาย LAB 1: ทุกคน "เห็นของจริง" ใน 5 นาทีแรก — **LM Studio = ChatGPT ส่วนตัวที่รันบน Spark ของเราเอง** ไม่ต้องต่อ cloud
- ติดตั้งแบบ headless ด้วยตัว `llmster` แล้วโหลดโมเดลตัวอย่าง playbook = **Nemotron 3 Nano Omni (~65–70GB)**:
  ```
  curl -fsSL https://lmstudio.ai/install.sh | bash
  lms get nvidia/nemotron-3-nano-omni
  lms load ...
  lms server start --bind 0.0.0.0 --port 1234
  ```
  (GUI: Developer → Serve on Local Network)
- ⚠️ ข้อจำกัดสำคัญ: **LM Link รับได้ ~2 users** → ใช้กับ 30 คนไม่ได้ → ทั้งห้องต้องต่อ **1 shared LAN endpoint** (Open WebUI หน้า vLLM/NIM) ไม่ใช่ต่อ LM Link คนละสาย
- โมเดลที่แชร์จริงทั้งห้อง = **Nemotron Nano (30B-A3B MoE)** หรือคลาส **7–9B**, FP8/NVFP4 — น้ำหนักโมเดลกินไม่กี่ GB เหลือ 128GB ส่วนใหญ่ไว้ทำ KV cache
- **Concurrency demo (ตั้งใจให้ contention เกิด):** นับ 3-2-1 ทุกคนกด Send พร้อมกัน → ดู dashboard เห็น batching รวม ~30 requests + GPU/memory พุ่ง
- ความจุที่คาดหวัง: worst case (30 คนยิงพร้อมกันเป๊ะ) ~**12 tok/s/คน**, ใช้งานจริงแบบ burst ~**30–46 tok/s/คน** (ตัวเลขนี้ต้องยืนยันใน dry-run ก่อนพูดบนเวที)
- สคริปต์ที่ต้องพูดดัง ๆ: "**ช้าลงตอนยิงพร้อมกัน = บทเรียนของ Pillar 1 ไม่ใช่บั๊ก**"

> **Key message (TH):** เครื่องนี้คือ ChatGPT ส่วนตัวของห้อง — และเพราะทุกคนต่อ endpoint เดียวกัน เราจึงเห็นกับตาว่าทรัพยากรถูกแชร์ยังไง
>
> **Analogy (TH):** shared endpoint เหมือนก๊อกน้ำสาธารณะตัวเดียวที่ทุกคนมาต่อท่อ — น้ำไหลแรงตอนคนเดียวเปิด แต่พอเปิดพร้อมกัน 30 คน แรงดันก็ลด นั่นแหละคือบทเรียนเรื่อง bandwidth

### Module 4 — "NeMo vs Nemotron, and Reasoning Toggle" (รองรับ LAB 2)

- แยกคำให้ขาด 3 คำที่มือใหม่มักสับสน:
  - **NeMo** = กล่องเครื่องมือ "สร้าง/ปรับ" โมเดล (train, fine-tune, export)
  - **Nemotron** = ตัวโมเดลจริงที่เรารันเสิร์ฟ
  - **NeMo Guardrails** = ด่านความปลอดภัย (เก็บไว้ใช้ช่วงบ่าย Pillar 3)
- **Nemotron 3 family** (ตามที่ประกาศในงาน — หาได้ที่ build.nvidia.com / huggingface.co/nvidia):
  - **Nano 30B-A3B** — เน้น efficiency + sub-agents (ตัวที่ฟิต Spark + มือใหม่ที่สุด)
  - **Super 120B-A12B** — เน้น throughput + tool calling
  - **Ultra 550B-A55B** — เน้น token efficiency ("ตามที่ประกาศในงาน GTC")
  - variants: **Nano Omni, RAG/Retriever, Speech, Safety**
- **MoE คืออะไร:** ตัวเลข "**A** = active params" — Nano 30B-total แต่ใช้แค่ ~3B active ต่อ token → **เร็วเหมือนโมเดล 3B แต่ฉลาดกว่า** = เหตุผลที่ฟิต DGX Spark
- Reasoning toggle: ส่งคำถามเดียวกันด้วย `/think` กับ `/no_think` → เห็นความต่างระหว่าง "คิดก่อนตอบ" vs "ตอบเลย" (ความแม่นยำ vs ความเร็ว)
- ข้อควรระวังบนเครื่องเดียว: `/think` กับ `/no_think` ใช้ **โมเดลเดิม** — ห้ามโหลดโมเดลที่สอง; จัดเป็น 2 เวฟเพื่อไม่ให้ contention พุ่ง
- เคสจริงให้เห็นภาพ (ตามที่นำเสนอในงาน): **YTL fine-tune Nemotron Nano → ILMU ใน 39 วัน** (MalayMMLU 50→77) แต่มี trade-off (C-MMLU ตก) → "fine-tune ไม่ได้ฟรี มีของแลกเสมอ"

> **Key message (TH):** NeMo คือโรงงานสร้างโมเดล, Nemotron คือโมเดลที่ออกจากโรงงาน; และ MoE ทำให้โมเดลใหญ่วิ่งเร็วเพราะปลุกสมองแค่บางส่วนต่อครั้ง
>
> **Analogy (TH):** MoE (30B-A3B) เหมือนบริษัทที่มีผู้เชี่ยวชาญ 30 คน แต่แต่ละคำถามเรียกมาประชุมแค่ 3 คนที่เกี่ยวข้อง — ได้คำตอบจากทีมใหญ่ในความเร็วของทีมเล็ก

### Module 5 — "A Window into Physical AI" (Jetson Thor + Robotics)

- เปลี่ยนฉากจาก "agent ในเครื่อง" ไปสู่ "AI ที่ขยับของจริงในโลก" — Physical AI
- ฉายคลิปจริงจาก GTC: **G1 humanoid เดินด้วย Reinforcement Learning** สตรีมจาก **Jetson Thor** — สำคัญ: sim ที่ใช้คือ **MuJoCo-Warp ไม่ใช่ Isaac Sim**
- แนวคิดหลัก: **"ภาพ + ประโยคคำสั่ง → คำสั่งมอเตอร์"** — โมเดลแปลโลกที่เห็นเป็นการกระทำ; อ้างถึง **Cosmos Reason 2**
- ภาพใหญ่ Physical AI (อิง STW61026/61028): **"Robotic Factory —sensor data→ AI Factory —tokens→"** — โรงงานหุ่นยนต์ป้อนข้อมูลเซนเซอร์ให้ AI Factory แล้วได้ tokens กลับมา
- 3 ขาของ full-stack: **TRAINING = Vera Rubin / SIM = Omniverse + RTX PRO / INFERENCE = Jetson Thor**
- **Cosmos 3 = World Foundation Model** (มี 4 roles); pipeline **Isaac GR00T**: Collect → Curate → Twin → Simulate → Train+Eval → Deploy
- สเปก **Jetson AGX Thor T5000** (ตามที่ประกาศในงาน): Blackwell, **2070 FP4 TFLOPS**, 14-core Arm, 128GB — ตัวเลข forward/CONFIDENTIAL ให้พูดว่า "ตามที่ประกาศ"
- ⚠️ ความซื่อสัตย์: รูป GTC ชุดนี้ **ไม่มี DGX Spark / Vera Rubin** — ถ้าจะพูด Vera Rubin ให้บอกว่าเป็นข่าวแยก ไม่ใช่จากรูปในมือ

> **Key message (TH):** AI ไม่ได้อยู่แค่ในจอ — แกนเดียวกัน (Model + Harness) ขยับหุ่นยนต์จริงได้ โดยมี sim เป็นสนามซ้อมก่อนลงสนามจริง
>
> **Analogy (TH):** Isaac GR00T pipeline เหมือนการฝึกนักกีฬา: เก็บข้อมูลการเคลื่อนไหว → สร้างฝาแฝดดิจิทัล (digital twin) → ซ้อมในสนามจำลองเป็นล้านรอบ → แล้วค่อยส่งลงสนามจริง

---

## ช่วงบ่าย — 3 เสาหลักของ Agent (ลงมือจริง)

### Module 6 — "Pillar 1: Optimize Tokens — Cost per Token Is the New KPI" (รองรับ LAB 3)

- ย้ำกลับสไลด์แกน: ตอนนี้เรากำลังปรับ **ฝั่ง cost/latency ของ Model**
- มนตราหลัก: **"Cost per token = KPI ใหม่"** — Blackwell ลด $/token ได้มาก (ตามที่นำเสนอ ~35X) → วัด AI ด้วยต้นทุนต่อ token ไม่ใช่แค่ "ฉลาดแค่ไหน"
- 4 คันโยกที่ปรับได้: **quantization (NVFP4/FP8) · prefix/prompt caching · KV cache · right-sizing** (เลือกโมเดลให้พอดีงาน)
- ⚠️ ข้อเท็จจริงสำคัญ: **NVFP4 ต้องใช้ TensorRT-LLM หรือ NIM เท่านั้น** (vLLM ทั่วไปยังไม่ใช่ทางนั้น) — ระบุชัดบนสไลด์
- **Context Rot — "window ใหญ่ ≠ สมองใหญ่":** ยิ่งยัด context ยาว ความแม่นยำยิ่งตก (f1 73%@256k → 45%@1M) → อย่ายัดทุกอย่างเข้า prompt
- มนตราเรื่องการป้อนข้อมูล: **inline << file reference << var reference** — อย่าแปะข้อความยาวลง prompt ตรง ๆ ให้อ้างไฟล์/ตัวแปรแทน (ถูกกว่า เร็วกว่า สมองโล่งกว่า)
- **Prefix / KV caching demo:** ส่ง prompt ที่มี system prompt เดียวกันซ้ำ → ครั้งที่สองเห็น **prefix cache hit** → TTFT (time-to-first-token) เร็วฮวบ; ดู aggregate vs per-user บน metrics
- ผู้เรียนจดเอง: tok/s + TTFT ก่อน/หลัง cache → เห็นตัวเลขจริงว่า caching ช่วยจริง

> **Key message (TH):** ของถูกที่สุดคือ token ที่ไม่ต้องสร้างใหม่ — quantize ให้เล็ก, แคชให้มาก, อย่ายัด context เกินจำเป็น
>
> **Analogy (TH):** prefix caching เหมือนร้านกาแฟที่จำออเดอร์ประจำของคุณได้ — ครั้งแรกต้องถามทุกอย่าง ครั้งต่อไปชงได้เลย; ส่วน context rot เหมือนอ่านหนังสือ 1000 หน้ารวดเดียว สุดท้ายจำต้นเรื่องไม่ได้

### Module 7 — "Pillar 2: Harnessing — Multi-Agent Orchestration" (รองรับ LAB 4)

- ย้ำกลับสไลด์แกน: ตอนนี้เราอยู่ที่ **ตัว Harness เอง** — ลูป CONTEXT→OBSERVE→REASON→ACT + ชั้น Tools/Orchestration/Memory
- **Agent = LLM + tools เป็นลูป** — ไม่ใช่ถาม-ตอบครั้งเดียว แต่ "คิด → เรียก tool → ดูผล → คิดต่อ" จนงานเสร็จ ("agent ≠ one-shot prompt")
- **Single-agent tool-use (ผู้เรียนรันเอง):** agent ตัวเดียวเรียกเครื่องมือผ่าน **MCP** (Model Context Protocol) — เห็น agent หยิบ tool มาใช้เอง
- **Multi-agent (instructor โชว์):** **orchestrator → coding agent + reviewer agent** ทำงานต่อกัน (แสดงคนละสีให้เห็น delegation ชัด ๆ)
- ข้อควรระวังบนเครื่องเดียว: multi-agent full-loop = contention สูงสุดของวัน → ใช้โมเดลเล็กผ่าน Ollama, จำกัด 2–3 steps, max_tokens 128–256, แบ่งเวฟ/คิว, มี cloud fallback เผื่อช้า
- **อ้างอิงของจริงจาก GTC — AI-Q Open Agent Blueprint** เป็นตัวอย่าง production ของสิ่งที่เราเพิ่งทำมือ:
  - **Intent Router = Nemotron 3 Nano** → Orchestration/Planning → **Researcher = Nemotron 3 Super** → Sandbox + Skills
  - tools ผ่าน **NeMo Agent Toolkit** + **NeMo Retriever RAG** + **MCP** + **Dynamo** priority routing → "50% lower cost with open models"
- **NemoClaw Hermes blueprint** (ตามที่ประกาศ): orchestrator = **Nemotron 3 Ultra**, sub-agents = **Nano**, tools **GitHub/Slack/Outlook** + continual-learning loop (Traces → Feedback → Learning)
- เคสจริง: **coding-agent ผ่าน TDD (MediaTek)** — "เลือกเลขในเมนู = no-code steering"; **Skills Hub ~87,917 skills** → "ไม่ใช่ skill ทุกตัวปลอดภัย" (เปิดทางไป Pillar 3)

> **Key message (TH):** agent ที่ทรงพลังคือ agent ที่ทำงานเป็นทีมและใช้เครื่องมือเป็น ไม่ใช่โมเดลเดี่ยวที่ตอบเก่ง
>
> **Analogy (TH):** multi-agent เหมือนทีมทำงาน: orchestrator = หัวหน้าโปรเจกต์แบ่งงาน, coding agent = คนเขียน, reviewer agent = คนตรวจ — งานออกมาดีเพราะมีคนคอยตรวจ ไม่ใช่คนเดียวทำหมด

### Module 8 — "Pillar 3: Secure & Sandbox — NemoClaw + OpenShell" (รองรับ LAB 5)

- ย้ำกลับสไลด์แกน: ตอนนี้เราอยู่ที่ **กล่อง Security & Governance** ที่ครอบ Harness ทั้งหมด — หลักคิด Agent Factory ข้อ "**security by default**"
- **OpenShell** (github.com/NVIDIA/OpenShell) = runtime แซนด์บ็อกซ์รัน agent อย่างปลอดภัย — **deny-by-default + audit trail**; banner ที่จะเห็นจริง: `OPENSHELL — Shells Wide Shut. v0.0.38 ALPHA`
- **4 policy domains:** **filesystem / network / process / inference** — คุมได้ว่า agent แตะไฟล์ไหน, ต่อเน็ตที่ไหน, รัน process อะไร, เรียกโมเดลตัวไหน
- คำสั่งจริงที่ยืนยันแล้ว (ฉาย/รันแบบเตรียมไว้ ไม่รันสดจาก URL ที่ยังไม่ยืนยัน):
  ```
  curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh
  # หรือ: uv tool install -U openshell
  openshell sandbox create -- claude          # หรือ opencode/codex/copilot
  openshell sandbox create --remote spark --from openclaw
  openshell policy set demo --policy examples/sandbox-policy-quickstart/policy.yaml --wait
  ```
- **The money demo (ลำดับนี้เป๊ะ):**
  1. agent ทำงานปกติได้ (สรุปข้อความ / สร้าง `note.txt`) ✅
  2. ลองออกเน็ตใน sandbox: `curl -sS https://api.github.com/zen` → `curl: (56) Received HTTP code 403 from proxy after CONNECT` ❌ (deny-by-default ทำงาน)
  3. เปิด read-only policy → **GET ผ่าน** ✅ / **POST ถูกบล็อก**: `{"error":"policy_denied","detail":"POST /repos/octocat/hello-world/issues not permitted by policy"}` ❌ + เห็น **audit trail**
- **NeMo Guardrails (เสริม):** ถามปกติ = ALLOWED (เขียว); วาง jailbreak = BLOCKED (แดง) — ใช้โมเดลเดิม self-check (ห้ามโหลด NemoGuard NIM ตัวที่สอง) + ตั้ง **auto re-enable กันลืมเปิดทิ้งไว้**
- แมปกับโปสเตอร์: **สไลด์ OpenShell จาก GTC = diagram บนโปสเตอร์เป๊ะ** — Policy Authoring & Signing → Gateway → Coding/Orchestrator/Specialized agents + Skills/Tools
- **NemoClaw** = reference stack (Nemotron + OpenShell + OpenClaw/Hermes), orchestrator = Nemotron 3 Ultra, sub-agents = Nano. ⚠️ คำสั่ง `curl -fsSL https://nvidia.com/nemoclaw.sh | bash; nemoclaw onboard` จากเด็ค = **URL ยังไม่ยืนยัน → ห้ามรันสดต่อหน้าคน** ใช้คำสั่ง OpenShell ที่ยืนยันแล้วแทน

> **Key message (TH):** agent ที่ปลอดภัยคือ agent ที่ถูกล็อกไว้ก่อน (deny-by-default) แล้วค่อยเปิดสิทธิ์ทีละอย่างพร้อมบันทึกทุกการกระทำ
>
> **Analogy (TH):** OpenShell sandbox เหมือนห้องทำงานที่ประตูล็อกหมดตั้งแต่แรก — agent ทำงานในห้องได้ แต่จะออกไปไหนต้องขอกุญแจทีละดอก (policy) และมีกล้องบันทึก (audit trail) ทุกครั้งที่เปิดประตู

### Module 9 — "Signed Skills: The 7-Stage Supply Chain"

- โยงจาก Pillar 3: **Skills Hub มี ~87,917 skills** → "ไม่ใช่ skill ทุกตัวปลอดภัย" → ต้องมีกระบวนการตรวจก่อนใช้
- **Skill supply chain 7 stages** (github.com/NVIDIA/skills): **Scan → Evaluate → Skill Card → Sign → Catalog → Sync → Enforce**
- จัดกลุ่มเป็น 3 เฟส: **VERIFY** (Scan, Evaluate, Skill Card) → **PUBLISH** (Sign, Catalog, Sync) → **CONSUME** (Enforce)
- จุดสำคัญคือขั้น **Sign** = "signed actions/skills" บนโปสเตอร์ — skill ที่ผ่านการตรวจแล้วถูกเซ็นรับรอง agent ถึงจะหยิบมาใช้ได้
- ขั้น **Enforce** เชื่อมกลับ OpenShell โดยตรง — policy domain **inference** บังคับให้ใช้เฉพาะ skill ที่ผ่าน supply chain นี้
- **Phoenix "Agent Insights":** อ่าน trace จริง (status / cost / latency) — และบรรทัด "**The sandbox has restricted egress, so I can't fetch live web data**" = หลักฐานว่า sandbox ทำงานจริง

> **Key message (TH):** ก่อนปล่อย skill ให้ agent ใช้ ต้องผ่านสายพานตรวจ 7 ขั้น — เซ็นรับรองแล้วเท่านั้นถึงใช้ได้ เหมือนของในร้านที่ผ่าน QC
>
> **Analogy (TH):** 7-stage skill supply chain = ระบบรีวิวของ app store — แอป (skill) ต้องถูกสแกน ประเมิน เซ็นรับรอง ลงแคตตาล็อก ก่อนผู้ใช้ (agent) จะติดตั้งได้ ไม่ใช่ใครก็อัปโหลดแล้วใช้ได้เลย

---

## ช่วงปิดท้าย

### Module 10 — "GTC Taipei 2026 Recap" (รองรับ wrap-up)

- recap board ทำแบบ offline จากรูปจริงที่แอดถ่ายในงาน (3–4 มิ.ย.) — ไม่พึ่งเน็ตสด
- ไทม์ไลน์ 3 ยุค: **ChatGPT (2022) → DeepSeek (2025, reasoning) → OpenClaw (2026, self-evolving agents)**
- **"How to Get Started" — 4 CTA:** **Skills** (github.com/NVIDIA/skills) · **Nemotron 3 Ultra** (build.nvidia.com) · **OpenShell** · **NemoClaw** (build.nvidia.com/blueprints)
- **AI-Q Open Agent Blueprint** = multi-agent research lab (Intent Router=Nano → Researcher=Super → Sandbox+Skills; NeMo Agent Toolkit + RAG + MCP + Dynamo) — ผูกกับ LAB 4
- **OpenShell Secure Runtime + live CLI** = สไลด์เดียวกับ diagram บนโปสเตอร์ (L7 allow-list + restricted egress) — ผูกกับ LAB 5
- **NemoClaw Blueprint for Hermes Agents:** orchestrator=Ultra, sub-agents=Nano, Skills Library + Learning Loop, tools GitHub/Slack/Outlook
- **Physical AI ปิดท้าย:** G1 humanoid (MuJoCo-Warp) + Cosmos Reason 2 — โยงกลับ Module 5
- มุม Sovereign AI: **"Five-Layer Cake — เรียกแค่ API คุณเป็นเจ้าของชั้นไหน?"** (STW61099)
- ⚠️ ความซื่อสัตย์ของ recap: รูปชุดนี้ **ไม่มี DGX Spark / Vera Rubin**; **OpenShell = ALPHA**; "OpenClaw" ไม่ปรากฏในสไลด์ → โฟกัส NemoClaw + OpenShell + Hermes; วัน JetPack 7.2 ในรูปอ่านไม่ออก → อย่าระบุวันเดา

> **Key message (TH):** ทุกอย่างที่เราลงมือทำวันนี้ คือสิ่งที่ NVIDIA เพิ่งประกาศที่ GTC 2026 — เราไม่ได้เรียนของเก่า เราเรียนของที่กำลังเกิด
>
> **Analogy (TH):** recap เหมือนแผนที่หลังจบทริป — ชี้ว่าวันนี้เราเดินผ่านจุดไหนของภาพใหญ่ NVIDIA และจะเดินต่อไปทางไหนได้บ้าง

### Module 11 — "Wrap-Up: Three Pillars + Certificate + Giveaway"

- สรุป 3 เสาหลักกลับสู่สไลด์แกน **Agent = Model + Harness**:
  - **Pillar 1 Optimize Tokens** = ปรับ Model ให้ถูก/เร็ว (cost per token = KPI)
  - **Pillar 2 Harnessing** = สร้าง Harness ให้ agent ทำงานเป็นทีม + ใช้ tools
  - **Pillar 3 Secure & Sandbox** = ครอบทุกอย่างด้วย Security & Governance (deny-by-default + signed skills)
- 4 หลักคิด Agent Factory ที่ใช้ได้จริงตั้งแต่พรุ่งนี้: distributed · data gravity · security by default · cost per token = KPI
- 3 take-home actions (no-code): (1) ลองต่อ shared endpoint แบบ OpenAI-compatible (2) เปิด prefix caching ในงานจริง (3) ห่อ agent ด้วย sandbox policy ก่อน deploy
- **Certificate:** "**สอนโดย NVIDIA Certified Professional**" — ระบุให้ชัดว่าเป็นใบรับรองการเข้าร่วมที่สอนโดยผู้ได้ certified **ไม่ใช่** NVIDIA ออก cert ให้ผู้เรียน
- Giveaway + ถ่ายรูปหมู่ + แบบประเมิน + ช่องทางติดตามต่อ (build.nvidia.com / huggingface.co/nvidia / github.com/NVIDIA)
- ขอบคุณ partner: **vLLM Singapore**

> **Key message (TH):** จบวันนี้คุณไม่ได้แค่ดู demo — คุณได้ลงมือกับ 3 เสาหลักของ agent จริง บนเครื่องจริง และเอากลับไปใช้ต่อได้
>
> **Analogy (TH):** 3 pillars เหมือนขาตั้งกล้อง 3 ขา — ขาดขาใดขาหนึ่ง agent ก็ล้ม: เร็ว/ถูก (tokens) + ทำงานเป็น (harness) + ปลอดภัย (sandbox) ต้องครบถึงตั้งอยู่ได้

---

## สิ่งที่ผู้สอนต้องเช็ค/เติมเองก่อนวันงาน

- **ตัวเลข performance ทั้งหมด** (12 / 30–46 tok/s/คน, TTFT, ~35X $/token, สเปก Jetson Thor) → ต้องวัด/ยืนยันใน dry-run ก่อนพูดบนเวที (แผนระบุว่ายังไม่ยืนยัน)
- **ทุก URL ในคำสั่ง** ต้อง resolve ก่อนวันงาน; **ห้ามรัน `curl … | bash` สดจาก URL ที่ยังไม่ยืนยัน** (โดยเฉพาะ `nvidia.com/nemoclaw.sh`)
- **ชื่อ/วันผลิตภัณฑ์ forward-dated** (Nemotron 3 Ultra "ตามที่ประกาศในงาน GTC", Cosmos 3, Jetson Thor specs) → พูดว่า "ตามที่ประกาศในงาน" เสมอ
- **เลือกโมเดลจริงที่จะเสิร์ฟ** ให้ชัด (Nemotron Nano 30B-A3B vs คลาส 7–9B) + ยืนยันไม่ OOM บน 128GB พร้อม 30 บัญชี
- เตรียม **screenshot/asset offline** ของ dashboard, GTC recap, คลิป G1 humanoid, ผล OpenShell 403/policy_denied เผื่อ demo สด fail
- ใส่ **ตัวเลข OpenShell version จริง** ที่จะใช้วันงาน (เด็คอ้าง v0.0.38 ALPHA — ยืนยันตอน dry-run)
