# 📊 Triton-style control-room dashboard (Prometheus + Grafana)
"watch 30 of us live" — scrape Prometheus metrics ที่ vLLM/NIM/Triton expose เหมือนกัน (ที่นี่ scrape vLLM `:8000`) → Grafana dashboard ✅ validated

## รัน
```bash
cd tools/monitoring
docker compose up -d
```
เปิด **http://localhost:3001** (anonymous, ไม่ต้อง login) → dashboard **"DGX Spark — vLLM serving"** (refresh 2s)
- Prometheus: http://localhost:9090

## พาเนล
- **Concurrent requests** — running (กำลังตอบ) vs waiting (เข้าคิว) → เห็นคิวพุ่งตอน 30 คนยิงพร้อมกัน
- **Throughput** — generation/prompt tokens/sec
- **TTFT p50/p95** — เวลาถึง token แรก
- **GPU KV-cache usage %** — เมมโมรีที่ใช้แคช

## ใช้ในคลาส (LAB 1 / 3)
ฉาย :3001 ขึ้นจอ → รัน `uv run tools/sim_30_learners.py --users 30` → **ดูกราฟ requests/throughput พุ่งสดๆ** = "เครื่องเดียวเสิร์ฟ 30 คน" จับต้องได้ (= บทบาท Triton control-room ในคอร์ส)
> เปลี่ยน scrape target เป็น NIM/Triton ได้ที่ `prometheus.yml` (ทุกตัว expose Prometheus /metrics เหมือนกัน)
