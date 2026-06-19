# 🎬 Live Demo Runbook — เล่าให้ผู้เรียนเห็นภาพที่สุด (validated บน DGX Spark)
สคริปต์กำกับเดโมสดต่อ LAB: hook → จอที่ฉาย → ขั้นตอนสด → จังหวะ "อ๋อ!" → อุปมา → เวลา → fallback
> ทุกคำสั่งใช้ **endpoint/บริการที่รันอยู่แล้ว** (ไม่ต้อง `run_dryrun.sh` ซ้ำ)

## ⚙️ เตรียมก่อนเดโม (เช็ก 30 วิ)
```bash
docker ps --format '{{.Names}} {{.Ports}}'     # ต้องเห็น: vllm-ngc :8000 · phoenix :6006 · docker-gateway-1 :8080 · open-webui :3000
curl -s localhost:8000/v1/models | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"][0]["id"])'   # = nemotron-nano
cd /home/agicafet/Documents/dgx1/course
export PATH=/tmp/osx/extracted/usr/bin:$PATH       # ให้เจอ openshell (LAB5)
export BASE_URL=http://localhost:8000/v1 MODEL=nemotron-nano
```
🖥️ เปิดทิ้งไว้ 3 แท็บเบราว์เซอร์: **Open WebUI :3000** · **Phoenix :6006** · slide deck — สลับให้ดูตอนเดโม

---

## LAB 1 — "เครื่องเดียว เสิร์ฟทั้งห้องพร้อมกัน"
🎯 **Hook:** "กล่องบนโต๊ะนี้คือ ChatGPT ส่วนตัวของห้องเรา — ไม่ใช่ cloud. ลองให้ทั้งห้องถามพร้อมกัน 30 คนดู เครื่องเดียวจะไหวไหม?"
🖥️ จอ: Open WebUI (:3000) + terminal
▶️ สด:
1. เปิด **Open WebUI :3000** พิมพ์ "แนะนำ DGX Spark สั้นๆ" → คำตอบสตรีมออกมา → "นี่รันบนเครื่องนี้ 100% ไม่ต่อเน็ตออกไปไหน"
2. terminal: `uv run tools/sim_30_learners.py --users 30 --max-tokens 128`
3. รอ ~30 วิ → เห็น **30/30 สำเร็จ · ~200 tok/s รวม · ไม่ OOM**
💡 **อ๋อ:** เครื่องเดียวตอบ 30 คนพร้อมกันได้ ด้วย **continuous batching ของ vLLM** (ไม่ใช่ตอบทีละคน)
🔗 อุปมา: พนักงานเสิร์ฟเก่ง รับออเดอร์ 30 โต๊ะแล้วเดินเสิร์ฟรอบเดียว — ไม่ใช่จ้าง 30 คน
⏱️ ~4 นาที · 🛟 ถ้า sim ช้า: ลด `--users 15`; ถ้า :3000 ล่ม: ใช้ `phoenix_chat_live.py` แทน

---

## LAB 2 — "โมเดลคิดให้ดู vs ตอบเลย" (reasoning)
🎯 **Hook:** "โมเดลตัวเดียวกัน สั่งให้ 'คิดดังๆ ทีละขั้น' หรือ 'ตอบเลย' ได้ — แล้วแบบไหนคุ้มกว่า?"
🖥️ จอ: terminal + Phoenix `dgx-spark-lab2`
▶️ สด:
1. `uv run tools/lab2_reasoning_demo.py`
2. **OFF** → ตอบสั้น ~210 tokens / ~15s (เช่น "ถึง 11:30")
3. **ON** → คิดยาว ~600 tokens / ~40s (โชว์วิธีคิดเป็นขั้น) — *เตือนผู้เรียนว่ารอ ~40 วิ = นั่นแหละต้นทุน*
4. สลับไป **Phoenix** → เทียบ 2 trace: ON tokens/latency พุ่งกว่ามาก
💡 **อ๋อ:** เปิดโหมดคิด = ฉลาด/รอบคอบขึ้น **แต่ช้าและแพงขึ้น** → เลือกใช้ให้เหมาะงาน (โยงเข้า LAB 3)
🔗 อุปมา: นักเรียนแสดงวิธีทำทุกขั้น vs ตอบแต่เลข
⏱️ ~3 นาที · 🛟 ON ช้า → ใช้คำถามสั้นลง/ลด max_tokens; พูดคุยระหว่างรอ

---

## LAB 3 — "token ที่ไม่ต้องคิดใหม่ = แทบฟรี" (Optimize Tokens)
🎯 **Hook:** "ถามคำถามที่มี context เดิมซ้ำ ทำไมครั้งที่สองเร็วขึ้นเยอะ?"
🖥️ จอ: terminal + Phoenix
▶️ สด:
1. `uv run tools/lab3_prefix_cache_demo.py`
2. เห็น **รอบ 1 (cold) TTFT ~330 ms → รอบ 2 (warm) ~100 ms = เร็วขึ้น ~68%**
💡 **อ๋อ:** prefix เดิมถูก **cache** ไว้ → ไม่ต้องประมวลผลซ้ำ → เร็ว+ถูกลง. "ของถูกสุดคือ token ที่ไม่ต้องสร้างใหม่" → **cost per token = KPI**
🔗 อุปมา: ร้านกาแฟจำออเดอร์ประจำคุณได้ — ครั้งแรกถามเยอะ ครั้งต่อไปชงเลย
⏱️ ~2 นาที · 🛟 ถ้าตัวเลขไม่ต่าง: ยิงรอบ 3 (cache อุ่นแล้ว) / เพิ่มความยาว system prompt

