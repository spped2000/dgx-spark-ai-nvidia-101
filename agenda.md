# Agenda — DGX Spark: AI NVIDIA 101 / Agent Enterprise (1 วัน · no-code)

> **กำหนดการตามเวลาฉบับเต็ม** สำหรับคอร์ส onsite 1 วัน
> **Event:** เสาร์ 20 มิ.ย. 2026 · **10:00–16:00** · Cleverse Rama9 · ผู้เรียน ~30 คน (เริ่มจากศูนย์ · no-code)
> **Hardware:** DGX Spark จริง **1 เครื่อง** (GB10 Grace Blackwell · 128GB unified memory) — ทุก demo รันจากเครื่องนี้ ผู้เรียนต่อแบบรีโมต
> **Instructor:** NVIDIA Certified Professional · **Partner:** vLLM Singapore

---

## How to read this agenda (วิธีอ่านตารางนี้)

แต่ละบล็อกมีข้อมูลครบ 7 อย่าง เพื่อให้ผู้สอนและทีมงานใช้คุมงานได้ทันที:

- **เวลา (Time):** ช่วงเวลาเป๊ะ ๆ ของบล็อก
- **ชื่อ (Title TH+EN):** ชื่อบล็อกสองภาษา
- **ชนิด (Type):** `reg` (ลงทะเบียน) · `lecture` (บรรยาย) · `lab` (ลงมือทำ) · `demo` (ดูสาธิต) · `break` / `lunch` (พัก) · `wrap` (ปิดท้าย)
- **Goal มือใหม่ (TH):** เป้าหมายที่ผู้เรียน "เริ่มจากศูนย์" ต้องได้กลับไป — เขียนเป็นภาษาง่าย ๆ
- **ผู้เรียนทำอะไร (no-code):** ขั้นตอนที่ผู้เรียนลงมือเอง โดย "ไม่ต้องเขียนโค้ด" (คลิก / พิมพ์แชต / กด Run-Cell ที่เตรียมไว้)
- **ผูกกับ Pillar / Promise:** บล็อกนี้สนับสนุนเสาหลักไหนของคอร์ส และเชื่อมกับคำสัญญาบนโปสเตอร์อย่างไร
- **หมายเหตุ "เครื่องเดียว" (Single-box note):** เรามี DGX Spark **เครื่องเดียว** ให้ 30 คนใช้พร้อมกัน — ช่องนี้บอกวิธีจัดการการแย่งทรัพยากร (contention) ของบล็อกนั้น

**แกนกลางที่ร้อยทั้งวัน — "Agent = Model + Harness":**
Harness คือลูป **CONTEXT → OBSERVE → REASON → ACT** ที่ห่อด้วย Prompt / Orchestration / Memory / Tools & Skills / Security & Governance.
3 เสาหลัก (Pillar) ของคอร์สแมปเข้ากับภาพนี้ตรง ๆ:
- **Pillar 1 — Optimize Tokens** = ฝั่ง cost/latency ของ **Model** ("cost per token = KPI ใหม่")
- **Pillar 2 — Harnessing** = ตัว **Harness** (loop + orchestration + tools)
- **Pillar 3 — Secure & Sandbox** = กล่อง **Security & Governance** (OpenShell + NemoClaw)

**กฎเหล็กของ "เครื่องเดียว":** ทั้งห้องแชร์ **1 shared LAN endpoint** + **1 โมเดลเดียว** (Nemotron Nano คลาส 30B-A3B MoE หรือ 7–9B, FP8/NVFP4) เสิร์ฟผ่าน **vLLM** (continuous batching + prefix caching). **ห้ามโหลดโมเดลที่สองพร้อมกัน** (OOM / แย่ง memory bandwidth). คอขวดจริงของ GB10 คือ **memory bandwidth ไม่ใช่ความจุ**.

---

## ตารางกำหนดการ 12 บล็อก (Full timed agenda)

### บล็อก 1 — 10:00–10:25 · Registration & Login Check

