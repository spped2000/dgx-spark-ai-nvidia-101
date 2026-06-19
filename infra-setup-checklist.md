# Infra & Setup Checklist — DGX Spark Course (1 Day, 30 Users, No-Code)

> **ใช้ไฟล์นี้ทำอะไร:** เช็กลิสต์เตรียมงานทั้งหมดสำหรับวันเสาร์ที่ 20 มิ.ย. 2026 (10:00–16:00 ที่ Cleverse Rama9, ~30 คน) บน **DGX Spark จริง 1 เครื่อง**. ติ๊ก `[ ]` ให้ครบทุกข้อก่อนวันงาน. ข้อที่มี 🔒 คือ **hard gate** — ถ้ายังไม่ผ่าน **ห้ามเริ่มสอน**.
>
> **อุปมาให้เห็นภาพ:** DGX Spark เครื่องนี้เหมือน **ร้านกาแฟร้านเดียว** ที่ต้องเสิร์ฟลูกค้า 30 คนพร้อมกัน. เราจะไม่เปิดร้านเพิ่ม (มีเครื่องเดียว) แต่จะจัด **บาริสต้าคนเดียวทำหลายแก้วพร้อมกัน** (continuous batching), **จำสูตรที่สั่งซ้ำ** (prefix cache), และ **เข้าคิวเป็นเวฟ** เพื่อไม่ให้ออเดอร์ล้น. ทั้งหมดนี้คือสิ่งที่เช็กลิสต์นี้เตรียมไว้.
>
> **กฎเหล็กของไฟล์นี้ (อย่าลืม):**
> - มี DGX Spark เครื่องเดียว = GB10, 128GB unified memory @ ~273 GB/s, ไม่มี MIG. คอขวดจริง = **memory bandwidth** ไม่ใช่ความจุ.
> - **โหลดโมเดลเดียวที่แชร์ทั้งห้อง** เท่านั้น. ห้ามให้ 30 คนโหลดคนละตัว และห้ามโหลดโมเดลที่สองพร้อมกัน → OOM ทันที.
> - **ตัวเลข performance ทั้งหมดต้องวัดจริงใน dry-run** ก่อนเชื่อ. อย่าเอาตัวเลขในไฟล์นี้ไปสัญญากับผู้เรียนก่อนวัด.

---

## ภาพรวมสถาปัตยกรรม (อ่านก่อนเริ่มติ๊ก) / Architecture Overview

ทุกคนใน 1 ห้อง → ต่อ **endpoint เดียว** → DGX Spark เครื่องเดียว:

```
[30 laptops] --LAN/Wi-Fi--> [JupyterHub per-user]   ┐
                            [Open WebUI front-end]   ├─> 1 SHARED ENDPOINT (vLLM/NIM, port 8000)
                                                     ┘        |
                                                     [Nemotron Nano / 7-9B class, FP8/NVFP4]
                                                              |
                                              [DGX Spark — GB10, 128GB unified, sm_121]
```

- **JupyterHub** = ให้ผู้เรียนแต่ละคนมี container/kernel ส่วนตัว (สำหรับ lab ที่ต้องรันเซลล์)
- **Open WebUI** = หน้าแชต (ทุกคนชี้ไป endpoint เดียวกัน)
- **1 shared endpoint (vLLM หรือ NIM)** = หัวใจของการเสิร์ฟ 30 คนพร้อมกัน

> **อุปมา:** JupyterHub = โต๊ะส่วนตัวของแต่ละคน, Open WebUI = เมนูสั่งอาหารหน้าร้าน, แต่ **ครัวมีครัวเดียว** (shared endpoint บน DGX Spark). เราตกแต่งโต๊ะให้ครบ 30 ตัวได้ แต่ครัวต้องจัดคิวให้ดี.

---

## 1. User Accounts — 30 บัญชี / 30 User Accounts

**เป้าหมาย:** ผู้เรียน 30 คน login ได้ภายในนาทีแรก ไม่ต้องตั้งค่าอะไรเอง (no-code).