---

## LAB 4 — "AI ทำงานเป็นทีม" (Multi-Agent / Harnessing)
🎯 **Hook:** "งานนึงไม่ต้องพึ่ง AI ตัวเดียว — ให้มันทำงานเป็นทีม หัวหน้า/คนเขียนโค้ด/คนตรวจ"
🖥️ จอ: terminal + **Phoenix `dgx-spark-lab4`** (โชว์ span tree)
▶️ สด:
1. `uv run tools/lab4_multiagent_demo.py` → orchestrator แตกงาน → coding-agent เขียน `is_prime()` → reviewer-agent ชี้ edge case → final
2. สลับไป **Phoenix** → กาง trace `orchestrator-turn` ให้เห็นลูก: `coding-agent` + `reviewer-agent` (เห็นการส่งต่องาน)
💡 **อ๋อ:** ผลลัพธ์ดีเพราะ **มีคนตรวจ (reviewer)** — ไม่ใช่โมเดลเดียวตอบรวด = นี่คือ "Harness" ที่ห่อโมเดล
🔗 อุปมา: ทีมโปรเจกต์ — PM แบ่งงาน, dev เขียน, QA ตรวจ
⏱️ ~3 นาที · 🛟 ใช้ Phoenix เป็นพระเอก (เห็นโครงสร้างทีมชัดกว่าอ่าน text)

---

## LAB 5 — "agent อันตราย แต่ถูกขังใน sandbox" (Secure & Sandbox) ⭐ เด็ดสุด
🎯 **Hook:** "ปล่อย AI ให้รันคำสั่งเอง = น่ากลัว. มาดูว่า OpenShell sandbox กันยังไง — ลองสั่งให้มันแหกกฎสดๆ"
🖥️ จอ: terminal (`phoenix_sandbox_live.py`) + Phoenix `dgx-spark-sandbox-live` + (ถ้ามีจอที่ 2) **`openshell term`** TUI
▶️ สด — พิมพ์ทีละบรรทัด ให้ผู้เรียนลุ้น:
1. `uv run tools/phoenix_sandbox_live.py`
2. พิมพ์ `curl -sS -w ' [%{http_code}]' https://api.github.com/zen` → ✅ **ALLOWED** (อ่าน GitHub ได้)
3. พิมพ์ `curl -sS -X POST https://api.github.com/repos/octocat/hello-world/issues -d '{}'` → ❌ **BLOCKED สดๆ** (`policy_denied`) — "เขียนไม่ได้!"
4. พิมพ์ `curl -sS https://example.com` → ❌ **BLOCKED** — "ออกเน็ตมั่วไม่ได้ = กันข้อมูลรั่ว"
5. **พลิกเกมสด** (อีก terminal): `openshell policy update lab5-ui --add-allow 'api.github.com:443:POST:/repos/octocat/hello-world/issues' --wait` → ยิง POST เดิมอีกที → **ผ่าน!** (เปลี่ยนกฎทันที ไม่ restart)
6. สลับไป Phoenix → เห็น trace allow/deny ทุก action
💡 **อ๋อ:** **deny-by-default → เปิดสิทธิ์ทีละกฎ → บันทึกทุกอย่าง (audit)** = ปลอดภัยจริง ควบคุมได้
🔗 อุปมา: ห้องทำงานล็อกประตูหมดตั้งแต่แรก จะออกไปไหนต้องขอกุญแจทีละดอก + มีกล้องวงจรปิด
⏱️ ~6 นาที · 🛟 ถ้าพิมพ์สดพลาด: มี `phoenix_agent_demo.py` (agent อัตโนมัติ) เป็นแบ็กอัป + แคปหน้าจอ 403 ไว้

---

## 🔁 จังหวะรวมทั้งวัน
เช้า LAB 1–2 (เห็นเครื่อง+โมเดลทำงาน) → บ่าย LAB 3 (เร็ว/ถูก) → LAB 4 (ทีม) → **LAB 5 (ปลอดภัย = ปิดจบทรงพลัง)** → Phoenix เป็น "จอกลาง" ที่ฉายให้เห็น trace ทุก lab (ร้อยเรื่องเข้าด้วยกัน)
> หมายเหตุ: คำตอบไทยจาก nemotron-nano 8B ยังหยาบ — ถ้าต้องโชว์คุณภาพคำตอบ สลับโมเดลใหญ่/อังกฤษ; แต่**กลไก (เร็ว/ทีม/บล็อก) เห็นภาพชัดอยู่แล้ว**