| field | รายละเอียด |
|---|---|
| **เวลา** | 10:00–10:25 (25 นาที) |
| **หมายเหตุเวลา (TH)** | ประตูเปิด + เช็ก login ได้ตั้งแต่ 09:30 (ตาม pre-course email); block ลงทะเบียนทางการ 10:00–10:25 |
| **ชื่อ (TH)** | ลงทะเบียน + เช็ค login ทุกบัญชี |
| **Title (EN)** | Registration & Login Check |
| **ชนิด** | `reg` |
| **Goal มือใหม่ (TH)** | ทุกคน "เข้าระบบได้จริง" ก่อนเริ่มสอน — มีหน้าจอ chat ของตัวเองที่ต่อกับ DGX Spark พร้อมใช้ |
| **ผู้เรียนทำอะไร (no-code)** | รับการ์ดที่มี URL + user/pass → เปิดเบราว์เซอร์ → login เข้า Open WebUI → พิมพ์คำว่า **"hello"** ในช่องแชตเพื่อยืนยันว่าระบบตอบกลับได้ (ไม่ต้องติดตั้งอะไร ไม่ต้องเขียนโค้ด) |
| **ผูกกับ Pillar / Promise** | ฐานก่อนทุก Pillar — ทำให้ promise "ลงมือจริงบน DGX Spark" เป็นจริงตั้งแต่นาทีแรก |
| **หมายเหตุ "เครื่องเดียว"** | บัญชี 30 คน pre-provision ไว้ล่วงหน้า (Open WebUI / JupyterHub) ชี้ไป **endpoint เดียว**. "hello" เป็นข้อความสั้น โหลดเบา ไม่ทำให้เครื่องตัน. เตรียม **การ์ดสำรอง 5 ใบ + ขั้นตอนแก้ login ล่ม** ไว้ที่โต๊ะลงทะเบียน |

---

### บล็อก 2 — 10:25–10:45 · Welcome + "What is this box?"

| field | รายละเอียด |
|---|---|
| **เวลา** | 10:25–10:45 (20 นาที) |
| **ชื่อ (TH)** | เปิดคอร์ส + "กล่องนี้คืออะไร" (DGX Spark) |
| **Title (EN)** | Welcome + "What is this box?" (DGX Spark) |
| **ชนิด** | `lecture` |
| **Goal มือใหม่ (TH)** | เข้าใจว่ากล่องตรงหน้า = คอมพิวเตอร์ AI ที่ปกติอยู่ใน datacenter ย่อมาวางบนโต๊ะได้ และเข้าใจภาพใหญ่ "Agent = Model + Harness" ที่จะร้อยทั้งวัน |
| **ผู้เรียนทำอะไร (no-code)** | ดู 1 สไลด์ไล่ขนาด small → desktop → datacenter + ดู **dashboard ของเครื่องจริง** (Triton/Grafana ฉายบนจอ) ว่าตอนว่างเครื่องนิ่งแค่ไหน — ไว้เทียบกับตอน 30 คนยิงพร้อมกันใน LAB 1 |
| **ผูกกับ Pillar / Promise** | วาง overarching frame "Agent = Model + Harness" → ชี้ล่วงหน้าว่า Pillar 1 = Model, Pillar 2 = Harness, Pillar 3 = Security box. รองรับ promise "เข้าใจทั้ง NVIDIA AI stack" |
| **หมายเหตุ "เครื่องเดียว"** | **Analogy:** DGX Spark = "ครัวกลางร้านเดียว" ที่ลูกค้า 30 โต๊ะสั่งอาหารพร้อมกัน — ปูพื้นให้ผู้เรียนเข้าใจว่าทำไมบางจังหวะจะ "ช้าลงเมื่อพร้อมกัน". ย้ำว่า GB10 มี memory ก้อนเดียว 128GB และ **ไม่มี MIG** → แชร์ด้วย container + time-slicing |

---

### บล็อก 3 — 10:45–11:20 · LAB 1 — LM Studio first-win → shared endpoint → "30 คนยิงพร้อมกัน"

