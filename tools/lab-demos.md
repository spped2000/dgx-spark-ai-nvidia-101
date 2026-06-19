# Live demo ต่อ LAB — validated จริงบน DGX Spark (`spark-4185`, GB10, 2026-06-19)

ทั้ง 5 labs ทดสอบรันจริงบนเครื่องแล้ว (ไม่ใช่แค่เอกสาร). endpoint/บริการที่ใช้: vLLM NGC `:8000` (nemotron-nano) · Ollama `:11434` · Phoenix `:6006` · OpenShell gateway `:8080` · Open WebUI `:3000`.

| LAB | Demo / สคริปต์ | คำสั่งรัน | ✅ ผลที่ validate |
|---|---|---|---|
| **1** serving + 30 คน | `sim_30_learners.py` + `run_dryrun.sh` | `bash tools/run_dryrun.sh` | 30/30, **vLLM NGC ~206 tok/s** (continuous batching), Ollama ~80 |
| **1** access UI | **Open WebUI** | `docker run ... -p 3000:8080 ... open-webui` | chat UI `:3000` ชี้ endpoint, เห็น `nemotron-nano` |
| **2** reasoning toggle | `lab2_reasoning_demo.py` | `BASE_URL=…:8000/v1 MODEL=nemotron-nano uv run tools/lab2_reasoning_demo.py` | thinking ON 600 tok/43s (โชว์วิธีคิด) vs OFF สั้น/เร็ว → Phoenix `dgx-spark-lab2` |
| **3** optimize tokens | `lab3_prefix_cache_demo.py` | `… uv run tools/lab3_prefix_cache_demo.py` | **prefix cache hit: TTFT 328→104 ms (−68%)** |
| **4** multi-agent | `lab4_multiagent_demo.py` | `… uv run tools/lab4_multiagent_demo.py` | orchestrator→coder→reviewer→final, span ครบ → Phoenix `dgx-spark-lab4` |
| **5** secure & sandbox | OpenShell `demo.sh` + `phoenix_sandbox_live.py` + `phoenix_agent_demo.py` | ดู `dryrun-report.md` › LAB 5 recipe | curl 403 → policy → GET ผ่าน/POST บล็อก L7 · **เพิ่มกฎสด** (`policy update --add-allow`) · GTC-style agent trace |
| **live** แชต/แซนด์บ็อกซ์สด | `phoenix_chat_live.py` · `phoenix_sandbox_live.py` | `uv run tools/phoenix_chat_live.py` | พิมพ์สด → คำตอบสตรีม + trace ขึ้น Phoenix ทันที |

> ⚠️ คุณภาพคำตอบไทยจาก nemotron-nano 8B ยังหยาบ (โมเดลเล็ก) — **กลไกทุก lab ใช้ได้จริง**; วันงานสลับโมเดลใหญ่ขึ้น (เช่น Nemotron Super / NVFP4) ให้คำตอบดีกว่าได้
> โมเดล/พอร์ต/คำสั่งเริ่ม service ทั้งหมด อยู่ใน `dryrun-report.md` (recipe) + `observability.md` (Phoenix/TUI)
