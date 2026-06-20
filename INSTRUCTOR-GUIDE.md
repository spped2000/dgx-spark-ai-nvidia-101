# 👩‍🏫 INSTRUCTOR GUIDE — คู่มือผู้สอน
companion ของ [LABS-GUIDE.md](LABS-GUIDE.md) (ด้านเทคนิค/คำสั่ง) — อันนี้คือ **"สอนยังไงให้เห็นภาพ"**

## หลักการสอน (มือใหม่ · no-code)
1. ทุกบล็อกต้องมี **visible win** ใน ~15–20 นาที (ผู้เรียนเห็นของจริงทำงาน)
2. ผู้เรียนแค่ **คลิก / พิมพ์แชต / Run-Cell** — คำสั่ง terminal เป็นของผู้สอน
3. พูดประโยคทอง: **"ช้าตอนยิงพร้อมกัน = บทเรียน ไม่ใช่บั๊ก"** (bandwidth ของ GPU เดียว)
4. **ซื่อสัตย์:** ของจาก GTC deck = "ตามที่ประกาศในงาน" · คำตอบไทยจากโมเดล 8B หยาบได้ (เน้นกลไก ไม่ใช่เนื้อหา)

## ✅ ก่อนวันงาน (master checklist)
- [ ] 🔒 **dry-run gate:** จำลอง 30 บัญชี + วัด tok/s/TTFT จริง + ยืนยันไม่ OOM (ดู `tools/dryrun-report.md`)
- [ ] **services up:** `docker ps` เห็น vLLM `:8000` · JupyterHub `:8888` · Grafana `:3001` · Phoenix `:6006` · OpenShell gateway `:8080` (+ sandbox `lab5-ui`) · Open WebUI `:3000`
- [ ] **tokens:** HF + NGC ใน `course/.env` (gitignored — ห้าม commit/โชว์จอ)
- [ ] **pre-warm:** ยิง ping เข้า vLLM 1 ครั้ง (กัน cold start) · pre-pull `dgx-singleuser` image (spawn เร็ว)
- [ ] **fallback พร้อม:** สกรีนช็อต/คลิป — `403/policy_denied` (LAB5), กราฟ Grafana ตอน 30 คน, คลิป Physical AI
- [ ] **เลือก serving 1 ตัว** (แนะนำ vLLM) — ถ้าจะโชว์ NIM ต้องสลับ (GPU เดียวรันทีละตัว)
- [ ] เปิด 4 แท็บบน projector: **Open WebUI · Grafana · Phoenix · slides (deck.pptx)**

## 🖥️ ฉายจออะไรตอนไหน
| LAB | จอหลัก | จอเสริม |
|---|---|---|
| 1 | Open WebUI (:3000) | Grafana (:3001) |
| 2 | terminal | Phoenix `dgx-spark-lab2` |
| 3 | terminal | Grafana / Phoenix |
| 4 | Phoenix `dgx-spark-lab4` (กาง trace) | terminal |
| 5 | terminal (`phoenix_sandbox_live`) | `openshell term` + Phoenix |

---

## การสอนต่อ LAB

### LAB 1 — Serving + 30 คน · ⏱️ ~35 นาที
- **เตรียม:** Open WebUI พร้อม login · sim พร้อมรัน · Grafana เปิดค้าง
- **พูด/ทำ:** เปิดแชต ถาม 1 คำถาม → "นี่รันบนกล่องนี้ ไม่ใช่ cloud" → "เป็น 30 คนพร้อมกันบ้าง" → รัน sim → ชี้ Grafana กราฟพุ่ง → **"เครื่องเดียวเสิร์ฟ 30 คนได้ด้วย continuous batching"**
- **คำถามที่เจอ:** *ต่อเน็ตไหม?* → ไม่, รันโลคัล · *ทำไมช้าลงตอนพร้อมกัน?* → แชร์ GPU bandwidth (คอขวด)
- **ถ้าพัง:** sim ช้า → `--users 15` · :3000 ล่ม → `uv run tools/phoenix_chat_live.py`

