#!/bin/sh
# reshape-it SCAN: churn-weighted shallowness inventory, per skills/reshape-it/SKILL.md § SCAN.
#   CHURN  = git log --since=90d --format=%h -- <module-path> | wc -l
#   WIDTH  = grep -cE '^(def |class |async def |[A-Z_]+ =)' <module>, plus __all__ length
#   DEPTH  = wc -l on the implementation file(s)
#   FAN-IN = git grep -lE '(from|import|require).*<module-name>' | wc -l
#   Rank by CHURN x WIDTH / max(DEPTH/100, 1), FAN-IN tiebreak.
#   YAGNI cut: zero-churn modules drop out.
# Usage: sh scan.sh > scan-transcript.txt 2>&1; inventory table is written to stdout tail.
set -u
SINCE=90d
TMP="$(mktemp -d)"
ALL="$TMP/all.tsv"
trap 'rm -rf "$TMP"' EXIT
: > "$ALL"

echo "== reshape-it SCAN transcript =="
echo "HEAD: $(git rev-parse HEAD)"
echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "window: --since=${SINCE}"
echo ""

git ls-files '*.py' | while IFS= read -r mod; do
  name="$(basename "$mod" .py)"
  churn="$(git log --since="$SINCE" --format=%h -- "$mod" | wc -l | tr -d ' ')"
  width_top="$(grep -cE '^(def |class |async def |[A-Z_]+ =)' "$mod" 2>/dev/null || true)"
  width_top="${width_top:-0}"
  dunder=0
  if grep -q '__all__' "$mod" 2>/dev/null; then
    dunder="$(sed -n "/__all__ *= *\[/,/\]/p" "$mod" | grep -oE "'[^']+'|\"[^\"]+\"" | wc -l | tr -d ' ')"
  fi
  width=$((width_top + dunder))
  depth="$(wc -l < "$mod" | tr -d ' ')"
  fanin="$(git grep -lE "(from|import|require).*${name}" 2>/dev/null | wc -l | tr -d ' ')"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$mod" "$churn" "$width_top" "$dunder" "$width" "$depth" "$fanin" >> "$ALL"
  echo "probed: $mod churn=$churn width=$width(top=$width_top,all=$dunder) depth=$depth fanin=$fanin"
done

echo ""
echo "== ranked inventory (CHURN x WIDTH / max(DEPTH/100,1), FAN-IN tiebreak; YAGNI: churn>0) =="
printf '%-45s %6s %6s %7s %7s %9s\n' "MODULE" "CHURN" "WIDTH" "DEPTH" "FAN-IN" "SCORE"
awk -F'\t' '$2 > 0 {
  denom = ($6/100); if (denom < 1) denom = 1;
  score = ($2 * $5) / denom;
  printf "%-45s %6d %6d %7d %7d %9.2f\n", $1, $2, $5, $6, $7, score
}' "$ALL" | sort -k6,6nr -k5,5nr

echo ""
echo "== YAGNI cut (zero churn in window; dropped, not erosion) =="
awk -F'\t' '$2 == 0 { printf "%-45s width=%d depth=%d fanin=%d\n", $1, $5, $6, $7 }' "$ALL" | sort