| field | รายละเอียด |
|---|---|
| **เวลา** | 10:45–11:20 (35 นาที) |
| **ชื่อ (TH)** | LAB 1 — ชนะครั้งแรกด้วย LM Studio → endpoint ที่แชร์ → "30 คนยิงพร้อมกัน" |
| **Title (EN)** | LAB 1 — LM Studio first-win → shared endpoint → concurrency demo |
| **ชนิด** | `lab` |
| **Goal มือใหม่ (TH)** | (1) เห็นว่า **LM Studio** = "ChatGPT ส่วนตัว" บน Spark (2) เข้าใจว่าทุกคนต่อ **endpoint เดียวกัน** (3) เห็นด้วยตาตัวเองว่าเมื่อ 30 คนยิงพร้อมกัน เครื่องทำงานหนักขึ้นบน dashboard |
| **ผู้เรียนทำอะไร (no-code)** | (1) ดู instructor เปิด **LM Studio (llmster)** บน Spark → "เครื่องนี้คุยได้เหมือน ChatGPT". (2) ผู้เรียนแต่ละคนพิมพ์คำถามของตัวเองในหน้า chat ที่ต่อ **shared LAN endpoint**. (3) **นับ 3-2-1 ทุกคนกด Send พร้อมกัน** → จ้องจอ dashboard เห็น GPU/memory พุ่ง + batching รวม 30 requests |
| **ผูกกับ Pillar / Promise** | นำเข้าสู่ **Pillar 1 (Optimize Tokens)** — "ช้าลงตอนพร้อมกัน = บทเรียน ไม่ใช่บั๊ก". ส่ง first-win ตาม promise "ลงมือได้จริงแม้เริ่มจากศูนย์" |
| **หมายเหตุ "เครื่องเดียว"** | ⚠️ **LM Link รับได้ ~2 คน — ใช้กับ 30 คนไม่ได้** → ทั้งห้องต้องต่อ **1 shared LAN endpoint** (Open WebUI หน้า vLLM/NIM) ไม่ใช่ LM Link. โมเดลตัวอย่าง playbook = **Nemotron 3 Nano Omni (~65–70GB)**. คำสั่ง first-win (instructor รันบนเครื่อง ไม่ใช่ผู้เรียน): `curl -fsSL https://lmstudio.ai/install.sh \| bash` → `lms get nvidia/nemotron-3-nano-omni` → `lms load ...` → `lms server start --bind 0.0.0.0 --port 1234`. Concurrency demo ตั้งใจให้ contention เกิด = หัวใจของบทเรียน |

---

### บล็อก 4 — 11:20–11:35 · Break 1

| field | รายละเอียด |
|---|---|
| **เวลา** | 11:20–11:35 (15 นาที) |
| **ชื่อ (TH)** | พักเบรก 1 |
| **Title (EN)** | Break 1 |
| **ชนิด** | `break` |
| **Goal มือใหม่ (TH)** | พักสมอง / เข้าห้องน้ำ / ถามคำถาม instructor แบบตัวต่อตัว |
| **ผู้เรียนทำอะไร (no-code)** | — (พัก) |
| **ผูกกับ Pillar / Promise** | — (transition จาก first-win เข้าสู่เนื้อ Nemotron/reasoning) |
| **หมายเหตุ "เครื่องเดียว"** | ช่วงนี้ instructor/ทีมงาน **re-warm โมเดล + เช็ค kernel ทุกบัญชี** เตรียมพร้อม LAB 2. ไม่มีโหลดยิงเข้าเครื่อง เครื่องได้พักไปด้วย |

---

### บล็อก 5 — 11:35–12:05 · LAB 2 — NeMo vs Nemotron + reasoning toggle

