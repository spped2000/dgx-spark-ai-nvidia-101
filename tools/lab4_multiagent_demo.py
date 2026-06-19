# /// script
# requires-python = ">=3.10"
# dependencies = ["openai>=1.40", "arize-phoenix-otel>=0.6", "openinference-instrumentation-openai>=0.1"]
# ///
"""
LAB 4 — Multi-agent orchestration: orchestrator → coding agent → reviewer agent
แต่ละ agent = 1 span ใน Phoenix → เห็นการ delegate เป็นทีม. traces → Phoenix 'dgx-spark-lab4'
รัน: BASE_URL=http://localhost:8000/v1 MODEL=nemotron-nano uv run tools/lab4_multiagent_demo.py
"""
import os
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000/v1")
MODEL = os.environ.get("MODEL", "nemotron-nano")
tp = register(project_name="dgx-spark-lab4", endpoint=f"{os.environ.get('PHOENIX_ENDPOINT','http://localhost:6006')}/v1/traces")
OpenAIInstrumentor().instrument(tracer_provider=tp)
tracer = tp.get_tracer("lab4")
client = OpenAI(base_url=BASE_URL, api_key="EMPTY")


def agent(name, system, user, kind="AGENT", maxtok=400):
    with tracer.start_as_current_span(name) as sp:
        sp.set_attribute("openinference.span.kind", kind)
        sp.set_attribute("input.value", user)
        r = client.chat.completions.create(
            model=MODEL, max_tokens=maxtok, temperature=0.3,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        out = r.choices[0].message.content.strip()
        sp.set_attribute("output.value", out)
        return out


TASK = "เขียนฟังก์ชัน Python ชื่อ is_prime(n) ที่บอกว่า n เป็นจำนวนเฉพาะไหม"

with tracer.start_as_current_span("orchestrator-turn") as root:
    root.set_attribute("openinference.span.kind", "AGENT")
    root.set_attribute("input.value", TASK)

    plan = agent("orchestrator", "You are the orchestrator. Break the task and delegate to a coder then a reviewer. Reply with a short plan.", TASK, maxtok=180)
    print(f"\n[orchestrator/plan]\n{plan[:300]}")

    code = agent("coding-agent", "You are a Python coding agent. Write ONLY the requested function, clean and correct.", TASK)
    print(f"\n[coding-agent]\n{code[:400]}")

    review = agent("reviewer-agent", "You are a strict code reviewer. List concrete issues/edge-cases (n<2, even numbers, efficiency) in bullet points.",
                   f"Review this code:\n{code}")
    print(f"\n[reviewer-agent]\n{review[:400]}")

    final = agent("orchestrator", "You are the orchestrator. Combine the coder's code and reviewer's notes into a final answer.",
                  f"Task: {TASK}\nCode:\n{code}\nReview:\n{review}", maxtok=300)
    root.set_attribute("output.value", final)
    print(f"\n[final]\n{final[:400]}")

print("\n[done] Phoenix project 'dgx-spark-lab4' → trace 'orchestrator-turn' มี span: orchestrator + coding-agent + reviewer-agent (เห็นทีมทำงาน)")