### LAB 2 — Reasoning toggle · ⏱️ ~30 นาที
- **เตรียม:** Phoenix เปิด project `dgx-spark-lab2`
- **พูด/ทำ:** รัน demo → OFF ตอบสั้น/เร็ว → ON คิดยาว (เตือน "รอ ~40 วิ = นั่นคือต้นทุน") → สลับ Phoenix เทียบ tokens/latency 2 รอบ
- **คำถามที่เจอ:** *ON ช้าเพราะ?* → สร้าง token คิดเยอะ · *ใช้ ON เมื่อไร?* → งานยาก/ต้องให้เหตุผล ไม่ใช่ทุกงาน
- **ถ้าพัง:** ON ช้าเกิน → ใช้คำถามสั้นลง / คุยกับห้องระหว่างรอ

### LAB 3 — Optimize Tokens · ⏱️ ~30 นาที
- **เตรียม:** terminal พร้อม
- **พูด/ทำ:** รัน demo → ชี้ **TTFT 330→100 ms (−68%)** → "prefix เดิมถูกแคช ไม่ต้องคิดใหม่ = เร็ว+ถูก" → โยง "cost per token = KPI"
- **คำถามที่เจอ:** *cache คืออะไร?* → จำ context เดิม · *ประหยัดจริงไหม?* → ใช่ token ที่ไม่สร้างใหม่ = เงินที่ประหยัด
- **ถ้าพัง:** ตัวเลขไม่ต่าง → ยิงรอบ 3 (cache อุ่นแล้ว) / เพิ่มความยาว prompt

### LAB 4 — Multi-Agent · ⏱️ ~45 นาที
- **เตรียม:** Phoenix project `dgx-spark-lab4`
- **พูด/ทำ:** รัน demo → ชี้ orchestrator แตกงาน → coder เขียน → reviewer ตรวจ → **กาง trace ใน Phoenix ให้เห็นทีม** → "งานดีเพราะมีคนตรวจ ไม่ใช่ตัวเดียวตอบรวด"
- **คำถามที่เจอ:** *agent ต่างจาก chatbot?* → agent ใช้ tools เป็นลูปจนงานเสร็จ · *ทำไมหลายตัว?* → แบ่งงาน + มีคนตรวจ
- **ถ้าพัง:** โมเดลตอบมั่ว → เน้น **โครงสร้าง trace ใน Phoenix** (เห็นการ delegate ชัดกว่าเนื้อหา)

### LAB 5 — Secure & Sandbox · ⏱️ ~40 นาที ⭐ ปิดทรงพลัง
- **เตรียม:** `export PATH=/tmp/osx/extracted/usr/bin:$PATH` · sandbox `lab5-ui` = read-only · เปิด `openshell term` อีกจอ
- **พูด/ทำ:** "ปล่อย AI รันคำสั่งเอง น่ากลัวไหม?" → `phoenix_sandbox_live.py` → พิมพ์ GET (✅) → POST (❌ 403 สดๆ) → example.com (❌) → **เพิ่มกฎสด** `policy update --add-allow` → POST ผ่าน! (ไม่ restart) → ชี้ audit/Phoenix
- **คำถามที่เจอ:** *ปลอดภัยจริง?* → deny-by-default + บันทึกทุก action · *เปิดสิทธิ์ยังไง?* → policy ทีละกฎ (มี signing)
- **ถ้าพัง:** พิมพ์สดพลาด/ sandbox งอแง → `uv run tools/phoenix_agent_demo.py` (อัตโนมัติ) หรือสกรีนช็อต 403 สำรอง

---

## 🔌 ถ้าจะโชว์ NIM / Triton (serving alternatives)
- **Triton dashboard** (มีอยู่แล้ว :3001) — ใช้คู่ LAB 1/3 โชว์ metrics สด
- **NIM** — โชว์ "one command turnkey": `docker stop vllm-ngc && docker start nim-llm-demo` → ready → curl :8002 → **เน้นว่า NIM auto-เลือก GB10/FP8 profile เอง** → เสร็จแล้ว `docker stop nim-llm-demo && docker start vllm-ngc` (⚠️ GPU เดียว = ทีละตัว — เป็นบทเรียนเอง!)

## 🏁 ปิดวัน (~30 นาที)
GTC Taipei 2026 recap (อิงรูป/เด็คจริง — confirmed vs "ตามที่ประกาศ") → สรุป **3 เสา** (Optimize/Harness/Secure) → certificate (สอนโดย NVIDIA Certified Professional) → giveaway → ถ่ายรูปหมู่
> รายละเอียด timing นาทีต่อนาที + ประโยคสคริปต์: [runbook.md](runbook.md) · scenario เดโม: [demo-runbook.md](demo-runbook.md)