| field | รายละเอียด |
|---|---|
| **เวลา** | 11:35–12:05 (30 นาที) |
| **ชื่อ (TH)** | LAB 2 — แยก NeMo กับ Nemotron + สวิตช์โหมดคิด (reasoning toggle) |
| **Title (EN)** | LAB 2 — NeMo vs Nemotron + reasoning toggle |
| **ชนิด** | `lab` |
| **Goal มือใหม่ (TH)** | แยกออกว่า **NeMo = กล่องเครื่องมือสร้าง/ปรับโมเดล** ส่วน **Nemotron = โมเดลที่รันจริง** และเห็นว่าโมเดลตัวเดียวกัน "คิดมากขึ้น" ได้เมื่อเปิดโหมด reasoning |
| **ผู้เรียนทำอะไร (no-code)** | ส่ง **คำถามเดียวกัน** สองรอบ — รอบแรกใส่ `/no_think`, รอบสองใส่ `/think` → เปรียบเทียบคำตอบและความเร็วด้วยตาตัวเอง (คลิก/พิมพ์ล้วน ไม่เขียนโค้ด) |
| **ผูกกับ Pillar / Promise** | ปูพื้นโมเดล Nemotron family (Nano 30B-A3B / Super 120B-A12B / Ultra 550B-A55B; A = active params, MoE) ก่อนเข้า 3 Pillar — สนับสนุน promise "เข้าใจทั้ง stack" |
| **หมายเหตุ "เครื่องเดียว"** | **Analogy:** MoE = "ทีมงาน 30 คน แต่เรียกใช้แค่ 3 คนต่องาน" → เร็วเหมือนโมเดล 3B แต่ฉลาดกว่า จึงฟิตกับ 128GB. `/think` vs `/no_think` ใช้ **โมเดลเดิมตัวเดียว** (ห้ามโหลดตัวที่สอง). โหมด `/think` กิน token เยอะกว่า → **จัดเป็น 2 เวฟ** (ครึ่งห้องก่อน) กันคิวยาว |

---

### บล็อก 6 — 12:05–12:25 · Physical AI window — Jetson Thor + humanoid

| field | รายละเอียด |
|---|---|
| **เวลา** | 12:05–12:25 (20 นาที) |
| **ชื่อ (TH)** | หน้าต่าง Physical AI — Jetson Thor + หุ่นยนต์ |
| **Title (EN)** | Physical AI window — Jetson Thor + humanoid |
| **ชนิด** | `demo` |
| **Goal มือใหม่ (TH)** | เห็นว่า AI ไม่ได้อยู่แค่ในแชต — มันคุมหุ่นยนต์ได้ และเข้าใจไอเดีย "ภาพ + ประโยค → คำสั่งมอเตอร์" แบบกว้าง ๆ |
| **ผู้เรียนทำอะไร (no-code)** | นั่งดูจอ: คลิป **G1 humanoid เดิน (RL, MuJoCo-Warp) สตรีมจาก Jetson Thor** (รูป/คลิปจริงจาก GTC) + ฟัง instructor อธิบายแนวคิด Cosmos Reason 2 และภาพรวม pipeline (ไม่ต้องทำอะไรกับเครื่อง) |
| **ผูกกับ Pillar / Promise** | ขยายภาพ NVIDIA AI stack ฝั่ง Physical AI/Edge — เชื่อม promise "เห็นภาพรวมทั้ง ecosystem". วาง teaser ก่อน GTC recap ตอนปิด |
| **หมายเหตุ "เครื่องเดียว"** | บล็อกนี้ **ไม่ยิงโหลดเข้า DGX Spark เลย** — ใช้ **asset offline** (วิดีโอ/รูปเซฟไว้ล่วงหน้า ไม่พึ่งเน็ตสด) → จงใจวางคั่นเป็น "ช่วงพักเครื่อง" ก่อนพักเที่ยง. ⚠️ พูดชื่อ/วันผลิตภัณฑ์ว่า **"ตามที่ประกาศในงาน"** (เด็คเป็น GTC 2026 forward-dated); Jetson AGX Thor T5000 spec ที่ประกาศ = Blackwell, 2070 FP4 TFLOPS, 14-core Arm, 128GB |

---

### บล็อก 7 — 12:25–13:10 · Lunch

