# ADR-0001 — Local-first: systemd user units on loopback, no hosted deploy

- Status: accepted (retro-documented)
- Date of evidence: 2026-10-11 (repo split from solo-empire) … 2026-10-22 (`b4881fa`)

## Context

ข้อมูลโควตามาจาก CLI ที่ล็อกอินอยู่ในเครื่องของเจ้าของ (Claude Code status line, Codex app-server) จึงเก็บได้เฉพาะบนเครื่องนั้น

## Decision

รัน `server.py --host 127.0.0.1 --port 3520` และ `collector.py codex --interval 300` เป็น systemd **user** units จาก checkout นี้ (`Restart=on-failure`, `UMask=0077`) ไม่มี hosted deploy: `service.yaml` `deploy.target: unassigned`; `Dockerfile` มีไว้เป็นทางเลือกเท่านั้น

## Evidence

- `systemd/solo-ai-usage-api.service`, `systemd/solo-ai-usage-collector.service`
- `service.yaml` (`deploy.target: unassigned`, `data.writes: []`)
- `PRODUCT.md` Operating Context (registry id `ai-usage`, status `exception`, host `local`)
- `docs/OWNER.th.md` ("ยังไม่ได้ deploy service นี้")

## Consequences

- ไม่มี uptime monitor ภายนอกสำหรับ API นี้ (PRODUCT.md Measures); services หยุดเมื่อ user session จบ (OWNER.th.md)
- เครื่องเดียวคือ single point of failure; ไม่มี data ที่ต้อง replicate นอกจาก `settings.json`