### 1.1 Pre-provision บัญชี
- [ ] สร้าง **JupyterHub** พร้อม per-user container/kernel ครบ **30 บัญชี** (pre-create ล่วงหน้า ไม่สร้างสดหน้างาน)
- [ ] ตั้ง **Open WebUI** เป็นหน้าแชต ชี้ไป **shared endpoint เดียว** (ไม่ใช่ให้แต่ละคนตั้ง endpoint เอง)
- [ ] ยืนยันว่าทุกบัญชีเห็น notebook ของทุก lab (LAB1–LAB5) โหลดค้างไว้แล้ว
- [ ] ตั้ง resource limit ต่อ user container (CPU/RAM เบา ๆ) ให้ JupyterHub เอง ไม่ให้คนเดียวกินเครื่องหมด

### 1.2 การ์ด user/pass (printed cards)
- [ ] พิมพ์ **การ์ด 30 ใบ** แต่ละใบมี: **URL** (LAN address ของ Open WebUI/JupyterHub) + **username** + **password**
- [ ] เขียน URL ตัวใหญ่ชัด ๆ บนการ์ด (มือใหม่พิมพ์ผิดบ่อย) — แนะนำใส่ **QR code** ของ URL ด้วย
- [ ] ทดสอบทุก user/pass ว่า login ได้จริง **ก่อน** พิมพ์การ์ด (อย่าพิมพ์แล้วค่อยเทส)

