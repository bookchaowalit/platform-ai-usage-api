# 18 — Git / release workflow

ทาง change ไปถึง "production" (= checkout บนเครื่องเจ้าของที่ systemd units ชี้อยู่): commit → `main` บน GitHub → CI → เจ้าของ `git pull` ใน checkout แล้ว restart units ด้วยมือ ไม่มี tag / release / deploy job

ใน 31 commits บน `main` มี 3 merge commits (`--no-ff` จาก branch PR #3, #4, #5), 2 squash-merged PRs (#1 `f440746`, #2 `939514c`) และที่เหลือ push ตรง `main` (เช่น `b4881fa` L2 baseline, SPEC-002 ระบุ "Main-only: committed straight to `main`") `main` ไม่มี branch protection / ruleset

```mermaid
gitGraph
  commit id: "11f8529 feat ai-usage"
  commit id: "9f95946 standalone repo"
  commit id: "6139fa0 feat ROI"
  commit id: "e779065 feat status"
  branch ci/devsecops-phase1
  commit id: "PR1 shared CI"
  checkout main
  commit id: "f440746 squash PR1"
  branch fix/keep-z-normalisation
  commit id: "PR2 fix"
  checkout main
  commit id: "939514c squash PR2"
  commit id: "2416e59 demo gif"
  branch ci/coverage-gate
  commit id: "e5b739e gate 90 red"
  commit id: "87f8b33 gate 82 green"
  checkout main
  merge ci/coverage-gate id: "a8b920b PR3"
  commit id: "5c26463 spec approved"
  branch docs/spec-private-links
  commit id: "add9828 pin v1.1.1"
  checkout main
  merge docs/spec-private-links id: "a7b48dd PR4"
  branch docs/spec-timing-figure
  commit id: "9c362de timing"
  checkout main
  merge docs/spec-timing-figure id: "feb7dd5 PR5"
  commit id: "b4881fa L2 baseline direct"
```

```mermaid
flowchart LR
  DEV["Change on branch or main"] --> PR{"PR?"}
  PR -->|"yes"| CIPR["CI on pull_request"]
  CIPR --> MRG["Merge locally and push, or squash"]
  PR -->|"no, main-only"| PUSH["push main"]
  MRG --> CIM["CI on push main"]
  PUSH --> CIM
  CIM --> PULL["Owner git pull in local checkout"]
  PULL --> RST["systemctl --user restart solo-ai-usage-api solo-ai-usage-collector"]
  RST --> LIVE["Local units run new code"]
```

Sources: `git log origin/main` (at `b4881fa`), `gh pr list -R bookchaowalit/platform-ai-usage-api --state all`, `gh api repos/bookchaowalit/platform-ai-usage-api/branches/main/protection` (404), `gh api .../rulesets` (`[]`), `docs/OWNER.th.md` (restart command), `specs/002-l2-baseline/spec.md` (Main-only), `.github/workflows/ci.yml`

## Open questions

- local checkout ถูก update อย่างไรและเมื่อไร (manual `git pull`?) — ไม่มีบันทึกใน repo จึงไม่รู้ว่า code ที่รันอยู่ตรงกับ `main` หรือไม่
