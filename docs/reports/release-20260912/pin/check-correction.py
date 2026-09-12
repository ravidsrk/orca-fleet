#!/usr/bin/env python3
"""Verify the source-bound inventory graph; --baseline replays the pre-correction defects.

This audits data against immutable Git objects and the independent audit's additions.
It does not test runtime behavior or assign conformance from source declarations.
"""
import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
PREFIX = str(HERE.relative_to(ROOT))


def read(name):
    return json.loads((HERE / name).read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(path, revision):
    return subprocess.check_output(['git', 'show', f'{revision}:{path}'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    corrections = read('claim-corrections.json')
    source = corrections['source_sha']
    base = corrections['baseline_sha']
    frozen = read('claim-inventory.frozen.json')
    original = read('claim-atomization.json')
    current = original if args.baseline else read('claim-current.json')
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    for name in ['claim-inventory.frozen.json', 'claim-atomization.json', 'source-location-audit.json',
                 'contract.json', 'manifest.pre-base-label.json']:
        require((HERE / name).read_bytes() == git(f'{PREFIX}/{name}', base), f'changed protected bytes: {name}')
    require(sha((HERE / 'claim-inventory.frozen.json').read_bytes()) == corrections['frozen_sha256'], 'frozen hash changed')
    for row in read('history/snapshot/inventory.json')['files']:
        data = (HERE / 'history/snapshot' / row['path']).read_bytes()
        require(sha(data) == row['sha256'] and len(data) == row['bytes'], f'snapshot changed: {row["path"]}')
    sources = {}
    for row in frozen['coverage']:
        data = git(row['path'], source)
        sources[row['path']] = data.decode().splitlines()
        require(sha(data) == row['sha256'] and len(data.splitlines()) == row['lines'], f'source coverage mismatch: {row["path"]}')
        require((ROOT / row['path']).read_bytes() == git(row['path'], base), f'doctrine/source changed in correction: {row["path"]}')
    for row in original['children'] + original['excluded_records'] + corrections['added_children'] + corrections['added_parents']:
        for span in [row['source']] + row.get('additional_sources', []):
            lines = sources[span['path']]
            require(span['text'] in '\n'.join(lines[span['line'] - 1:span['end_line']]), f'source quote mismatch: {row["id"]}')
    for row in read('correction-input/review-pin-inventory-ro-source-bindings.json'):
        require(sources[row['path']][row['line'] - 1] == row['text'], f'independent audit quote mismatch: {row["path"]}:{row["line"]}')

    # Reconstruct the graph from unchanged first atomization and explicit additive operations.
    expected = {row['id']: copy.deepcopy(row) for row in original['children']}
    for override in corrections['child_overrides']:
        cid = override['id']
        require(expected[cid] == override['before'], f'override history mismatch: {cid}')
        expected[cid].update(override['changes'])
        expected[cid]['correction'] = {'path': 'claim-corrections.json', 'id': cid,
                                     'reason': override['reason'], 'historical_record': f'claim-atomization.json#{cid}'}
    for row in corrections['added_children']:
        require(row['id'] not in expected, f'reused child ID: {row["id"]}')
        expected[row['id']] = row
    actual = {row['id']: row for row in current['children']}
    require(len(actual) == len(current['children']), 'duplicate child IDs')
    for cid in sorted(set(expected) | set(actual)):
        require(actual.get(cid) == expected.get(cid), f'missing or uncorrected predicate: {cid}')
    for cid, row in actual.items():
        for target in row.get('decomposition', []):
            require(target in actual, f'dangling conjunct: {cid} -> {target}')
        for targets in row.get('links', {}).values():
            for target in targets:
                require(target in actual, f'dangling claim link: {cid} -> {target}')
        for name in row.get('receipt_paths', []):
            require((HERE / name).is_file(), f'missing receipt: {cid} -> {name}')
    excluded = {row['id'] for row in current['excluded_records']}
    mechanics = {row['parent_id'] for row in current['children']}
    original_ids = {row['id'] for row in frozen['claims']}
    appended = {row['id'] for row in corrections['added_parents']}
    require(not (excluded & mechanics), 'parent both wholly excluded and mapped')
    require(excluded | mechanics == original_ids | appended, 'parent denominator or appended coverage lost')
    require(not (original_ids & appended), 'appended parent reuses original ID')
    for row in corrections['mixed_scope_corrections']:
        require(row['id'] in mechanics and row['id'] not in excluded, f'mixed mechanics still excluded: {row["id"]}')

    if not args.baseline:
        counts = dict(Counter(row['disposition'] for row in current['children']))
        require(counts == current['counts'], 'current counts mismatch')
        require(current['mechanics_parent_count'] == len(mechanics), 'mechanics parent count mismatch')
        outstanding = read('outstanding-claims.json')
        unfinished = [row for row in current['children'] if row['disposition'] not in ['WITNESSED', 'PATCHED']]
        require(outstanding['claims'] == unfinished and outstanding['count'] == len(unfinished), 'unfinished register does not equal unresolved predicates')
        continuation = (HERE / 'CONTINUATION.md').read_text()
        require(all(row['id'] in continuation for row in unfinished), 'continuation drops unresolved IDs')
        inventory = read('claim-inventory.json')
        require(inventory['denominator'] == frozen['denominator'], 'original denominator changed')
        require({row['id'] for row in inventory['records']} == original_ids | appended, 'current parent inventory mismatch')
        for row in inventory['records']:
            require(set(row.get('child_ids', [])) == {c['id'] for c in current['children'] if c['parent_id'] == row['id']}, f'parent mapping mismatch: {row["id"]}')
        # Every original receipt remains byte-bound at the baseline; evidence reuse cannot rewrite it.
        manifest = read('history/e2e7adab/manifest.json')
        for artifact in manifest['artifacts']:
            data = git(artifact['path'], base)
            require(sha(data) == artifact['sha256'], f'baseline artifact hash mismatch: {artifact["path"]}')
            if '/receipts/' in artifact['path']:
                require((ROOT / artifact['path']).read_bytes() == data, f'historical receipt changed: {artifact["path"]}')
        for group in read('correction-source-refutations.json')['groups']:
            require(group['verdict'] == 'REPRODUCED-INVENTORY-DEFECT', f'unaccounted audit group: {group["id"]}')
        require(read('parked-register.json')['true_parked_claims'] == [], 'workload park introduced')

        reconciliation = read('correction-evidence-reconciliation.json')

        def result(name):
            return json.loads(read(f'receipts/{name}.json')['stdout'])['result']

        for mapping in reconciliation['reference_retrieval']['mapping']:
            require(bool(mapping['individual_invocations']), f'unmapped reference: {mapping["listed_name"]}')
            for invocation in mapping['individual_invocations']:
                data = read(invocation['path'])
                require(data['argv'] == invocation['argv'] and data['exit'] == 0, f'reference invocation mismatch: {invocation["path"]}')
                require(sha((HERE / invocation['path']).read_bytes()) == invocation['sha256'], 'reference receipt hash mismatch')
        gate_rows = result('helper-gates-during-ask')['gates']
        require(gate_rows == [result('helper-resolve')['gate']], 'ask-time rows differ from preexisting resolved gate')
        require(gate_rows[0]['id'] == result('helper-gate')['gate']['id'], 'gate identity mismatch')
        delivery = result('mailbox-delivery')['messages']
        require(len(delivery) == 50 and {m['type'] for m in delivery} == {'status', 'handoff'}, 'mixed-delivery witness mismatch')
        require([m['id'] for m in delivery] == [m['id'] for m in result('mailbox-replay')['messages']], 'delivery replay mismatch')
        tick = json.loads(read('receipts/mailbox-empty-wait.json')['stderr'])
        require(tick['_keepalive'] is True and tick['_heartbeat'] is True and tick['elapsedMs'] == 15001, 'single marker tick mismatch')
        require(result('followup-bulk-close') == reconciliation['bulk_close']['result'], 'bulk close counts mismatch')
        for identity in reconciliation['bulk_close']['identities']:
            exited = read(identity['exit_receipt'])['result']['terminal']
            data = json.loads(read(identity['identity_receipt'])['stdout'])['result']
            candidates = data.get('terminals', [data.get('terminal')])
            observed = next(row for row in candidates if row['handle'] == identity['handle'])
            require(all(observed[key] == identity[key] for key in ['handle', 'ptyId', 'incarnationId', 'worktreeId']), 'bulk close identity mismatch')
            require(exited['handle'] == identity['handle'] and exited['status'] == 'exited', 'missing authoritative process exit')

    print(json.dumps({'mode': 'original graph negative control' if args.baseline else 'corrected graph',
                      'source_sha': source, 'baseline_sha': base, 'source_files': len(sources),
                      'original_parents': len(original_ids), 'appended_parents': len(appended),
                      'mechanics_parents': len(mechanics), 'excluded_parents': len(excluded),
                      'children': len(actual), 'errors': errors, 'runtime_claims_tested': 0}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