### 1.3 การ์ดสำรอง + ขั้นตอน login ล่ม / Spare cards + login failure runbook
- [ ] เตรียม **การ์ดสำรอง 5 ใบ** (บัญชี #31–#35 ที่ pre-create ไว้แล้วและเทสแล้ว) สำหรับกรณีการ์ดหาย/บัญชีมีปัญหา
- [ ] ติดประกาศ/บอกผู้ช่วย **ขั้นตอนแก้ login ล่ม** ตามลำดับ:
  1. พิมพ์ user/pass ผิด → ให้ดูการ์ดอีกครั้ง, ระวังตัวพิมพ์เล็ก/ใหญ่ และช่องว่างท้ายบรรทัด
  2. URL ผิด → ชี้ QR code / พิมพ์ตามการ์ดทีละตัว
  3. บัญชียัง login ไม่ได้ → **แจกการ์ดสำรอง 1 ใบ** (บัญชี #31+) แทนทันที อย่าเสียเวลา debug หน้างาน
  4. ทั้งห้อง login ไม่ได้ → เป็นปัญหาเครือข่าย/endpoint ดูหัวข้อ 4 (Network) และ 6 (Fallback)
- [ ] ระบุ **ผู้ช่วย 1 คน** ดูแลเรื่อง login โดยเฉพาะ ช่วงลงทะเบียน 10:00–10:25

---

## 2. Models — Pre-pull โมเดล / Pre-pull Models

**เป้าหมาย:** โมเดลทุกตัวต้อง **โหลดมาไว้บนเครื่องล่วงหน้า** (pre-pull) ห้ามพึ่งเน็ตดาวน์โหลดสดหน้างาน.

### 2.1 โมเดลหลัก (shared ทั้งห้อง) / Main shared model
- [ ] Pre-pull **โมเดลเดียวที่แชร์ทั้งห้อง** = **Nemotron Nano (30B-A3B MoE)** หรือคลาส **7–9B**, quantize **FP8 หรือ NVFP4**
- [ ] เสิร์ฟผ่าน **vLLM** (ตัวหลัก) ด้วยคำสั่งฐาน:
  ```bash
  vllm serve <model> \
    --gpu-memory-utilization 0.85 \
    --max-num-seqs 32 \
    --max-model-len 4096 \
    --kv-cache-dtype fp8
  ```
  > หมายเหตุ: `--max-num-seqs 32` รองรับ 30 คนพร้อมกัน; `--max-model-len` เริ่มที่ 4096 (ขยายได้ถึง 8192 ถ้า dry-run ยืนยันว่าไม่ OOM)
- [ ] **ทางเลือก NIM** (ติดตั้งง่ายกว่า): pre-pull image และทดสอบ
  ```bash
  docker run --gpus all --shm-size=16GB \
    -e NGC_API_KEY=$NGC_API_KEY \
    -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
    -p 8000:8000 \
    nvcr.io/nim/meta/llama-3.1-8b-instruct-dgx-spark:latest
  ```
  > endpoint OpenAI-compatible: `/v1/chat/completions` ที่พอร์ต `8000`
- [ ] ⚠️ **ถ้าใช้ NVFP4 → ต้องเสิร์ฟผ่าน TensorRT-LLM หรือ NIM เท่านั้น** (vLLM ปกติใช้ FP8). เลือกให้สอดคล้องกับสิ่งที่ pre-pull
- [ ] ยืนยัน **น้ำหนักโมเดลเหลือพื้นที่ให้ KV cache เยอะ** (โมเดล 4–16GB จาก 128GB) → ที่เหลือเป็น KV cache สำหรับ 30 concurrent

### 2.2 LM Studio (สำหรับ first-win demo LAB 1) / LM Studio first-win
- [ ] ติดตั้ง LM Studio headless `llmster` บน Spark ล่วงหน้า:
  ```bash
  curl -fsSL https://lmstudio.ai/install.sh | bash
  lms get nvidia/nemotron-3-nano-omni
  lms load nvidia/nemotron-3-nano-omni
  lms server start --bind 0.0.0.0 --port 1234
  ```
  > GUI ทางเลือก: Developer → Serve on Local Network
- [ ] ⚠️ **LM Link จำกัด ~2 users** → ใช้แค่โชว์ "first win" บนจอ instructor; สำหรับ 30 คนใช้ **shared LAN endpoint** (vLLM/NIM) ตามข้อ 2.1 เสมอ
- [ ] โมเดลตัวอย่าง playbook = **Nemotron 3 Nano Omni (~65–70GB)** — ยืนยันว่าโหลดได้และพอดี 128GB

### 2.3 Ollama เล็ก (สำหรับ LAB 4 multi-agent) / Small Ollama for LAB 4
- [ ] Pre-pull **โมเดลเล็กผ่าน Ollama** สำหรับ LAB 4 (multi-agent loop ที่ contention สูงสุด)
- [ ] ⚠️ LAB 4 ต้องจำกัด: **2–3 steps, max_tokens 128–256, แบ่งเวฟ/คิว** เพื่อไม่ให้แย่งทรัพยากรกับ endpoint หลัก

### 2.4 Offline assets — เซฟทุกอย่างไว้ในเครื่อง / Save all assets offline
- [ ] เซฟ **วิดีโอ G1 humanoid walking (RL, MuJoCo-Warp)** ไว้ในเครื่อง (สำหรับ Physical AI window)
- [ ] เซฟ **GTC Taipei 2026 recap board** (รูปจริง 20 ใบใน `ref_nvidia_gtc/`) เป็น offline asset
- [ ] เซฟสไลด์อ้างอิง (AI-Q Open Agent Blueprint, OpenShell diagram) ไว้ฉายแบบ offline
- [ ] ⚠️ **ห้ามพึ่งเน็ตสดสำหรับ asset ใด ๆ** — ถ้าเน็ตล่มต้องฉายได้หมด

---

## 3. กันแย่งทรัพยากร / Resource Contention Controls

**เป้าหมาย:** ทำให้ 30 คนพร้อมกันบนเครื่องเดียว **ช้าลงได้ แต่ห้าม OOM / ห้ามค้าง**. "ช้าตอนพร้อมกัน = บทเรียน Pillar 1 ไม่ใช่บั๊ก".

> **อุปมา:** บาริสต้าคนเดียวทำกาแฟ 30 แก้ว — เคล็ดลับคือ **ทำหลายแก้วในรอบเดียว** (batching), **จำสูตรที่ซ้ำ** (prefix cache), และ **ปล่อยคิวเป็นรอบ ๆ** (เวฟ) ไม่ใช่ปล่อย 30 คนดันประตูพร้อมกัน.

- [ ] ใช้ **1 shared endpoint** เท่านั้น (ไม่ใช่ endpoint ต่อคน)
- [ ] เปิด **continuous batching** (vLLM ทำให้อัตโนมัติด้วย PagedAttention) — รวม request หลายคนเป็น batch เดียว
- [ ] เปิด **prefix caching / KV cache** — ทำให้ prompt ซ้ำ (เช่น system prompt เดียวทั้งห้อง) hit cache เร็วฮวบ
- [ ] **Cap context** (`--max-model-len`) และ **cap max_tokens** ต่อ request เพื่อกันคนเดียวกินทั้งคิว
- [ ] **แบ่งเวฟ (waves)** สำหรับ lab ที่หนัก: LAB 2 (`/think` vs `/no_think`) จัด 2 เวฟ; LAB 4 (multi-agent) แบ่งเวฟ/คิว + มี fallback
- [ ] 🚫 **ห้ามโหลดโมเดลที่สองพร้อมกัน** (เช่น NemoGuard NIM 8B ตัวที่สอง = กิน 16–20GB → OOM). LAB 5 ใช้ **self-check rail บนโมเดลเดิม**
- [ ] 🚫 **ห้ามให้ 30 คนโหลดโมเดลคนละตัว** — ทุกคนชี้ shared endpoint เดียว
- [ ] เตรียมสคริปต์ลด batch / เพิ่มคิว ไว้ใช้ทันทีถ้า dashboard เห็นเครื่องเริ่มตึง (ดู runbook)

---

## 4. Network — เครือข่าย / Networking

**เป้าหมาย:** LAN/Wi-Fi รองรับ 30 เครื่องพร้อมกัน และ endpoint เข้าถึงได้เฉพาะใน LAN.

- [ ] ยืนยัน **LAN/Wi-Fi ที่ Cleverse Rama9 รองรับ 30 เครื่อง** พร้อมกัน (ทดสอบจำนวน client จริง)
- [ ] **Bind endpoint ใน LAN เท่านั้น** — ระวัง bind `0.0.0.0` แล้วเปิดสู่ภายนอกโดยไม่ตั้งใจ; จำกัด access เฉพาะวงในห้อง
- [ ] จด **LAN IP/URL ของ DGX Spark** ที่จะใส่ในการ์ด user/pass (ข้อ 1.2) — ต้องเป็น address ที่ทุก laptop ในห้องเข้าถึงได้
- [ ] ทดสอบจาก laptop ตัวอย่างว่าเปิด URL แล้วถึง endpoint จริงผ่าน LAN
- [ ] เตรียม **cloud / laptop fallback** สำหรับ demo ที่เสี่ยง (กรณี endpoint หลักล่ม — ดูข้อ 6)

---

## 5. Facilitator Pre-flight (เช้าวันงาน) / Morning Pre-flight

**เป้าหมาย:** ก่อนผู้เรียนเข้า ทุกอย่างพร้อมและ "warm" แล้ว.

- [ ] **Re-warm โมเดลหลัก** (ยิง request อุ่นเครื่อง ให้ weights/cache อยู่ใน memory)
- [ ] เช็ก **30 kernels / containers** ของ JupyterHub ว่าขึ้นครบและตอบสนอง
- [ ] โหลด **notebook ของทุก lab (LAB1–LAB5)** ค้างไว้ในทุกบัญชี
- [ ] เปิด **dashboard (Triton metrics → Prometheus → Grafana)** ฉายขึ้นจอ — โชว์ GPU/memory/tok-s แบบสด
- [ ] เปิด offline assets (วิดีโอ, GTC recap) ทดสอบฉายได้
- [ ] ทดสอบ **concurrency demo** (LAB 1 "3-2-1 ยิงพร้อมกัน") ครั้งสุดท้ายว่าเห็น batching บน dashboard

---

## 6. Fallback & Failure Recovery — แผนสำรอง / Backup Plans

**เป้าหมาย:** มีแผน B ทุกจุดเสี่ยง เพื่อไม่ให้คอร์สสะดุด.

- [ ] **DGX Spark overload** (เครื่องตึง) → ลด batch / เพิ่มคิว / แบ่งเวฟผู้เรียน
- [ ] **OOM** → restart เสิร์ฟ **โมเดลเดียว** (ยืนยันไม่มีโมเดลที่สองค้างอยู่)
- [ ] **เน็ตล่ม** → สลับไปใช้ **offline asset** ทั้งหมด (วิดีโอ/recap board)
- [ ] **Demo สด fail** → มี **คลิปสำรอง** ของ demo สำคัญทุกตัว (โดยเฉพาะ LAB 5 OpenShell block)
- [ ] **ช้ากว่าแผน** → ตัด **LAB 4 full multi-agent loop** เหลือให้ instructor โชว์ครั้งเดียว
- [ ] **endpoint หลักล่ม** → สลับไป **cloud / laptop fallback** สำหรับ demo ที่เตรียมไว้
- [ ] 🔴 **ห้ามรัน `curl … | bash` สดต่อหน้าผู้เรียนจาก URL ที่ยังไม่ยืนยัน** — LAB 5 ใช้คำสั่ง OpenShell ที่ verify แล้วเท่านั้น (`curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh`); ติดตั้งจริง **ก่อน** วันงาน ไม่ใช่สดหน้างาน

---

## 7. 🔒 DRY-RUN HARD GATE (1 วันก่อนงาน) — ต้องผ่านก่อนสอน / DRY-RUN HARD GATE (D-1)

> **🔒 นี่คือ hard gate. ถ้า dry-run ไม่ผ่านครบทุกข้อด้านล่าง = ยังไม่พร้อมสอน ต้องแก้ก่อน.**
> เหตุผล: ตัวเลข performance ทั้งหมดยังไม่ยืนยัน — **ต้องวัดจริง** บนเครื่องจริง ด้วยภาระจริง 30 คน ก่อนเชื่อ.

### 7.1 ยิงพร้อมกัน 30 บัญชี / 30 accounts concurrent load
- [ ] ให้ **30 บัญชี login พร้อมกัน** (จำลองผู้เรียนจริง) — ยืนยันทุกบัญชีเข้าได้
- [ ] **ยิง prompt พร้อมกันทั้ง 30 บัญชี** (จำลองโมเมนต์ "3-2-1 Send พร้อมกัน" ใน LAB 1)

### 7.2 วัด tok/s จริง / Measure real tok/s
- [ ] **วัด tok/s จริง** ตอน 30 คนยิงพร้อมกัน (worst case) — บันทึกตัวเลขไว้
  > ค่าอ้างอิงจากแผน: worst case ~12 tok/s/คน, ปกติ (burst) ~30–46 tok/s/คน — **ต้องยืนยันด้วยตัวเลขที่วัดได้จริง ไม่ใช่ลอกตัวเลขนี้**
- [ ] วัด **TTFT (time to first token)** ด้วย เพื่อใช้ใน LAB 3 (Optimize Tokens)
- [ ] ยืนยัน **prefix cache hit** เห็นผลจริง (prompt ซ้ำเร็วขึ้นชัดเจน) สำหรับ LAB 3

### 7.3 ยืนยันไม่ OOM / Confirm no OOM
- [ ] 🔒 **ยืนยันไม่ OOM** ตลอดการยิงพร้อมกัน 30 คน — memory ไม่เต็ม, เสิร์ฟไม่ crash
- [ ] ยืนยันว่ามี **โมเดลเดียว** โหลดอยู่ (ไม่มีโมเดลที่สองแอบค้าง)

### 7.4 รันทุก lab จริง / Run every lab end-to-end
- [ ] 🔒 **รัน LAB 1–LAB 5 ตั้งแต่ต้นจนจบ** ด้วยบัญชีผู้เรียนจริง 1 บัญชี + พร้อมกับ load 30 บัญชี
- [ ] **LAB 5 ทดสอบเฉพาะ:** ยืนยัน **OpenShell block `curl` ออกเน็ต (403)** จริง → แก้ YAML policy เปิด read-only → **GET ผ่าน / POST ถูกบล็อก** + เห็น **audit trail**
- [ ] **LAB 5 guardrail:** ยืนยัน NeMo Guardrails block jailbreak ได้ + ตั้ง **auto re-enable** กันลืมเปิด config ทิ้งไว้
- [ ] **ทดสอบ offline:** เปิด asset offline ทั้งหมด (วิดีโอ, GTC recap board) **โดยถอดเน็ต** — ต้องฉายได้หมด

### 7.5 Sign-off
- [ ] 🔒 ทุกข้อ 7.1–7.4 ผ่าน → **บันทึกตัวเลขที่วัดได้** (tok/s, TTFT, memory peak) และ instructor sign-off ว่าพร้อมสอน

---

## 8. สรุปกฎเหล็กก่อนวันงาน / Pre-Event Hard Rules (Quick Recap)

- [ ] 1 เครื่อง · 1 shared endpoint · **1 โมเดลเท่านั้น** (ห้ามโมเดลที่สอง = OOM)
- [ ] ตัวเลข performance = **วัดจริงใน dry-run** (ข้อ 7) ไม่ใช่เดา
- [ ] การ์ด 30 ใบ + **สำรอง 5 ใบ** เทสแล้วทุกใบ
- [ ] Offline assets ครบ (เน็ตล่มก็สอนต่อได้)
- [ ] 🔴 ไม่รัน `curl | bash` สดจาก URL ที่ยังไม่ยืนยัน
- [ ] 🔒 **Dry-run hard gate ผ่าน** → ถึงเริ่มสอนได้

---

## สิ่งที่ผู้สอนต้องเช็ก/เติมเอง / Instructor To-Verify (ก่อนพิมพ์การ์ด/ก่อนวันงาน)

> รายการนี้เป็น **ค่าจริงเฉพาะสถานที่/เครื่อง** ที่แผนไม่ได้ระบุ — ผู้สอนต้องเติมเองและยืนยันก่อนงาน:

1. **LAN IP/URL จริง** ของ DGX Spark ที่ Cleverse Rama9 (ใส่ลงการ์ด user/pass + QR) — แผนไม่ได้ระบุ address
2. **เลือก serving stack สุดท้าย:** vLLM (FP8) **หรือ** NIM/TensorRT-LLM (ถ้าต้องการ NVFP4) — ต้องเลือกให้ตรงกับโมเดลที่ pre-pull
3. **ชื่อ/ขนาดโมเดลหลักจริง** ที่จะใช้ (Nemotron Nano 30B-A3B หรือคลาส 7–9B) + ชื่อ tag ที่ pre-pull จริง
4. **NGC_API_KEY และ LOCAL_NIM_CACHE** (ถ้าใช้ NIM) — เป็นค่าเฉพาะของผู้สอน
5. **ตัวเลขจาก dry-run** (tok/s, TTFT, memory peak) — ต้องวัดเองวันก่อนงาน; ค่าในไฟล์นี้เป็นเพียงค่าอ้างอิงจากแผน
6. **ความจุ Wi-Fi/LAN จริง** ของสถานที่ว่ารับ 30 เครื่องไหว — ต้องเทสจำนวน client จริง
7. **Cloud fallback endpoint** ที่จะใช้ (ถ้ามี) — แผนระบุว่าให้เตรียม แต่ไม่ระบุผู้ให้บริการ
