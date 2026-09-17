#!/usr/bin/env python3
"""Count-lint regex engine — the catalog-count patterns behind validate.py's
`check_doc_counts` (moved here verbatim by reshape-it RV-D1; `validate.py`
keeps one re-export, `COUNT_LINT_RE`). Private module: import through
`scripts/validate.py`, never directly.
"""
import re


# Catalog-SIZE phrasings only: a digit or spelled number in the catalog range, landing
# on a catalog noun ("11 missions", "eleven missions", "10 outcome-named"), hyphenated
# ("ten-mission set"), or through one adjective and markdown emphasis ("Ten **autonomous
# fleets**"). A bare "one mission" / "two missions" in the mission-identity prose is NOT
# a catalog count and must not trip — so a lone ones-word is never a count.
_ONES = "one|two|three|four|five|six|seven|eight|nine"
_TEENS = ("ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
          "nineteen")
_TENS = "twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
# A compound is ONE number token, not a number followed by a word (#346). The old pattern
# stopped at "twenty", so "thirty-one missions" was invisible; worse, in "twenty-one
# autonomous fleets" the "one" was consumed by the single optional-adjective slot below,
# leaving no room for "autonomous" — so the repo's own tagline shape slipped through at
# the exact catalog size that made the phrase current. A ones-word still cannot stand
# alone as a count, which is what keeps "one mission" out.
_SPELLED = rf"(?:(?:{_TENS})(?:[-\s]+(?:{_ONES}))?|{_TEENS})"
_NUM = rf"(?:\d+|{_SPELLED})"
# Separator between count, optional adjective, and noun: a hyphen (ten-mission) or
# whitespace with optional markdown emphasis markers (Ten **autonomous fleets**).
_SEP = r"(?:-|[\s*_`]+)"
# The proof tiers are catalog nouns too: "21 `doctrine-only`" is a hardcoded catalog count that
# the noun set could not see, and it sat in README.md while this very guard was green (#282).
_CATALOG_NOUN = (r"(?:missions?|fleets?|outcome-named|callable|"
                 r"`?(?:doctrine-only|self-run|external-run)`?)")
COUNT_LINT_RE = re.compile(
    rf"\b{_NUM}{_SEP}(?:[a-z]+{_SEP})?{_CATALOG_NOUN}\b",
    re.IGNORECASE,
)
# "all ten" / "all 11" carries a catalog count with no noun at all; it only reads as a
# catalog count on a line that is talking about the catalog. Bare "catalog" is kept
# deliberately: in COUNT_LINT_FILES the word only ever means the mission catalog, and
# a false positive here is a cheap rephrase while a false negative is silent rot.
ALL_COUNT_RE = re.compile(rf"\ball\s+{_NUM}\b", re.IGNORECASE)
MISSION_CONTEXT_RE = re.compile(r"\b(?:missions?|fleets?|catalog)\b", re.IGNORECASE)
