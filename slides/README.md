# Slides — DGX Spark course (bilingual TH/EN)

ไฟล์ในโฟลเดอร์นี้ (สร้างจาก [`../slides-outline.md`](../slides-outline.md)):

| ไฟล์ | คือ |
|---|---|
| **`deck.pptx`** | สไลด์พร้อมใช้ — เปิดใน **PowerPoint / Google Slides / Keynote / LibreOffice** ได้เลย (76 สไลด์, 12 โมดูล, ฟอนต์ Tahoma รองรับไทย) |
| `deck.md` | **Marp** markdown (source แก้ง่าย + มี speaker notes) |
| `slides.json` | structured source (title/bullets/notes) ที่ใช้ build `.pptx` |
| `build_pptx.py` | สคริปต์ build `slides.json` → `deck.pptx` |

## แก้/สร้างใหม่
- **แก้เนื้อหา** → แก้ `slides.json` แล้ว rebuild: `uv run slides/build_pptx.py` (จากโฟลเดอร์ `course/`)
- **เรนเดอร์ Marp** เป็น PDF/HTML/PPTX (สวยกว่า, ต้องมี Node): `npx @marp-team/marp-cli slides/deck.md -o slides/deck.pdf` หรือใช้ส่วนขยาย **Marp for VS Code**

## หมายเหตุ
- โครงสร้าง 12 โมดูล: M0 แกน "Agent = Model + Harness" · M1–5 พื้นฐาน (เช้า) · M6–9 สามเสาหลัก + signed skills (บ่าย) · M10–11 GTC recap + ปิดท้าย
- ก่อนใช้จริง: เติมตัวเลข tok/s/TTFT ที่วัดจาก dry-run, ยืนยันสินค้า forward-dated พูดว่า "as announced at GTC" (ดู `../README.md` › pre-event checklist)
