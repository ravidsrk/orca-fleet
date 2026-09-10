#!/usr/bin/env sh
# print-settings-snippet.sh — emit the symlink-install completion gate, path resolved.
#
# A `ln -s` install into ~/.claude/skills/ loads no plugin, so ${CLAUDE_PLUGIN_ROOT}
# is unset and hooks/hooks.json never fires: the recommended install path ships
# missions with NO completion gate (issue #262). This prints the same two hooks with
# this clone's absolute path substituted, ready to merge into settings.json.
#
#   sh hooks/print-settings-snippet.sh              # to stdout
#   sh hooks/print-settings-snippet.sh --check      # verify the wired script exists
#
# Exit: 0 ok · 1 the template or the gate script is missing.
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$HERE/.." && pwd)
TEMPLATE="$HERE/settings-snippet.json"
GATE="$ROOT/runtime/scripts/verify-gate.sh"

[ -f "$TEMPLATE" ] || { echo "missing $TEMPLATE" >&2; exit 1; }
[ -x "$GATE" ] || [ -f "$GATE" ] || { echo "missing $GATE" >&2; exit 1; }

if [ "${1:-}" = "--check" ]; then
  echo "ok: $GATE exists; snippet would wire it from $ROOT"
  exit 0
fi

sed "s|__ORCA_FLEET_ROOT__|$ROOT|g" "$TEMPLATE"
