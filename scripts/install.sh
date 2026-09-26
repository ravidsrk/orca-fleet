#!/usr/bin/env sh
# install.sh — one-command orca-fleet install (issue #414).
#
# From a clone:
#   sh scripts/install.sh
# From anywhere (the documented one-command install):
#   git clone https://github.com/ravidsrk/orca-fleet.git && cd orca-fleet && sh scripts/install.sh
#
# What it does:
#   1. HARD prerequisites: git present, python3 >= 3.13, catalog gates green
#      (scripts/validate.py), every mission symlinked into the skills dir with
#      its playbooks/ and runtime/ references resolving, completion-gate
#      snippet available. Any failure here exits nonzero.
#   2. SOFT prerequisites (warnings only — needed to RUN missions, not to
#      install the catalog): the orca CLI at or above the runtime/pins.json
#      pin, gh present and authenticated, Claude Code present.
#   3. --check re-verifies an existing install without changing anything.
#
# Exit: 0 installed (warnings allowed) · 1 a hard prerequisite failed.
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$HERE/.." && pwd)
SKILLS_DIR="${HOME}/.claude/skills"
MODE="install"
WARN=0

for arg in "$@"; do
  case "$arg" in
    --check) MODE="check" ;;
    --skills-dir=*) SKILLS_DIR="${arg#--skills-dir=}" ;;
    -h|--help)
      echo "usage: sh scripts/install.sh [--check] [--skills-dir=DIR]"
      exit 0
      ;;
    *) echo "install.sh: unknown argument $arg" >&2; exit 1 ;;
  esac
done

say() { printf '%s\n' "$1"; }
warn() { WARN=$((WARN + 1)); printf 'WARN: %s\n' "$1"; }
die() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }

# --- hard prerequisites -------------------------------------------------------
command -v git >/dev/null 2>&1 || die "git not found in PATH (install git first)"
command -v python3 >/dev/null 2>&1 || die "python3 not found in PATH (Python >= 3.13 required)"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 13) else 1)' \
  || die "python3 is $(python3 -V 2>&1); orca-fleet requires Python >= 3.13"
[ -d "$ROOT/skills" ] && [ -d "$ROOT/playbooks" ] && [ -d "$ROOT/runtime" ] \
  || die "not an orca-fleet checkout: $ROOT lacks skills/, playbooks/ or runtime/"

# --- soft prerequisites (warn, never fail: the catalog installs without them) -
ORCA_MIN="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["orca"]["version"].lstrip("v"))' "$ROOT/runtime/pins.json" 2>/dev/null || true)"
if command -v orca >/dev/null 2>&1 || command -v orca-ide >/dev/null 2>&1; then
  ORCA_BIN="$(command -v orca || command -v orca-ide)"
  ORCA_VER="$("$ORCA_BIN" --version 2>/dev/null | head -n 1 || true)"
  if [ -z "$ORCA_MIN" ]; then
    warn "cannot read the Orca version pin (runtime/pins.json) — unable to verify the Orca floor"
  elif [ -z "$ORCA_VER" ]; then
    warn "orca CLI at $ORCA_BIN returned no version output — unable to verify it meets the catalog pin ${ORCA_MIN}"
  else
    python3 - "$ORCA_VER" "$ORCA_MIN" 2>/dev/null <<'PY' || warn "orca CLI reports '${ORCA_VER:-unknown}', below the catalog pin ${ORCA_MIN} (runtime/pins.json); missions may misbehave"
import re, sys
def parts(s):
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", s)
    return tuple(map(int, m.groups())) if m else None
have, want = parts(sys.argv[1]), parts(sys.argv[2])
sys.exit(0 if (have and want and have >= want) else 1)
PY
  fi
  # Live readiness (S23): `orca status --json` reports app/ + runtime/ + graph/.
  # Ready means the app runs AND the runtime is reachable AND its state is
  # ready (graph folds into runtime.state upstream: status.ts). SOFT like the
  # version floor above — a hard gate here would refuse headless/CI installs
  # where the app simply is not launched yet. That hardening is PARKED
  # (needs-human policy), not silently added.
  ORCA_STATUS="$("$ORCA_BIN" status --json 2>/dev/null || true)"
  if [ -z "$ORCA_STATUS" ]; then
    warn "orca CLI at $ORCA_BIN answered no \`status --json\`, so readiness could not be determined — start Orca before running missions"
  else
    _status_rc=0
    python3 - "$ORCA_STATUS" 2>/dev/null <<'PY' || _status_rc=$?
import json, sys
try:
    doc = json.loads(sys.argv[1])
except Exception:
    sys.exit(2)
r = doc.get("result") if isinstance(doc, dict) else None
if not isinstance(r, dict):
    sys.exit(2)
