#!/usr/bin/env python3
"""
orca-fleet eval runner.

Ports the marketingskills per-skill eval JSON pattern and adds a mission-routing
benchmark. Uses only the Python standard library.

Usage:
    python3 scripts/eval.py validate
    python3 scripts/eval.py run --suite routing|skills|all
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
EVALS_DIR = ROOT / "evals"
ROUTING_EVAL = EVALS_DIR / "routing.json"

# Heuristic triggers derived from each mission's frontmatter description and the
# intent → mission table in AGENTS.md. This is a deterministic baseline, not an
# LLM; it is meant to catch regressions in routing clarity and provide a score
# that future LLM-judge evals can improve on.
MISSION_TRIGGERS = {
    "ship-it": [
        "build and ship", "spec to shipped", "ship this", "build-to-release",
        "autonomous build", "release state", "deployed and verified", "new feature",
        "implement", "build me",
    ],
    "clean-sweep": [
        "close every issue", "drain the backlog", "fix everything", "clean sweep",
        "readme lies", "false doc", "audit findings", "backlog", "finite backlog",
    ],
    "harden-it": [
        "harden", "security sweep", "red team", "red-team", "security loop",
        "security audit", "exploit", "threat model", "stride",
        "secret", "cve",
    ],
    "speed-it": [
        "slow", "perf", "performance", "core web vitals", "cwv", "perf budget",
        "lighthouse", "load test", "bottleneck",
    ],
    "modernize-it": [
        "update dependencies", "upgrade everything", "framework migration",
        "dependency upgrades", "old major", "dependency", "migrate from",
        "npm audit", "get off",
    ],
    "prove-it": [
        "test gap", "critical paths", "test debt", "mutation", "characterization",
        "critical surface", "money/auth/data",
    ],
    "deflake-it": [
        "flaky", "flake", "deflake", "intermittent suite", "flake zero",
        "green streak",
    ],
    "review-it": [
        "review this pr", "ready to merge", "review queue", "verdict",
        "pr review", "read-only",
    ],
    "map-it": [
        "chart this", "plan this epic", "don't know the shape", "foggy",
        "execution map", "frozen map", "chart",
    ],
    "root-cause": [
        "diagnose", "why is this", "root cause", "hard bug", "intermittent bug",
        "happening", "concurrency bug", "production symptom",
    ],
}

EXPECTED_MISSIONS = set(MISSION_TRIGGERS.keys())


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {err}") from err


def validate_skill_eval(skill_dir: Path) -> list[str]:
    """Return a list of error strings for a single skill's evals.json."""
    errors = []
    eval_file = skill_dir / "evals" / "evals.json"
    if not eval_file.exists():
        # Evals are optional in this first pass; absence is not an error.
        return errors

    try:
        data = load_json(eval_file)
    except ValueError as err:
        return [str(err)]

    name = skill_dir.name
    if data.get("skill_name") != name:
        errors.append(f"{eval_file.relative_to(ROOT)}: skill_name '{data.get('skill_name')}' does not match folder '{name}'")

    evals = data.get("evals")
    if not isinstance(evals, list):
        errors.append(f"{eval_file.relative_to(ROOT)}: missing or non-list 'evals'")
        return errors

    required = {"id", "prompt", "expected_output", "assertions"}
    for idx, ev in enumerate(evals):
        if not isinstance(ev, dict):
            errors.append(f"{eval_file.relative_to(ROOT)}: eval[{idx}] is not an object")
            continue
        missing = required - set(ev.keys())
        if missing:
            errors.append(f"{eval_file.relative_to(ROOT)}: eval[{idx}] missing {sorted(missing)}")
        if "id" in ev and not isinstance(ev["id"], int):
            errors.append(f"{eval_file.relative_to(ROOT)}: eval[{idx}].id is not an integer")
        if "assertions" in ev and not isinstance(ev["assertions"], list):
            errors.append(f"{eval_file.relative_to(ROOT)}: eval[{idx}].assertions is not a list")
        if "files" in ev and not isinstance(ev.get("files"), list):
            errors.append(f"{eval_file.relative_to(ROOT)}: eval[{idx}].files is not a list")

    return errors


def validate_routing_eval() -> list[str]:
    errors = []
    if not ROUTING_EVAL.exists():
        errors.append(f"missing {ROUTING_EVAL.relative_to(ROOT)}")
        return errors

    try:
        data = load_json(ROUTING_EVAL)
    except ValueError as err:
        return [str(err)]

    if "evals" not in data or not isinstance(data["evals"], list):
        errors.append(f"{ROUTING_EVAL.relative_to(ROOT)}: missing or non-list 'evals'")
        return errors

    required = {"id", "prompt", "expected_mission", "type", "reason"}
    seen_missions = set()
    for idx, ev in enumerate(data["evals"]):
        if not isinstance(ev, dict):
            errors.append(f"{ROUTING_EVAL.relative_to(ROOT)}: eval[{idx}] is not an object")
            continue
        missing = required - set(ev.keys())
        if missing:
            errors.append(f"{ROUTING_EVAL.relative_to(ROOT)}: eval[{idx}] missing {sorted(missing)}")
        if ev.get("type") == "positive" and ev.get("expected_mission") in EXPECTED_MISSIONS:
            seen_missions.add(ev["expected_mission"])
        if ev.get("type") not in {"positive", "negative"}:
            errors.append(f"{ROUTING_EVAL.relative_to(ROOT)}: eval[{idx}].type must be 'positive' or 'negative'")

    uncovered = EXPECTED_MISSIONS - seen_missions
    if uncovered:
        errors.append(f"{ROUTING_EVAL.relative_to(ROOT)}: no positive routing examples for {sorted(uncovered)}")

    return errors


