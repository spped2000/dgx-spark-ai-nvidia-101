# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "openai>=1.40",
#   "arize-phoenix-otel>=0.6",
#   "openinference-instrumentation-openai>=0.1",
#   "openinference-semantic-conventions>=0.1",
# ]
# ///
"""
phoenix_agent_demo.py — GTC-style "Agent Insights" trace ใน Phoenix
agent (LLM=Ollama) รันบน host แต่ "shell tool" execute เข้าไป *ใน OpenShell sandbox*
→ Phoenix เห็น 1 trace: agent-turn -> [llm plan] [tool GET allowed] [tool POST blocked] [llm reflect]
→ tool POST โดน OpenShell บล็อก (policy_denied) แล้ว LLM สรุปเองว่า "sandbox restricted egress" = ภาพ GTC

ก่อนรัน: Phoenix(:6006) + OpenShell gateway + sandbox 'lab5-ui' (read-only policy) ต้องรันอยู่
รัน: PATH=/tmp/osx/extracted/usr/bin:$PATH uv run tools/phoenix_agent_demo.py
"""
import os, subprocess, tempfile

from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI

PHOENIX = os.environ.get("PHOENIX_ENDPOINT", "http://localhost:6006")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("MODEL", "nemotron-mini")
SANDBOX = os.environ.get("SANDBOX", "lab5-ui")

tp = register(project_name="dgx-spark-course-agent", endpoint=f"{PHOENIX}/v1/traces")
OpenAIInstrumentor().instrument(tracer_provider=tp)
tracer = tp.get_tracer("dgx-agent")
client = OpenAI(base_url=BASE_URL, api_key="EMPTY")

# --- ssh config สำหรับ exec เข้า sandbox (ProxyCommand ใช้ openshell ssh-proxy) ---
cfg = tempfile.mktemp(suffix=".sshcfg")
with open(cfg, "w") as f:
    subprocess.run(["openshell", "sandbox", "ssh-config", SANDBOX], stdout=f, check=True)
HOST = ""
for line in open(cfg):
    if line.strip().startswith("Host "):
        HOST = line.split()[1]; break
print(f"[agent] sandbox={SANDBOX} ssh_host={HOST}")


def run_in_sandbox(cmd: str) -> str:
    """shell tool — รันใน OpenShell sandbox (egress คุมด้วย policy). บันทึกเป็น TOOL span."""
    with tracer.start_as_current_span("run_in_sandbox") as sp:
        sp.set_attribute("openinference.span.kind", "TOOL")
        sp.set_attribute("tool.name", "run_in_sandbox")
        sp.set_attribute("tool.description", "execute a shell command inside the OpenShell sandbox")
        sp.set_attribute("input.value", cmd)
        try:
            r = subprocess.run(["ssh", "-F", cfg, HOST, cmd],
                               capture_output=True, text=True, timeout=30)
            out = (r.stdout + r.stderr).strip()[:600]
        except Exception as e:  # noqa: BLE001
            out = f"ERROR {type(e).__name__}: {e}"
        sp.set_attribute("output.value", out)
        return out


def llm(system: str, user: str) -> str:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=220, temperature=0.4,
    )
    return r.choices[0].message.content


SYS = ("You are an autonomous agent running inside a locked-down OpenShell sandbox with a shell tool. "
       "The sandbox enforces a network policy: only read-only GitHub API access is allowed.")
TASK = ("Goal: (1) read GitHub's zen message, then (2) try to OPEN a new GitHub issue. "
        "Explain what you will do.")

with tracer.start_as_current_span("agent-turn") as root:
    root.set_attribute("openinference.span.kind", "AGENT")
    root.set_attribute("input.value", TASK)

    plan = llm(SYS, TASK)
    print(f"\n[plan]\n{plan}\n")

    print("[tool] GET zen (should be ALLOWED) ...")
    get_out = run_in_sandbox(
        "curl -sS --max-time 8 -w '\\n[HTTP %{http_code}]' https://api.github.com/zen")
    print(f"  -> {get_out[:160]}")

    print("[tool] POST new issue (should be BLOCKED by sandbox) ...")
    post_out = run_in_sandbox(
        "curl -sS --max-time 8 -X POST https://api.github.com/repos/octocat/hello-world/issues -d '{\"title\":\"oops\"}'")
    print(f"  -> {post_out[:200]}")

    reflect = llm(SYS,
        f"Here are my tool results.\nGET zen -> {get_out}\nPOST issue -> {post_out}\n\n"
        "In 3 sentences, explain what succeeded, what was blocked, and why (mention the sandbox egress policy).")
    print(f"\n[reflect]\n{reflect}\n")
    root.set_attribute("output.value", reflect)

print(f"[done] เปิด {PHOENIX} → โปรเจกต์ 'dgx-spark-course-agent' → ดู trace 'agent-turn' (llm + tool GET allowed + tool POST blocked)")
