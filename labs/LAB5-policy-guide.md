# LAB 5 เสริม — OpenShell Policy & Rules: ตั้งและเพิ่มยังไง
(อิง OpenShell v0.0.66 · `docs/reference/policy-schema.mdx` · ทดสอบจริงบน DGX Spark)

## แนวคิดหลัก: **deny-by-default**
sandbox บล็อก outbound ทั้งหมดตั้งแต่แรก — เปิดเฉพาะที่เขียนใน `network_policies` เท่านั้น

## โครงสร้างไฟล์ policy.yaml
```yaml
version: 1

filesystem_policy:                 # คุมไฟล์
  include_workdir: true
  read_only:  [/usr, /lib, /etc, /var/log]
  read_write: [/sandbox, /tmp]
landlock: { compatibility: best_effort }
process:  { run_as_user: sandbox, run_as_group: sandbox }

network_policies:                  # คุมเครือข่าย
  <ชื่อ-policy>:
    name: <label>
    endpoints:
      - host: api.github.com       # รองรับ wildcard label แรก: *.example.com
        port: 443
        protocol: rest             # rest | websocket | graphql ; ละไว้ = TCP passthrough (L4)
        enforcement: enforce       # enforce = บล็อกจริง · audit = แค่ log ไม่บล็อก
        access: read-only          # preset (ดูตาราง) — ใช้คู่กับ rules ไม่ได้
    binaries: [{ path: /usr/bin/curl }]   # จำกัดเฉพาะ binary (ไม่ใส่ = ทุก binary)
```

## access presets (วิธีง่าย)
| preset | REST อนุญาต |
|---|---|
| `full` | ทุก method |
| `read-only` | GET, HEAD, OPTIONS |
| `read-write` | GET, HEAD, OPTIONS, POST, PUT, PATCH |

## rules + deny_rules (วิธีละเอียด L7) — ใช้แทน access
```yaml
- host: api.github.com
  port: 443
  protocol: rest
  enforcement: enforce
  rules:                                   # allow ราย method + path glob (* / **)
    - allow: { method: GET,  path: /repos/** }
    - allow: { method: POST, path: /repos/*/issues }   # POST เฉพาะ path นี้
  deny_rules:                              # ทำงานหลัง allow และชนะเสมอ
    - deny:  { method: DELETE, path: /** }
```
- รองรับ `websocket` (method `WEBSOCKET_TEXT`) และ `graphql` (operation_type/fields) ด้วย
- `query:` matcher ได้ เช่น `query: { service: "git-*" }`

## CLI — ตั้ง vs เพิ่ม
```bash
# (A) ตั้งทั้งไฟล์ = replace ทั้ง policy  → แก้ YAML แล้ว apply
openshell policy set  <sandbox> --policy policy.yaml --wait

# (B) เพิ่ม/ลบ ทีละกฎ = incremental (ไม่ต้องเขียนไฟล์ใหม่)
openshell policy update <sandbox> \
  --add-endpoint api.github.com:443:read-only:rest:enforce --binary /usr/bin/curl --wait
openshell policy update <sandbox> --add-allow api.github.com:443:POST:/repos/*/issues --wait
openshell policy update <sandbox> --add-deny  api.github.com:443:DELETE:/** --wait
openshell policy update <sandbox> --remove-endpoint example.com:443 --wait
openshell policy update <sandbox> --dry-run --add-allow ...      # พรีวิวก่อน apply

# ดู/ตรวจ
openshell policy get   <sandbox>        # policy ที่ active อยู่
openshell policy list  <sandbox>        # ประวัติ version
openshell policy prove <sandbox> ...    # พิสูจน์คุณสมบัติ policy / หา counterexample
```

## เดโมในคลาส (live)
1. `openshell policy get lab5-ui` → โชว์ policy ปัจจุบัน (read-only)
2. ผู้เรียนยิง POST → ❌ blocked (L7 policy_denied)
3. ผู้สอน **เพิ่มกฎสด**: `openshell policy update lab5-ui --add-allow api.github.com:443:POST:/repos/*/issues --wait`
4. ยิง POST ที่ path เดิมอีกครั้ง → ✅ ผ่าน (เห็น policy เปลี่ยนพฤติกรรมทันที ไม่ต้อง restart sandbox)
5. (ตัวเลือก) `--add-deny` คืน หรือ `policy set` กลับเป็น read-only

> เครื่องมือช่วย: skill **`generate-sandbox-policy`** — สร้าง policy.yaml จากคำอธิบายภาษาคน + เอกสาร API (OpenAPI/Swagger) อัตโนมัติ