| field | รายละเอียด |
|---|---|
| **เวลา** | 12:25–13:10 (45 นาที) |
| **ชื่อ (TH)** | พักกลางวัน |
| **Title (EN)** | Lunch |
| **ชนิด** | `lunch` |
| **Goal มือใหม่ (TH)** | พักกินข้าว / networking / ถามตอบนอกรอบ |
| **ผู้เรียนทำอะไร (no-code)** | — (พักเที่ยง) |
| **ผูกกับ Pillar / Promise** | — (แบ่งครึ่งวัน: เช้าปูพื้น → บ่ายลงลึก 3 Pillar) |
| **หมายเหตุ "เครื่องเดียว"** | ช่วงนี้ทีมงาน **pre-load notebook ทุก lab ค้างไว้ในบัญชีผู้เรียน** + ยืนยันโมเดลหลักยัง warm + ฉาย dashboard ค้างไว้ พร้อมลุยภาคบ่าย |

---

### บล็อก 8 — 13:10–13:50 · LAB 3 — Pillar 1: Optimize Tokens

| field | รายละเอียด |
|---|---|
| **เวลา** | 13:10–13:50 (40 นาที) |
| **ชื่อ (TH)** | LAB 3 — เสาหลักที่ 1: Optimize Tokens (ลดต้นทุน/เร่งความเร็ว) |
| **Title (EN)** | LAB 3 — Pillar 1: Optimize Tokens |
| **ชนิด** | `lab` |
| **Goal มือใหม่ (TH)** | เข้าใจว่า "ความเร็ว/ต้นทุน" ของ AI ปรับได้ และเห็นเองว่า **prompt ซ้ำตอบเร็วฮวบ** เพราะ cache |
| **ผู้เรียนทำอะไร (no-code)** | (1) จดตัวเลข **tok/s** และ **TTFT** จากหน้าจอ. (2) ส่ง prompt เดิม **ซ้ำอีกครั้ง** → เห็น **prefix cache hit** ทำให้เร็วขึ้นชัด ๆ. (3) ดู metrics เทียบ **aggregate (รวมทั้งห้อง) vs per-user** บน dashboard |
| **ผูกกับ Pillar / Promise** | **Pillar 1 (Optimize Tokens)** เต็มตัว — สรุปแก่น "cost per token = KPI ใหม่", Context Rot ("window ใหญ่ ≠ สมองใหญ่", f1 73%@256k → 45%@1M), มนตรา **inline << file reference << var reference**. ตรงกับ promise เสาหลักที่ 1 บนโปสเตอร์ |
| **หมายเหตุ "เครื่องเดียว"** | ใช้ **system prompt เดียวกันทั้งห้อง** เพื่อให้ **prefix/KV caching hit ชัด** = เป็นข้อดีของเครื่องเดียว/endpoint เดียว ไม่ใช่ข้อจำกัด. ⚠️ **NVFP4 ต้องใช้ TensorRT-LLM หรือ NIM เท่านั้น** → ส่วนนี้อธิบาย/โชว์เป็น concept ไม่บังคับ build สดต่อหน้าคน. คำสั่งอ้างอิง vLLM: `vllm serve <model> --gpu-memory-utilization 0.85 --max-num-seqs 32 --max-model-len 4096-8192 --kv-cache-dtype fp8` |

---

### บล็อก 9 — 13:50–14:35 · LAB 4 — Pillar 2: Harnessing (multi-agent)

