#!/usr/bin/env python3
"""Read-only structural and input-integrity check for the local Action test kit.

Requires PyYAML (see requirements-check.txt). Does not execute Actions or read
hidden evaluator answers. For pre-merge PR16 review only, use
--candidate-reference-root; default readiness requires files in this Git tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError as exc:
    raise SystemExit('PyYAML is required: pip install -r practical-tests/actions/requirements-check.txt') from exc


ACTIONS = Path(__file__).resolve().parent
REPO = ACTIONS.parent.parent
EXPECTED_V1 = {'VT01', 'VT02', 'VT07', 'VT08', 'VT11', 'VT12', 'VT15'}
CORE_KEYS = {'name', 'category', 'instruction', 'workflow', 'schedule'}
KINDS = {'authoring', 'reference_creation', 'reference_edit', 'visual_review', 'evaluation'}
BASES = {'visual_detail', 'defect_detectability', 'not_applicable'}


class StrictLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise ValueError('YAML aliases are prohibited')
        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key, _ in node.value:
            k = self.construct_object(key, deep=deep)
            if not isinstance(k, str) or k in seen:
                raise ValueError(f'duplicate/non-text YAML key: {k!r}')
            seen.add(k)
        return super().construct_mapping(node, deep=deep)


def read_yaml(file: Path) -> dict:
    raw = file.read_text(encoding='utf-8')
    assert len(raw) <= 64_000, file
    doc = yaml.load(raw, Loader=StrictLoader)
    assert isinstance(doc, dict), file
    return doc


def resolve_repo_path(value: str, candidate_root: Path | None, *, allow_candidate: bool) -> tuple[Path, bool]:
    assert isinstance(value, str) and value and not value.startswith('/'), value
    assert '\\' not in value and all(x not in ('', '.', '..') for x in value.split('/')), value
    local = REPO / value
    assert local.resolve().is_relative_to(REPO.resolve()), value
    if local.is_file():
        return local, False
    if allow_candidate and candidate_root is not None:
        other = candidate_root / value
        assert other.resolve().is_relative_to(candidate_root.resolve()), value
        if other.is_file():
            return other, True
    raise AssertionError(f'missing required accepted path: {value}')


def check_action_core_shape(doc: dict) -> None:
    assert set(doc) <= CORE_KEYS and {'name', 'instruction'} <= set(doc), doc
    assert isinstance(doc['name'], str) and 0 < len(doc['name'].strip()) <= 200
    assert isinstance(doc['instruction'], str) and 0 < len(doc['instruction'].strip()) <= 32000
    assert doc.get('category') == 'visual_testing'
    # V1 tests are executed by people in ChatGPT, not through Core's programmatic Workflow.
    assert 'workflow' not in doc and 'schedule' not in doc


def check_catalog(candidate_root: Path | None) -> tuple[int, int]:
    action_dirs = sorted(p for p in ACTIONS.iterdir() if p.is_dir() and re.fullmatch(r'VT\d\d', p.name))
    ids = {p.name for p in action_dirs}
    assert EXPECTED_V1 <= ids, f'missing V1 Actions: {EXPECTED_V1 - ids}'
    unit_ids: set[str] = set()
    candidate_used: list[str] = []
    variants: dict[tuple[str, str], dict] = {}
    stage_count = 0
    for folder in action_dirs:
        core = read_yaml(folder / 'action.yaml')
        check_action_core_shape(core)
        assert core['name'].startswith(folder.name + ' — ')
        doc = read_yaml(folder / 'visual-testing.yaml')
        assert set(doc) == {'schema_version', 'action_id', 'kind', 'capability', 'difficulty_basis', 'default_variant', 'variants'}
        assert type(doc['schema_version']) is int and doc['schema_version'] == 1
        assert doc['action_id'] == folder.name
        assert doc['kind'] in KINDS and doc['difficulty_basis'] in BASES
        assert isinstance(doc['capability'], str) and doc['capability']
        assert isinstance(doc['variants'], list) and doc['variants']
        assert any(v['id'] == doc['default_variant'] for v in doc['variants'])
        for v in doc['variants']:
            assert set(v) == {'id', 'difficulty', 'inputs', 'steps', 'legacy_sources'}
            key = (folder.name, v['id'])
            assert key not in variants and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', v['id'])
            variants[key] = v
            difficulty = v['difficulty']
            assert set(difficulty) == {'level', 'basis', 'rationale'}
            assert difficulty['basis'] == doc['difficulty_basis']
            assert difficulty['level'] in ('L1', 'L2', 'L3', None)
            assert isinstance(difficulty['rationale'], str) and difficulty['rationale'].strip()
            if doc['kind'] == 'evaluation':
                assert difficulty['level'] is None and difficulty['basis'] == 'not_applicable'
            elif doc['kind'] == 'visual_review':
                assert difficulty['basis'] == 'defect_detectability'
            else:
                assert difficulty['basis'] == 'visual_detail' and difficulty['level'] is not None
            inp = v['inputs']
            assert set(inp) == {'brief', 'reference_pngs', 'visual_cases'}
            if inp['brief'] is not None:
                resolve_repo_path(inp['brief'], candidate_root, allow_candidate=False)
            assert isinstance(inp['reference_pngs'], list) and isinstance(inp['visual_cases'], list)
            if doc['kind'] in ('reference_creation', 'reference_edit'):
                assert inp['reference_pngs'], f'{key} requires pinned PNG'
            for reference in inp['reference_pngs']:
                assert set(reference) == {'path', 'sha256'}
                assert re.fullmatch('[0-9a-f]{64}', reference['sha256'])
                file, pending = resolve_repo_path(reference['path'], candidate_root, allow_candidate=True)
                assert file.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n', file
                assert hashlib.sha256(file.read_bytes()).hexdigest() == reference['sha256'], file
                if pending:
                    candidate_used.append(reference['path'])
            for case in inp['visual_cases']:
                assert re.fullmatch('clip-[a-z0-9]+', case)
                folder_path = REPO / 'practical-tests/visual/cases' / case
                assert (folder_path / 'brief.md').is_file()
                capture = json.loads((folder_path / 'capture.json').read_text())
                assert capture['frame_count'] == len(list((folder_path / 'frames').glob('frame_*.png')))
                assert (folder_path / 'contact_sheet.png').is_file()
            assert isinstance(v['legacy_sources'], list)
            for legacy in v['legacy_sources']:
                _, pending = resolve_repo_path(legacy, candidate_root, allow_candidate=True)
                if pending:
                    candidate_used.append(legacy)
            assert isinstance(v['steps'], list) and v['steps']
            for step in v['steps']:
                assert set(step) in ({'unit_id', 'work_prompt', 'evaluation_prompt'},
                                    {'unit_id', 'work_prompt', 'evaluation_prompt', 'case_ids'})
                assert re.fullmatch(r'(?:VT\d\d|SV\d\d)\.[A-Za-z0-9.]+', step['unit_id'])
                assert step['unit_id'] not in unit_ids, step['unit_id']
                unit_ids.add(step['unit_id'])
                resolve_repo_path(step['work_prompt'], candidate_root, allow_candidate=False)
                if step['evaluation_prompt'] is None:
                    assert doc['kind'] == 'evaluation'
                else:
                    assert '_evaluator/' not in step['work_prompt']
                    resolve_repo_path(step['evaluation_prompt'], candidate_root, allow_candidate=False)
                for case in step.get('case_ids', []):
                    assert case in inp['visual_cases'], (step['unit_id'], case)
                stage_count += 1
        print(f'ACTION_OK {folder.name} {len(doc["variants"])} variants')

    for collection_file in sorted((ACTIONS / 'collections').glob('*.yaml')):
        c = read_yaml(collection_file)
        assert set(c) == {'schema_version', 'id', 'description', 'items'}
        assert c['schema_version'] == 1 and collection_file.stem == c['id']
        assert c['items'] and len(c['items']) == len({(i['action_id'], i['variant_id']) for i in c['items']})
        for item in c['items']:
            assert set(item) == {'action_id', 'variant_id'}
            assert (item['action_id'], item['variant_id']) in variants
        print(f'COLLECTION_OK {c["id"]} {len(c["items"])} variants')
    if candidate_used:
        assert candidate_root is not None
        print('CANDIDATE_REFERENCE_ONLY: reference-driven Actions BLOCKED until these paths exist in accepted main:')
        for p in sorted(set(candidate_used)):
            print('  ' + p)
    else:
        print('REFERENCE_INPUTS_ACCEPTED_IN_CURRENT_TREE')
    print(f'ACTION_CATALOG_PASS actions={len(action_dirs)} variants={len(variants)} stages={stage_count} candidate={bool(candidate_used)}')
    return len(action_dirs), stage_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate-reference-root', type=Path, help='PR16 candidate checkout for pre-merge structural review only; not accepted as runnable main')
    args = parser.parse_args()
    if args.candidate_reference_root:
        assert args.candidate_reference_root.is_dir()
    check_catalog(args.candidate_reference_root)


if __name__ == '__main__':
    main()
