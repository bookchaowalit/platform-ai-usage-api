# ADR-0004 — Sanitized JSON snapshot files instead of a database

- Status: accepted (retro-documented)

## Context

ข้อมูลที่ต้องเก็บมีแค่ค่าล่าสุดของโควตาต่อ provider และค่าที่เจ้าของตั้งไว้

## Decision

- เก็บเป็น 3 ไฟล์ใน `AI_USAGE_STATE_DIR` (default `~/.local/state/solo-empire/ai-usage`): `claude.json`, `codex.json`, `settings.json`
- writer (collector) เขียนแบบ atomic (`tempfile.mkstemp` → `fsync` → `os.replace`), dir `0700`, file `0600`, ปฏิเสธ symlink
- reader (API) เปิดแบบ `O_NOFOLLOW` ทุก path component, เฉพาะ regular file ≤ 1 MiB, JSON ห้าม key ซ้ำ; ไม่มี write route
- ไม่มี history: snapshot ใหม่ทับของเดิม; API คำนวณ projection ใหม่ทุก request

## Evidence

- `collector.py` `atomic_json`, `update_settings`
- `model.py` `read_snapshot`, `_open_directory`, `_unique_object`, `MAX_SNAPSHOT_BYTES`
- `service.yaml` `data.reads` / `data.writes: []`
- `contracts/ai-usage.v1.md` (Snapshot และ settings boundary)

## Consequences

- ไม่มี migration / schema evolution นอกจาก `schema_version` string (`solo-empire.ai-usage.snapshot.v1`)
- ไม่มี backup ในตัว (ดู 14); snapshot สร้างใหม่ได้เอง แต่ `settings.json` เป็นข้อมูลที่เจ้าของกรอก