| field | รายละเอียด |
|---|---|
| **เวลา** | 13:50–14:35 (45 นาที) |
| **ชื่อ (TH)** | LAB 4 — เสาหลักที่ 2: Harnessing (ระบบหลายเอเจนต์ทำงานร่วมกัน) |
| **Title (EN)** | LAB 4 — Pillar 2: Harnessing (multi-agent) |
| **ชนิด** | `lab` |
| **Goal มือใหม่ (TH)** | เข้าใจว่า "agent = โมเดล + เครื่องมือ ที่ทำงานเป็นลูป" และเห็น orchestrator สั่งงาน sub-agent หลายตัวให้ทำงานต่อกัน |
| **ผู้เรียนทำอะไร (no-code)** | (1) กด **Run-Cell** ที่เตรียมไว้ → ดู **orchestrator สั่ง coding agent + reviewer agent** (แสดงคนละสีให้แยกออก). (2) ผู้เรียนรัน **single-agent tool-use (MCP)** ด้วยตัวเอง โดยกดปุ่ม/เลือกเมนูที่เตรียมให้ (no-code steering) |
| **ผูกกับ Pillar / Promise** | **Pillar 2 (Harnessing) = ตัว Harness** ใน "Agent = Model + Harness" — บล็อก wow สูงสุดของวัน. ฉาย **AI-Q Open Agent Blueprint** (Intent Router=Nano → Researcher=Super, NeMo Agent Toolkit, RAG, MCP, Dynamo routing) เป็นตัวอย่าง production. ตรงกับ promise เสาหลักที่ 2 |
| **หมายเหตุ "เครื่องเดียว"** | ⚠️ **contention สูงสุดของวัน** (หลาย agent = หลาย request ซ้อน). มาตรการ: **full multi-agent loop ให้ instructor โชว์ครั้งเดียว**, sub-agent ใช้โมเดลเล็กผ่าน **Ollama**, จำกัด **2–3 steps**, `max_tokens 128–256`, **แบ่งเวฟ/คิว** สำหรับ single-agent ของผู้เรียน, มี **cloud fallback** เผื่อ demo สด fail. ยังคง **ห้ามโหลดโมเดลที่สองชนกับโมเดลหลัก** จนเครื่องล่ม |

---

### บล็อก 10 — 14:35–14:50 · Break 2

| field | รายละเอียด |
|---|---|
| **เวลา** | 14:35–14:50 (15 นาที) |
| **ชื่อ (TH)** | พักเบรก 2 |
| **Title (EN)** | Break 2 |
| **ชนิด** | `break` |
| **Goal มือใหม่ (TH)** | พักสมองหลังบล็อกหนักที่สุด (LAB 4) ก่อนเข้าเรื่องความปลอดภัย |
| **ผู้เรียนทำอะไร (no-code)** | — (พัก) |
| **ผูกกับ Pillar / Promise** | — (transition จาก Harnessing เข้าสู่ Secure & Sandbox) |
| **หมายเหตุ "เครื่องเดียว"** | ทีมงานเตรียม **sandbox container ของ LAB 5** (CPU-only ephemeral ต่อคน) + ยืนยันโมเดลหลักยังเสิร์ฟอยู่ ไม่มีโมเดลที่สองค้างจาก LAB 4 |

---

### บล็อก 11 — 14:50–15:30 · LAB 5 — Pillar 3: Secure & Sandbox = NemoClaw + OpenShell

| field | รายละเอียด |
|---|---|
| **เวลา** | 14:50–15:30 (40 นาที) |
| **ชื่อ (TH)** | LAB 5 — เสาหลักที่ 3: Secure & Sandbox = NemoClaw + OpenShell |
| **Title (EN)** | LAB 5 — Pillar 3: Secure & Sandbox = NemoClaw + OpenShell |
| **ชนิด** | `lab` |
| **Goal มือใหม่ (TH)** | เข้าใจว่า "agent ทำงานได้ แต่ถูก policy ล็อกไว้ให้ปลอดภัย" — เห็น sandbox บล็อกการออกเน็ต และเห็น audit trail ที่บันทึกทุกอย่าง |
| **ผู้เรียนทำอะไร (no-code)** | (1) เปิด chat **NemoClaw** สั่ง "สรุปข้อความ / สร้างไฟล์ note.txt" → ทำได้ ✅. (2) ลองให้ agent ออกเน็ต `curl -sS https://api.github.com/zen` → เจอ **`curl: (56) ... 403 from proxy after CONNECT`** ❌ (deny-by-default). (3) ดู instructor แก้ **YAML policy** เปิด GitHub read-only → **GET ผ่าน ✅ / POST → `{"error":"policy_denied",...}` ❌** + ดู **audit trail** |
| **ผูกกับ Pillar / Promise** | **Pillar 3 (Secure & Sandbox) = กล่อง Security & Governance** — headline ของ Pillar 3. สรุปแมปกับ **สไลด์ OpenShell จาก GTC = ภาพ diagram บนโปสเตอร์ Agent Enterprise เป๊ะ** (Policy Authoring & Signing → Gateway → agents + Skills/Tools) + แนวคิด signed skills (7-stage: Scan→Evaluate→Skill Card→Sign→Catalog→Sync→Enforce). ตรงกับ promise เสาหลักที่ 3 |
| **หมายเหตุ "เครื่องเดียว"** | self-check rail ใช้ **โมเดลเดิม** (⚠️ ห้ามโหลด NemoGuard NIM 8B ตัวที่สอง = กิน 16–20GB เสี่ยง OOM); **sandbox container เบา CPU-only ephemeral ต่อคน** ไม่แย่ง GPU. 🔴 **ห้ามรัน `curl ... \| bash` สดจาก URL ที่ยังไม่ยืนยัน** (เช่น nemoclaw.sh) — ใช้คำสั่ง OpenShell ที่ยืนยันแล้ว: `curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh \| sh` ; `openshell sandbox create --remote spark --from openclaw` ; `openshell policy set demo --policy examples/sandbox-policy-quickstart/policy.yaml --wait`. ⚠️ OpenShell = **ALPHA (v0.0.38)** |

