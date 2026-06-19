# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "openai>=1.40",
#   "arize-phoenix-otel>=0.6",
#   "openinference-instrumentation-openai>=0.1",
# ]
# ///
"""
phoenix_sandbox_live.py — LIVE scenario: พิมพ์คำสั่งสดๆ → รันใน OpenShell sandbox
→ เห็น ✅ ALLOWED / ❌ BLOCKED ทันที + ทุก turn เป็น trace ใน Phoenix

โหมด:
  - พิมพ์ shell command ตรงๆ:   curl -sS https://api.github.com/zen
  - หรือให้ agent คิดให้:        /ask ลองเปิด issue ใหม่บน github

ต้องมี: Phoenix(:6006) + OpenShell gateway + sandbox (ดีฟอลต์ 'lab5-ui', read-only policy) + LLM endpoint
รันสด (ในเทอร์มินอลคุณ):
  PATH=$HOME/.local/bin:/tmp/osx/extracted/usr/bin:$PATH \
    uv run /home/agicafet/Documents/dgx1/course/tools/phoenix_sandbox_live.py
ออก: exit / Ctrl-D
"""
import os, subprocess, tempfile, sys

from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI

PHOENIX = os.environ.get("PHOENIX_ENDPOINT", "http://localhost:6006")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000/v1")
MODEL = os.environ.get("MODEL", "nemotron-nano")
SANDBOX = os.environ.get("SANDBOX", "lab5-ui")
PROJECT = os.environ.get("PROJECT", "dgx-spark-sandbox-live")

G, R, Y, B, X = "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m"

tp = register(project_name=PROJECT, endpoint=f"{PHOENIX}/v1/traces")
OpenAIInstrumentor().instrument(tracer_provider=tp)
tracer = tp.get_tracer("sandbox-live")
client = OpenAI(base_url=BASE_URL, api_key="EMPTY")

# ssh config เข้า sandbox (ProxyCommand ใช้ openshell ssh-proxy → ต้องมี openshell ใน PATH)
cfg = tempfile.mktemp(suffix=".sshcfg")
with open(cfg, "w") as f:
    subprocess.run(["openshell", "sandbox", "ssh-config", SANDBOX], stdout=f, check=True)
HOST = next((l.split()[1] for l in open(cfg) if l.strip().startswith("Host ")), "")

BLOCK_MARKERS = ("policy_denied", "403 from proxy", "Received HTTP code 403",
                 "not permitted by policy", "curl: (56)", "curl: (7)", "Could not resolve")


def exec_in_sandbox(cmd: str):
    with tracer.start_as_current_span("run_in_sandbox") as sp:
        sp.set_attribute("openinference.span.kind", "TOOL")
        sp.set_attribute("tool.name", "sandbox_shell")
        sp.set_attribute("input.value", cmd)
        try:
            r = subprocess.run(["ssh", "-F", cfg, HOST, cmd],
                               capture_output=True, text=True, timeout=30)
            out = (r.stdout + r.stderr).strip()
        except Exception as e:  # noqa: BLE001
            out = f"ERROR {type(e).__name__}: {e}"
        blocked = any(m in out for m in BLOCK_MARKERS)
        sp.set_attribute("output.value", out[:800])
        sp.set_attribute("sandbox.blocked", blocked)
        return out, blocked


def ask_agent_for_cmd(goal: str) -> str:
    r = client.chat.completions.create(
        model=MODEL, max_tokens=120, temperature=0.2,
        messages=[
            {"role": "system", "content": "Convert the user's goal into EXACTLY ONE shell command using curl. "
             "Output ONLY the command, no markdown, no explanation."},
            {"role": "user", "content": goal},
        ])
    cmd = (r.choices[0].message.content or "").strip().strip("`")
    for line in cmd.splitlines():
        line = line.strip().lstrip("$ ").strip()
        if line and not line.startswith("#"):
            return line
    return "curl -sS https://api.github.com/zen"


print(f"\n{B}OpenShell LIVE sandbox{X}  sandbox={SANDBOX}  policy=read-only github_api")
print(f"LLM={MODEL}@{BASE_URL}  ·  Phoenix={PHOENIX} → project '{PROJECT}'")
print(f"{Y}ลองพิมพ์:{X}")
print("  curl -sS -w ' [%{http_code}]' https://api.github.com/zen          # ✅ allowed")
print("  curl -sS -X POST https://api.github.com/repos/octocat/hello-world/issues -d '{}'   # ❌ L7 block")
print("  curl -sS --max-time 6 https://example.com                          # ❌ host ไม่อยู่ใน policy")
print("  /ask ลองดึงข้อมูล user octocat จาก github                          # agent คิดคำสั่งให้")
print("ออก: exit / Ctrl-D\n")

while True:
    try:
        line = input(f"{B}sandbox>{X} ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nbye 👋"); break
    if not line:
        continue
    if line.lower() in ("exit", "quit", "ออก"):
        print("bye 👋"); break

    with tracer.start_as_current_span("sandbox-turn") as turn:
        turn.set_attribute("openinference.span.kind", "AGENT")
        turn.set_attribute("input.value", line)
        if line.startswith("/ask "):
            cmd = ask_agent_for_cmd(line[5:].strip())
            print(f"  {Y}agent →{X} {cmd}")
        else:
            cmd = line
        out, blocked = exec_in_sandbox(cmd)
        verdict = f"{R}❌ BLOCKED by sandbox policy{X}" if blocked else f"{G}✅ ALLOWED{X}"
        print(f"  {verdict}")
        print("  " + out.replace("\n", "\n  ")[:600])
        turn.set_attribute("output.value", out[:800])
    print(f"  {Y}↳ trace → Phoenix '{PROJECT}'{X}\n")
