import os
c = get_config()  # noqa: F821

# ---- hub reachability ----
c.JupyterHub.bind_url = "http://0.0.0.0:8000"          # ใน container (map :8888 บน host)
c.JupyterHub.hub_ip = "0.0.0.0"
c.JupyterHub.hub_connect_ip = "dgx-jupyterhub"          # ชื่อ container hub บน docker network

# ---- DockerSpawner: ผู้เรียนแต่ละคน = container แยก (= sandbox ตัวเอง) ----
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"
c.DockerSpawner.image = os.environ.get("SINGLEUSER_IMAGE", "dgx-singleuser:latest")
c.DockerSpawner.network_name = "dgx-hub-net"
c.DockerSpawner.remove = True
c.DockerSpawner.name_template = "jupyter-{username}"
# ให้ container ของผู้เรียนเห็น vLLM บน host
c.DockerSpawner.extra_host_config = {"extra_hosts": {"host.docker.internal": "host-gateway"}}
c.DockerSpawner.environment = {
    "OPENAI_BASE_URL": "http://host.docker.internal:8000/v1",   # vLLM กลาง
    "OPENAI_API_KEY": "EMPTY",
    "MODEL": "nemotron-nano",
}
# mount lab notebooks (อ่านอย่างเดียว) เข้า ~/labs ของทุกคน — source = path บน HOST
c.DockerSpawner.read_only_volumes = {
    "/home/agicafet/Documents/dgx1/course/portal/notebooks": "/home/jovyan/labs",
    "/home/agicafet/Documents/dgx1/skills": "/home/jovyan/nvidia-skills",   # NVIDIA Agent Skills (read-only)
}
c.Spawner.default_url = "/lab/tree/labs/00_welcome.ipynb"
c.Spawner.mem_limit = "2G"
c.Spawner.cpu_limit = 2.0
c.Spawner.start_timeout = 180
c.Spawner.http_timeout = 120

# ---- auth: workshop (พิมพ์ username อะไรก็ได้ + รหัสรวม) ----
c.JupyterHub.authenticator_class = "dummy"
c.DummyAuthenticator.password = os.environ.get("WORKSHOP_PASSWORD", "dgxspark2026")
c.Authenticator.allow_all = True

# ---- admin service token (สำหรับเทส/จำลอง headless) ----
c.JupyterHub.services = [{"name": "adminsvc", "api_token": os.environ.get("ADMIN_TOKEN", "dgxadmintoken123")}]
c.JupyterHub.load_roles = [{
    "name": "admin-role",
    "scopes": ["admin:users", "admin:servers", "read:hub", "list:users"],
    "services": ["adminsvc"],
}]