app = r.get("app") or {}
rt = r.get("runtime") or {}
ready = app.get("running") is True and rt.get("reachable") is True and rt.get("state") == "ready"
sys.exit(0 if ready else 1)
PY
    if [ "$_status_rc" -eq 2 ]; then
      warn "orca CLI at $ORCA_BIN answered an unreadable \`status --json\`, so readiness could not be determined — start Orca before running missions"
    elif [ "$_status_rc" -ne 0 ]; then
      warn "orca CLI at $ORCA_BIN is present but its app/runtime is not ready (\`orca status\` disagrees) — start Orca before running missions"
    fi
  fi
else
  warn "no orca CLI in PATH (missions dispatch through it; install Orca >= ${ORCA_MIN:-unknown} to run them)"
fi
if command -v gh >/dev/null 2>&1; then
  gh auth status >/dev/null 2>&1 || warn "gh is present but not authenticated (gh auth login); fleets open PRs per unit"
else
  warn "gh not found in PATH (fleets open PRs per unit; install gh to run them)"
fi
command -v claude >/dev/null 2>&1 || warn "claude CLI not found (needed for the symlinked skills to load)"

# --- install ------------------------------------------------------------------
if [ "$MODE" = "install" ]; then
  say "validating the catalog..."
  python3 "$ROOT/scripts/validate.py" || die "scripts/validate.py failed — refusing to install a broken catalog"
  mkdir -p "$SKILLS_DIR"
  # Pre-check every destination BEFORE linking anything: a conflict in a
  # later mission must refuse the whole install, not leave a partial one.
  for d in "$ROOT"/skills/*/; do
    [ -f "$d/SKILL.md" ] || continue
    m="$(basename "$d")"
    case "$m" in .*|_*) continue ;; esac
    if [ -e "$SKILLS_DIR/$m" ] && [ ! -L "$SKILLS_DIR/$m" ]; then
      die "$SKILLS_DIR/$m exists and is not a symlink (a copy install severs playbook resolution — remove it and re-run)"
    fi
  done
  n=0
  for d in "$ROOT"/skills/*/; do
    [ -f "$d/SKILL.md" ] || continue
    m="$(basename "$d")"
    case "$m" in .*|_*) continue ;; esac
    if [ -e "$SKILLS_DIR/$m" ] && [ ! -L "$SKILLS_DIR/$m" ]; then
      die "$SKILLS_DIR/$m exists and is not a symlink (a copy install severs playbook resolution — remove it and re-run)"
    fi
    ln -sfn "$ROOT/skills/$m" "$SKILLS_DIR/$m"
    n=$((n + 1))
  done
  [ "$n" -gt 0 ] || die "no missions found under $ROOT/skills"
  say "linked $n missions into $SKILLS_DIR"
fi

# --- verify (both modes) ------------------------------------------------------
[ -d "$SKILLS_DIR" ] || die "$SKILLS_DIR does not exist — run without --check first"
n=0
for d in "$ROOT"/skills/*/; do
  [ -f "$d/SKILL.md" ] || continue
  m="$(basename "$d")"
  case "$m" in .*|_*) continue ;; esac
  link="$SKILLS_DIR/$m"
  [ -L "$link" ] || die "$link is not a symlink (a copy severs playbook resolution — reinstall)"
  resolved="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$link")"
  [ "$resolved" = "$ROOT/skills/$m" ] || die "$link resolves to $resolved, not $ROOT/skills/$m"
  [ -s "$link/SKILL.md" ] || die "$link/SKILL.md is missing or empty"
  parent="$(python3 -c 'import os,sys; print(os.path.dirname(os.path.dirname(sys.argv[1])))' "$resolved")"
  [ -d "$parent/playbooks" ] && [ -d "$parent/runtime" ] \
    || die "$m resolves outside the repo tree ($parent) — playbooks/ and runtime/ do not resolve"
  n=$((n + 1))
done
[ "$n" -gt 0 ] || die "no missions found under $ROOT/skills"
sh "$ROOT/hooks/print-settings-snippet.sh" --check >/dev/null \
  || die "completion-gate snippet unavailable (hooks/print-settings-snippet.sh --check failed)"

say "verified $n missions: symlinks resolve, SKILL.md non-empty, playbooks/ + runtime/ in reach"
if [ "$MODE" = "install" ]; then
  say ""
  say "A symlink install loads no plugin, so wire the completion gate by hand:"
  say "  sh hooks/print-settings-snippet.sh   # merge the output into ~/.claude/settings.json"
  say "Details: docs/install.md"
fi
if [ "$WARN" -gt 0 ]; then
  say ""
  if [ "$MODE" = "install" ]; then
    say "$WARN warning(s): install complete, but missions will not RUN until these clear."
  else
    say "$WARN warning(s): install verifies, but missions will not RUN until these clear."
  fi
fi