def validate_all() -> list[str]:
    errors = validate_routing_eval()
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith((".", "_")):
            continue
        errors.extend(validate_skill_eval(skill_dir))
    return errors


# Missions that require specific technical vocabulary to override general intent.
SPECIALIST_MISSIONS = {
    "harden-it", "speed-it", "modernize-it", "prove-it", "deflake-it",
}


def classify_prompt(prompt: str) -> str | None:
    """Return the mission with the highest heuristic trigger overlap.

    Specialist missions (security/perf/deps/tests/flakes) override general
    backlog/diagnosis/build routing when their technical vocabulary is present.
    """
    prompt_lower = prompt.lower()
    scores = {}
    for mission, triggers in MISSION_TRIGGERS.items():
        score = 0
        for trig in triggers:
            if trig in prompt_lower:
                # Longer triggers that match are more specific; weight by length.
                score += len(trig.split())
        scores[mission] = score

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return None

    # Specialist wins if it has any signal and the general winner is not already
    # a specialist. This handles prompts like "Drain the backlog of dependency
    # upgrades" where clean-sweep scores high on "drain the backlog" but
    # modernize-it has the decisive technical term.
    if best not in SPECIALIST_MISSIONS:
        specialist_best = None
        specialist_score = 0
        for mission, score in scores.items():
            if mission in SPECIALIST_MISSIONS and score > specialist_score:
                specialist_best = mission
                specialist_score = score
        if specialist_best is not None and specialist_score > 0:
            return specialist_best

    return best


def run_routing_eval() -> dict:
    data = load_json(ROUTING_EVAL)
    evals = data["evals"]
    total = len(evals)
    correct = 0
    failures = []

    for ev in evals:
        predicted = classify_prompt(ev["prompt"])
        expected = ev["expected_mission"]
        if predicted == expected:
            correct += 1
        else:
            failures.append({
                "id": ev["id"],
                "prompt": ev["prompt"],
                "expected": expected,
                "predicted": predicted,
                "type": ev["type"],
                "reason": ev["reason"],
            })

    return {
        "total": total,
        "correct": correct,
        "score": correct / total if total else 0.0,
        "failures": failures,
    }


def run_skills_eval() -> dict:
    """Return a summary of per-skill eval files (schema validation only)."""
    skill_evals = {}
    errors = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith((".", "_")):
            continue
        eval_file = skill_dir / "evals" / "evals.json"
        if eval_file.exists():
            try:
                data = load_json(eval_file)
                skill_evals[skill_dir.name] = len(data.get("evals", []))
            except ValueError as err:
                errors.append(str(err))
        skill_errors = validate_skill_eval(skill_dir)
        errors.extend(skill_errors)

    return {
        "skill_evals": skill_evals,
        "total_evals": sum(skill_evals.values()),
        "errors": errors,
    }


def cmd_validate(_args: argparse.Namespace) -> int:
    errors = validate_all()
    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        return 1

    routing = load_json(ROUTING_EVAL)
    routing_count = len(routing.get("evals", []))
    skill_count = sum(
        len(load_json(d / "evals" / "evals.json").get("evals", []))
        for d in SKILLS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith((".", "_")) and (d / "evals" / "evals.json").exists()
    )
    print(f"All evals valid: {routing_count} routing examples, {skill_count} per-skill evals.")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    exit_code = 0
    if args.suite in ("routing", "all"):
        result = run_routing_eval()
        print(f"Routing eval: {result['correct']}/{result['total']} correct ({result['score']:.0%})")
        if result["failures"]:
            print("Failures:")
            for f in result["failures"]:
                print(f"  [{f['type']}] id={f['id']} expected={f['expected']} predicted={f['predicted']}")
                print(f"    prompt: {f['prompt']}")
                print(f"    reason: {f['reason']}")
        if result["score"] < (args.threshold or 0.0):
            exit_code = 1

    if args.suite in ("skills", "all"):
        result = run_skills_eval()
        print(f"Per-skill evals: {result['total_evals']} evals across {len(result['skill_evals'])} missions")
        if result["errors"]:
            print("Schema errors:")
            for e in result["errors"]:
                print(f"  - {e}")
            exit_code = 1

    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="orca-fleet eval runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="validate all eval JSON files")

    run_parser = subparsers.add_parser("run", help="run an eval suite")
    run_parser.add_argument(
        "--suite",
        choices=["routing", "skills", "all"],
        default="all",
        help="which eval suite to run",
    )
    run_parser.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="minimum routing score (0.0–1.0) required to pass",
    )

    args = parser.parse_args()
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "run":
        return cmd_run(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
