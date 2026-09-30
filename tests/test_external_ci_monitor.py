"""The external monitor must page on missing, red, stale and unreadable CI."""
import contextlib
import datetime as dt
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / 'scripts/external-ci-monitor.py'
SPEC = importlib.util.spec_from_file_location('external_ci_monitor', SCRIPT)
monitor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(monitor)
NOW = dt.datetime(2026, 9, 30, 10, tzinfo=dt.timezone.utc)


def run(conclusion='success', age=1):
    return {'conclusion': conclusion, 'updatedAt': (NOW-dt.timedelta(hours=age)).isoformat(),
            'headSha': 'a'*40, 'url': 'https://github.com/example/repo/actions/runs/7', 'databaseId': 7}


class HealthVerdicts(unittest.TestCase):
    def test_recent_success_is_healthy(self):
        self.assertEqual(monitor.assess(run(), NOW)['status'], 'healthy')

    def test_staleness_is_exactly_24_hours(self):
        self.assertEqual(monitor.assess(run(age=23.99), NOW)['status'], 'healthy')
        self.assertEqual(monitor.assess(run(age=24), NOW)['status'], 'stale')

    def test_non_success_and_missing_runs_alert(self):
        for result in ('failure', 'cancelled', 'timed_out', 'skipped', 'action_required'):
            with self.subTest(result=result):
                self.assertEqual(monitor.assess(run(result), NOW)['status'], 'red')
        self.assertEqual(monitor.assess(None, NOW)['status'], 'missing')

    def test_malformed_completed_run_cannot_be_green(self):
        for change in ({'updatedAt': None}, {'updatedAt': 'yesterday'}, {'updatedAt': '2026-09-30T10:00:00'},
                       {'updatedAt': '2026-10-01T10:00:00Z'}, {'conclusion': None}):
            with self.subTest(change=change), self.assertRaises((ValueError, TypeError)):
                monitor.assess({**run(), **change}, NOW)


class GitHubReader(unittest.TestCase):
    def test_latest_query_ignores_in_progress_runs(self):
        with patch.object(monitor, 'gh_json', return_value=[run()]) as gh:
            self.assertEqual(monitor.fetch_run('example/repo')['databaseId'], 7)
        args = gh.call_args.args[0]
        self.assertEqual(args[args.index('--status')+1], 'completed')
        self.assertEqual(args[args.index('--branch')+1], 'main')
        self.assertEqual(args[args.index('--event')+1], 'push')

    def test_empty_or_malformed_response(self):
        with patch.object(monitor, 'gh_json', return_value=[]):
            self.assertIsNone(monitor.fetch_run('example/repo'))
        with patch.object(monitor, 'gh_json', return_value={}), self.assertRaises(ValueError):
            monitor.fetch_run('example/repo')

    def test_drill_requires_a_real_unsuccessful_completed_validate_run(self):
        raw = {'name':'validate', 'status':'completed', 'conclusion':'failure', 'id':7,
               'head_sha':'a'*40, 'html_url':run()['url'], 'updated_at':run()['updatedAt']}
        with patch.object(monitor, 'gh_json', return_value=raw):
            self.assertEqual(monitor.fetch_run('example/repo', 7)['conclusion'], 'failure')
        for change in ({'name':'install'}, {'status':'in_progress'}, {'conclusion':'success'}):
            with self.subTest(change=change), patch.object(monitor, 'gh_json', return_value={**raw,**change}), self.assertRaises(ValueError):
                monitor.fetch_run('example/repo', 7)

    def test_api_error_does_not_echo_sensitive_stderr(self):
        failed = subprocess.CompletedProcess(['gh'], 1, '', 'private response')
        with patch.object(monitor.subprocess, 'run', return_value=failed), self.assertRaises(RuntimeError) as error:
            monitor.gh_json(['run','list'])
        self.assertNotIn('private response', str(error.exception))

    def test_exit_contract_and_authentication_failure(self):
        for value, expected in ((run(),0), (run('failure'),1), (None,1)):
            with self.subTest(expected=expected), patch.object(monitor,'fetch_run',return_value=value), contextlib.redirect_stdout(io.StringIO()) as output:
                # Wall clock is later than the fixed fixture; recent success needs a current date.
                if value is not None:
                    value['updatedAt'] = dt.datetime.now(dt.timezone.utc).isoformat()
                self.assertEqual(monitor.main([]), expected)
                self.assertIn('status', json.loads(output.getvalue()))
        for error in (OSError(), RuntimeError(), subprocess.TimeoutExpired('gh',45), ValueError()):
            with self.subTest(error=type(error)), patch.object(monitor,'fetch_run',side_effect=error), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(monitor.main([]),2)
                self.assertEqual(json.loads(output.getvalue())['status'],'monitor-error')


if __name__ == '__main__':
    unittest.main()