---

### บล็อก 12 — 15:30–16:00 · Closing — GTC Taipei 2026 recap + giveaways + certificate

| field | รายละเอียด |
|---|---|
| **เวลา** | 15:30–16:00 (30 นาที) |
| **ชื่อ (TH)** | ปิดท้าย — สรุป GTC Taipei 2026 + ของแจก + certificate + ทบทวน 3 เสาหลัก |
| **Title (EN)** | Closing — GTC Taipei 2026 recap + giveaways + certificate |
| **ชนิด** | `wrap` |
| **Goal มือใหม่ (TH)** | ปะติดปะต่อทั้งวันเข้าเป็นภาพเดียว ("Agent = Model + Harness" + 3 เสาหลัก) รู้ว่าจะไปต่ออย่างไร และได้ของกลับบ้าน |
| **ผู้เรียนทำอะไร (no-code)** | ดู **recap board** (อิงรูปจริงจาก GTC) → ทบทวน 3 เสาหลัก → **รับของแจก + certificate** → ถ่ายรูปหมู่ → ทำแบบประเมิน |
| **ผูกกับ Pillar / Promise** | ปิด loop ทั้ง 3 Pillar เข้ากับ "Agent = Model + Harness" + 4 Agent Factory principles (distributed / data gravity / security-by-default / cost-per-token = KPI). ส่งมอบ promise สุดท้าย: certificate + recap |
| **หมายเหตุ "เครื่องเดียว"** | ไม่มีโหลดหนักเข้าเครื่อง — recap ใช้ **asset offline**. **certificate = "สอนโดย NVIDIA Certified Professional"** (ไม่ใช่ "ออก NVIDIA cert ให้ผู้เรียน"). ⚠️ ชื่อ/วันผลิตภัณฑ์ใน recap (Nemotron 3 Ultra, Cosmos 3 ฯลฯ) พูดว่า **"ตามที่ประกาศในงาน"**. 30 นาทีพอแจก cert ครบ 30 คนพอดี |

---

## สรุปน้ำหนักเวลา (Time-weight summary)

### แยกตามชนิดบล็อก (by type)

