# field-test-it self-test — MISSION-LEVEL PARK (no target exists)

RUN: field-test-it self-test against orca-fleet itself · COORDINATOR · BASE 6390743815f8f435181fa410cce374587128b30a (origin/main tip, verified `git rev-parse HEAD origin/main` both equal) · FORK_POINT - · T0 2026-09-16 · SOURCE: (empty — no defect set, no device flow; see §1) · WIP: builders=0 reviewers=0

Branch: `campaign/field-test-it-selftest`. No code changed; this report is the only artifact. No run was fabricated.

## Verdict

**PARKED at PAIR — the mission does not apply to this repo.** `field-test-it` verifies
"an app on a real device or emulator" (SKILL.md: unit = one device-observed defect or one
device QA pass over a flow; oracle = the ledgered device session). orca-fleet at
`6390743` contains no app of any tier the oracle ladder accepts
(`DEVICE | EMULATOR | BROWSER | DESKTOP | CLEAN-ENV`), so there is nothing to pair a
session against, no BASELINE to capture, and no defect set to enter the pipeline.
Per the mission's own ordering rule ("a desktop pass never substitutes") and the workflow's
honest-park rule, no substitute run was performed.

## 1. Target survey (evidence — all commands run in the worktree at 6390743)

| # | Probe | Result |
|---|-------|--------|
| 1 | `ls skills/ demo/ playbooks/ runtime/ tests/ scripts/` | Repo = markdown missions/playbooks/runtime + Python validator scripts + tests + static assets (`assets/`: badges, diagrams, jpgs). `demo/` holds only `negative-control/` (frozen-spec.md, gamed-manifest.json, run.sh, selfscore.py — a negative-control fixture, not an app). |
| 2 | `find . -iname AndroidManifest.xml -o -iname *.xcodeproj -o -iname *.xcworkspace -o -iname Podfile -o -iname *.apk -o -iname *.ipa -o -iname package.json -o -iname pubspec.yaml -o -iname *.gradle` | Zero hits. |
| 3 | `find . -iname *.apk -o -iname *.ipa -o -iname *.app -o -iname *.aab -o -iname build.gradle* -o -iname *.xcodeproj` | Zero hits. No buildable mobile app, no packaged artifact. |
| 4 | `grep -rilE 'flask\|django\|fastapi\|express\|electron\|tkinter\|pyqt\|streamlit\|localhost:[0-9]'` | Only prose/fixture mentions (`expression` in runtime docs; `django==5.2.6` fixture strings in `tests/test_evals.py`). No servable web app, no GUI code. |
| 5 | `command -v orca/adb/xcodebuild/simctl` | orca 1.4.203 present; xcodebuild present (CLT stub); **adb absent**; **simctl absent** (`xcrun: error: unable to find utility "simctl"`). |
| 6 | `orca skills list` | `orca-emulator` and `orca-emulator-android` guides available; iOS guide states "build and install the app with xcodebuild or simctl first" — there is no app to build (see #2–3), and simctl is unavailable (see #5). |

## 2. Pairing preconditions (mission PAIR phase)

- Android: requires an emulator/AVD or adb-visible device **plus a Gradle-built APK**. No
  `build.gradle`, no manifest, no adb → cannot pair, nothing to install.
- iOS: requires the app's own xcodebuild/simctl build+install first; the emulator skill
  does not install apps. No Xcode project, no full Xcode/simctl → cannot pair.
- Physical iOS is not a command surface of either skill (SKILL.md) → any such flow would
  PARK even if an app existed.
- No BROWSER surface (no served web app), no DESKTOP surface (no window-level GUI).

## 3. Why no substitute qualifies (substitutes considered and rejected)

- `scripts/install.sh` under CLEAN-ENV: rejected — a shell installer for a markdown catalog
  is not an app; it has no install/permission-prompt behaviour on a device, and a sandbox
  shell run is a desktop-tier run, which the mission forbids as device evidence
  ("a desktop pass never substitutes"; desktop-only verification is PARKED, not proven).
- `scripts/validate.py` + `tests/` suite: rejected — a CLI Python suite with no
  render/input/lifecycle surface; exercising it is `prove-it` territory, not field testing.
- Static docs/assets: rejected — markdown + images, no flows to drive on-device.
- Fabricating a demo app to "have something to test": rejected — that would test a
  synthetic artifact, not orca-fleet itself, violating the honest-park rule.

## 4. Pipeline state

PAIR → PARK. No BASE (no fix work exists, so no integration branch was cut — nothing to
land, nothing to serialize). BASELINE/REPRODUCE/FIX/REVIEW/LAND/RE-VERIFY/SNAPSHOT-LEDGER
not reached: defect set is empty and the oracle tier is unassignable. No ledger rows
(the canonical row requires a defect; there are none). One-worker-router rule, gates, and
negative-control requirements are vacuous with no units. No secrets touched, no deploys,
no destructive commands.

## 5. What would un-park this mission

A device-testable surface owned by this repo (a companion mobile app, a served web UI, or
a desktop GUI with flows to drive) plus the matching toolchain (full Xcode + simctl for
iOS; Android SDK + adb for Android). Until then, `metadata.proof` for `field-test-it`
correctly remains `doctrine-only` as far as this self-test is concerned — this PARK is
not a run report that binds, and claims no proof advancement.
