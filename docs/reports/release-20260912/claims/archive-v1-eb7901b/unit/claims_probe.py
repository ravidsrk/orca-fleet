"""Fixture-only source probes; these do not certify legal or mission conformance."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def module(path):
    spec = importlib.util.spec_from_file_location(path.stem.replace('-', '_'), path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


parser = argparse.ArgumentParser()
parser.add_argument('case', choices=['provenance', 'hooks', 'oncall', 'badge'])
parser.add_argument('--root', type=Path, default=Path.cwd())
args = parser.parse_args()
root = args.root.resolve()
print('root:', root)
print('commit:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip())
if args.case == 'provenance':
    verifier = module(root / 'runtime/scripts/verify.py')
    packet = {'provenance': dict(standard='EU-AI-Act-Art-12', spec_version='fixture-v1',
                                model='fixture-model', reviewer='fixture-reviewer',
                                retention='fixture-pointer')}
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / 'output.txt'
        output.write_text('Synthetic fixture content without machine-readable AI marking.\n')
        errors = verifier.check_provenance(packet)
        assert errors == [], errors
        assert sorted(p.name for p in Path(tmp).iterdir()) == ['output.txt']
        print('COUNTEREXAMPLE: presence check accepts all four strings; no logger or marking exists.')
        del packet['provenance']['retention']
        errors = verifier.check_provenance(packet)
        assert errors and 'retention' in errors[0], errors
        print('POSITIVE CONTROL: missing retention is rejected:', errors)
elif args.case == 'hooks':
    env = {key: value for key, value in os.environ.items() if not key.startswith('ORCA_')}
    for event, expected in [('stop', 0), ('task', 2)]:
        proc = subprocess.run(['sh', str(root / 'runtime/scripts/verify-gate.sh'), '--event', event],
                              cwd=root, env=env, text=True, capture_output=True, check=False)
        print(f'event={event}, exit={proc.returncode}: {proc.stdout}{proc.stderr}'.strip())
        assert proc.returncode == expected
    print('COUNTEREXAMPLE: installed Stop hook permits an idle turn without running a verifier.')
    print('POSITIVE CONTROL: TaskCompleted without evidence still blocks.')
elif args.case == 'oncall':
    mission = (root / 'skills/oncall-it/SKILL.md').read_text()
    row = next(line for line in (root / 'docs/runs/README.md').read_text().splitlines()
               if line.startswith('| oncall-it |'))
    allowed = set(re.findall(r'^- \*\*([A-Z][A-Z-]+)\*\*', mission, re.MULTILINE))
    declared = set(re.findall(r'`([A-Z][A-Z-]+)`', row.split('|')[4]))
    print('authoritative mission terminal states:', sorted(allowed))
    print('field-proof plan row:', row)
    assert allowed == {'OPERABLE', 'OPERABLE-WITH-PARKED'}
    assert 'RESOLVED' not in allowed  # Incident resolution is the negative scenario.
    assert declared and declared <= allowed, f'plan terminals {declared} violate mission {allowed}'
    print('PASS: plan terminal states exist in the mission; blind-run semantics require walkthrough.')
else:
    generator = module(root / 'scripts/gen-badges.py')
    with tempfile.TemporaryDirectory() as tmp:
        generator.TESTS_DIR = Path(tmp)
        test = Path(tmp) / 'test_fixture.py'
        badges = []
        for value, expected in [('False', 1), ('True', 0)]:
            test.write_text('import unittest\nclass Fixture(unittest.TestCase):\n'
                            '    def test_behavior(self):\n'
                            f'        self.assertTrue({value})\n')
            proc = subprocess.run(['python3', '-B', '-m', 'unittest', 'discover', '-s', tmp],
                                  text=True, capture_output=True, check=False)
            badge = generator.compute()['tests.json']
            badges.append(badge)
            print(json.dumps({'fixture': value, 'test_exit': proc.returncode, 'badge': badge}))
            print(proc.stderr)
            assert proc.returncode == expected
        assert badges[0] == badges[1]
        print('COUNTEREXAMPLE: failing and passing fixtures yield identical public passing badge.')