| ชนิด | บล็อก | รวมเวลา |
|---|---|---|
| **lab** (ลงมือทำ) | LAB 1 (35') + LAB 2 (30') + LAB 3 (40') + LAB 4 (45') + LAB 5 (40') | **190 นาที** |
| **lecture / demo** (บรรยาย/สาธิต) | Welcome (20') + Physical AI (20') | **40 นาที** |
| **reg / wrap** (เปิด/ปิด) | Registration (25') + Closing (30') | **55 นาที** |
| **break / lunch** (พัก) | Break 1 (15') + Lunch (45') + Break 2 (15') | **75 นาที** |
| | **รวมทั้งวัน** | **360 นาที (6 ชม.)** |

### Net teaching time (เวลาสอนสุทธิ)

**Net teaching ≈ 4.75 ชม. (285 นาที)** = lab (190') + lecture/demo (40') + closing recap (30') + welcome ส่วนเปิด frame (25' ของ reg/welcome ที่เป็นเนื้อ) — หักเวลาพักและพักเที่ยงออก (75').
สูตรง่าย ๆ: 360 นาทีทั้งวัน − 75 นาทีพัก = **285 นาที ≈ 4.75 ชม. เวลาสอนสุทธิ**.

### น้ำหนักของ 3 เสาหลัก (Pillar weighting)

| Pillar | บล็อก | เวลา | เหตุผลของน้ำหนัก |
|---|---|---|---|
| **Pillar 1 — Optimize Tokens** | LAB 3 (+ concurrency lesson จาก LAB 1) | **40 นาที** | แก่นเข้าใจ cost/latency — กระชับได้เพราะมี LAB 1 ปูมาแล้ว |
| **Pillar 2 — Harnessing** | LAB 4 | **45 นาที** | **ยาวสุด** — wow สูงสุด + เสี่ยง contention สูงสุด ต้องจัดเป็นเวฟ/มี fallback |
| **Pillar 3 — Secure & Sandbox** | LAB 5 | **40 นาที** | headline NemoClaw + OpenShell — ต้องมีเวลาโชว์ policy edit + audit trail ครบสเต็ป |

> **น้ำหนัก Pillar 1/2/3 = 40 / 45 / 40 นาที.** Pillar 2 ยาวสุดโดยตั้งใจ (จุด wow + ความเสี่ยงสูงสุด). Closing 30 นาทีพอแจก certificate ครบ 30 คนได้จริง.

---

## หมายเหตุการคุมเวลา (Pacing notes for instructor)

- **บล็อกที่เสี่ยงล่าช้าสุด = LAB 4** (multi-agent contention) → ถ้าช้ากว่าแผน ให้ **ตัด full multi-agent loop เหลือ instructor โชว์ครั้งเดียว** แล้วเดินต่อทันที
- ทุก lab ต้องมี **visible win** ภายในนาทีแรก ๆ (ผู้เรียนเริ่มจากศูนย์ ต้องเห็นผลเร็วเพื่อไม่หลุด)
- เตรียมสคริปต์ประโยค **"ช้าลงตอนพร้อมกัน = บทเรียน Pillar 1 ไม่ใช่บั๊ก"** ใช้ซ้ำได้ทุกครั้งที่เครื่องตึง
- **🔒 Hard gate ก่อนวันงาน:** dry-run เต็มรูปแบบ 30 บัญชียิงพร้อมกัน 1 วันก่อน → วัด tok/s จริง, ยืนยันไม่ OOM, ยืนยันทุก lab รันได้

---

## สิ่งที่ผู้สอนต้องเช็ค/เติมเองก่อนวันงาน (Instructor TODO)

1. **ตัวเลข performance จริง** (tok/s, TTFT) — ✏️ ยังไม่ยืนยัน ต้อง **วัดเองใน dry-run** แล้วเติมลงสคริปต์ LAB 1/LAB 3
2. **ยืนยันทุก URL resolve ได้** ก่อนวันงาน (โดยเฉพาะ install scripts ของ LM Studio / OpenShell) — และ **ห้ามรัน `curl|bash` สดจาก URL ที่ยังไม่ยืนยัน** เช่น `nemoclaw.sh`
3. **เลือก/ยืนยันโมเดลหลักตัวจริง** ที่จะ pre-pull (Nemotron Nano 30B-A3B หรือคลาส 7–9B, FP8/NVFP4) + โมเดล Ollama เล็กสำหรับ LAB 4
4. **ถ้อยคำบน certificate** — ยืนยันว่าเป็น "สอนโดย NVIDIA Certified Professional" ไม่ใช่ออก NVIDIA cert ให้ผู้เรียน
5. **คลิป/asset offline** (G1 humanoid, Cosmos, GTC recap board) — เซฟครบและทดสอบเปิดแบบถอดเน็ต
6. **cloud / laptop fallback** สำหรับ demo เสี่ยง (โดยเฉพาะ LAB 4 multi-agent loop)
