# 🧑‍🎓 Learner Portal — JupyterHub + DockerSpawner (sandbox ต่อคน)
ผู้เรียน 30 คน login → ได้ **container/sandbox ของตัวเอง** (FS/process/notebook แยก) → เรียก **vLLM กลาง `:8000`** ร่วมกัน (continuous batching รับ 30 คน) — ✅ validated บน DGX Spark

## สถาปัตยกรรม
```
30 learners ──login(:8888)──> JupyterHub ──DockerSpawner──> jupyter-<user> (container ของแต่ละคน)
                                                                  └──OPENAI_BASE_URL──> vLLM :8000 (กลาง)
```
แต่ละ container เบา (CPU, mem_limit 2G) — **ไม่โหลดโมเดลเอง** → ไม่ OOM. โมเดลหนักอยู่ที่ vLLM ตัวเดียวที่แชร์

## ติดตั้ง + รัน
```bash
cd portal
docker build -f Dockerfile.singleuser -t dgx-singleuser:latest .   # sandbox image (minimal-notebook + openai)
docker compose up -d --build                                       # JupyterHub :8888
```
เปิด **http://localhost:8888** → login: **username อะไรก็ได้** (เช่น student01) + รหัส **`dgxspark2026`** → ได้ sandbox + เปิดโน้ตบุ๊ก `labs/00_welcome.ipynb` อัตโนมัติ

## provision 30 บัญชี
- ใช้ **DummyAuthenticator**: แจกแค่ *username (student01..30)* + *รหัสรวม* (`WORKSHOP_PASSWORD`) — ใครพิมพ์ username อะไรก็ได้ container แยกตาม username
- เปลี่ยนรหัส/หาผู้ดูแล: env `WORKSHOP_PASSWORD`, `ADMIN_TOKEN` ใน `docker-compose.yml`
- โน้ตบุ๊ก lab: วางไฟล์ `.ipynb` ใน `portal/notebooks/` → mount เข้า `~/labs` ของทุกคน (read-only)

## ✅ Validated (จำลอง 5 คน)
spawn student01..05 → container ขึ้นครบ 5/5 (healthy) · student01/03 เรียก vLLM ได้ ("2+2=4") · whoami/hostname แยกกันจริง → สเกล 30 ได้ (CPU เบา + GPU แชร์ตัวเดียว)

## เทส/จำลอง headless (admin API)
```bash
TOKEN=dgxadmintoken123; B=http://localhost:8888/hub/api
curl -s -X POST -H "Authorization: token $TOKEN" $B/users/student01            # สร้าง user
curl -s -X POST -H "Authorization: token $TOKEN" $B/users/student01/server     # spawn sandbox
docker ps --filter name=jupyter-                                               # ดู container
curl -s -X DELETE -H "Authorization: token $TOKEN" $B/users/student01/server   # หยุด/เก็บ
```
## ⚠️ ก่อนใช้จริง
- เปลี่ยน `WORKSHOP_PASSWORD` + `ADMIN_TOKEN` (ค่าใน repo เป็น demo) · pre-pull `dgx-singleuser` ไว้ให้ spawn เร็ว · ตั้ง `mem_limit`/`cpu_limit` ตามจำนวนคน
