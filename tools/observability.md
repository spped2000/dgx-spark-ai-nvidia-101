# UI & Observability สำหรับ LAB (validated live บน DGX Spark)

สองหน้าจอ "UI" ที่ใช้ฉายให้ผู้เรียนเห็นการทำงานจริง (ตรงกับรูป GTC):

## 1) OpenShell TUI — `openshell term` (เสริม LAB 5: Secure & Sandbox)
หน้าจอ dashboard แบบ terminal (ratatui) = หน้าจอ **"OPENSHELL [ALPHA]"** ในรูป GTC — โชว์ sandbox / policy / logs (allow·deny) แบบ real-time

```bash
# gateway ต้องรันอยู่ + register แล้ว (ดู dryrun-report.md › LAB 5 recipe)
openshell term            # หรือ: openshell term --theme dark
```
- แท็บ **Sandboxes**: รายการ sandbox + phase (Ready)
- แท็บ **Policy**: policy ที่ active (เช่น github_api read-only)
- แท็บ **Logs**: บรรทัด `action=deny` / `action=allow` วิ่งสดเมื่อ agent/curl ยิงออก
- **ใช้ในคลาส:** ฉาย `openshell term` ขึ้นจอ แล้วรัน demo → ผู้เรียนเห็น curl โดน deny แดงๆ สดๆ

## 2) Phoenix (Arize) — web UI `:6006` (เสริม LAB 3: Optimize Tokens)
หน้าจอ observability = **"Agent Insights"** ในรูป GTC — โชว์ trace/span + **tokens · latency · cost** ต่อ request

```bash
# รัน Phoenix
docker run -d --name phoenix -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
# ส่ง trace จาก endpoint จริง (instrument OpenAI client → Phoenix)
uv run tools/phoenix_trace_demo.py        # LLM tracing ล้วน
```

### GTC-style "Agent Insights" (agent + sandbox tools → Phoenix)
`tools/phoenix_agent_demo.py` — agent (สมอง = vLLM/Ollama Nemotron) ที่มี shell tool รัน **ใน OpenShell sandbox** → Phoenix เห็น trace `agent-turn` ที่มี tool-call โดน sandbox บล็อก (เหมือนรูป GTC):
```bash
PATH=/tmp/osx/extracted/usr/bin:$PATH \
  BASE_URL=http://localhost:8000/v1 MODEL=nemotron-nano \
  uv run tools/phoenix_agent_demo.py
# Phoenix → project 'dgx-spark-course-agent' → trace: llm + tool(GET allowed) + tool(POST blocked) + reflect
```
- เปิด **http://localhost:6006** → โปรเจกต์ `dgx-spark-course`
- เห็นแต่ละ request: prompt/completion/total tokens, latency, model
- **ใช้ในคลาส:** ฉาย Phoenix ตอน LAB 3 → ชี้ให้เห็น "token ที่ประหยัด = เงินที่ประหยัด" (cost per token = KPI), prefix-cache hit ทำ latency ลด

> ✅ ทั้งสองทดสอบรันจริงบน DGX Spark (`spark-4185`, GB10) แล้ว — non-root ผ่าน Docker
