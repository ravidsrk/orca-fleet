#!/usr/bin/env python3
"""Read CI health outside Actions. Exit 0=healthy, 1=unhealthy, 2=monitor failed.

Use --drill-run with an existing failed run to exercise the same classifier without
changing main. This tool only reads GitHub and emits JSON; the host routes alerts.
"""
import argparse
import datetime as dt
import json
import re
import subprocess

REPO = "ravidsrk/orca-fleet"


def assess(run, now, max_age_hours=24):
    if run is None:
        return {"status": "missing", "detail": "no completed validate run on main"}
    if not isinstance(run, dict):
        raise ValueError("run must be an object")
    if not isinstance(run["updatedAt"], str):
        raise ValueError("run timestamp must be a string")
    stamp = dt.datetime.fromisoformat(run["updatedAt"].replace("Z", "+00:00"))
    if stamp.tzinfo is None or stamp > now:
        raise ValueError("run timestamp is unzoned or in the future")
    conclusion = run["conclusion"]
    if not isinstance(conclusion, str) or not conclusion:
        raise ValueError("completed run has no conclusion")
    if not isinstance(run["headSha"], str) or not re.fullmatch(r"[0-9a-f]{40}", run["headSha"]):
        raise ValueError("completed run has no valid commit SHA")
    run_id = run["databaseId"]
    if type(run_id) is not int or run_id <= 0:
        raise ValueError("completed run has no valid run ID")
    if not isinstance(run["url"], str) or not re.fullmatch(
            rf"https://github\.com/[^/]+/[^/]+/actions/runs/{run_id}", run["url"]):
        raise ValueError("completed run has no matching GitHub run URL")
    status = "healthy"
    if conclusion != "success":
        status = "red"
    elif now - stamp >= dt.timedelta(hours=max_age_hours):
        status = "stale"
    return {"status": status, "conclusion": conclusion, "updatedAt": run["updatedAt"],
            "sha": run["headSha"], "url": run["url"], "runId": run["databaseId"]}


def gh_json(args):
    proc = subprocess.run(["gh", *args], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=45, check=False)
    if proc.returncode:
        raise RuntimeError("GitHub query failed; check connectivity and gh authentication")
    return json.loads(proc.stdout)


def fetch_run(repo, drill_run=None):
    if drill_run is not None:
        run = gh_json(["api", f"repos/{repo}/actions/runs/{drill_run}"])
        # A drill uses a real failed validate run, never a synthetic success/failure.
        if (run["name"] != "validate" or run["status"] != "completed"
                or run["conclusion"] == "success"):
            raise ValueError("drill target must be a completed unsuccessful validate run")
        return {"databaseId": run["id"], "conclusion": run["conclusion"],
                "headSha": run["head_sha"], "url": run["html_url"],
                "updatedAt": run["updated_at"]}
    runs = gh_json(["run", "list", "--repo", repo, "--workflow", "validate.yml",
                    "--branch", "main", "--event", "push", "--status", "completed",
                    "--limit", "1", "--json", "databaseId,conclusion,headSha,url,updatedAt"])
    if not isinstance(runs, list) or len(runs) > 1:
        raise ValueError("unexpected latest-run response")
    return runs[0] if runs else None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--drill-run", type=int, help="read a real failed validate run instead of main")
    args = parser.parse_args(argv)
    try:
        result = assess(fetch_run(args.repo, args.drill_run), dt.datetime.now(dt.timezone.utc))
        result["drill"] = args.drill_run is not None
    except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError):
        # Never turn an absent tool, malformed response or API outage into a green result.
        # Avoid echoing raw subprocess stderr or payloads into persistent alert logs.
        result = {"status": "monitor-error", "detail": "CI health could not be read; check gh/API access",
                  "drill": args.drill_run is not None}
        print(json.dumps(result, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "healthy" else 1


if __name__ == "__main__":
    raise SystemExit(main())
