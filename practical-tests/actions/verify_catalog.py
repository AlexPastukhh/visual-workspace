#!/usr/bin/env python3
"""Read-only structural and input-integrity check for the local Action test kit.

Uses a small strict subset of YAML, without external Python packages.
Does not execute Actions or read hidden evaluator answers. Reference PNGs
must already be in the accepted Git tree: never substitute another worktree.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from yaml_subset import parse as parse_catalog_yaml


ACTIONS = Path(__file__).resolve().parent
REPO = ACTIONS.parent.parent
REQUIRED_ACTIONS = {'VT01', 'VT02', 'VT03', 'VT04', 'VT07', 'VT08', 'VT09', 'VT10', 'VT11', 'VT12', 'VT15'}
CORE_KEYS = {'name', 'category', 'instruction', 'workflow', 'schedule'}
KINDS = {'authoring', 'reference_creation', 'reference_edit', 'visual_review', 'evaluation'}
BASES = {'visual_detail', 'defect_detectability', 'not_applicable'}


def read_yaml(file: Path) -> dict:
    return parse_catalog_yaml(file.read_text(encoding='utf-8'))


def resolve_repo_path(value: str) -> Path:
    assert isinstance(value, str) and value and not value.startswith('/'), value
    assert '\\' not in value and all(x not in ('', '.', '..') for x in value.split('/')), value
    local = REPO / value
    assert local.resolve().is_relative_to(REPO.resolve()), value
    assert local.is_file(), f'missing required accepted path: {value}'
    return local


def check_action_core_shape(doc: dict) -> None:
    assert set(doc) <= CORE_KEYS and {'name', 'instruction'} <= set(doc), doc
    assert isinstance(doc['name'], str) and 0 < len(doc['name'].strip()) <= 200
    assert isinstance(doc['instruction'], str) and 0 < len(doc['instruction'].strip()) <= 32000
    assert doc.get('category') == 'visual_testing'
    # V1 tests are executed by people in ChatGPT, not through Core's programmatic Workflow.
    assert 'workflow' not in doc and 'schedule' not in doc


def check_catalog() -> tuple[int, int]:
    action_dirs = sorted(p for p in ACTIONS.iterdir() if p.is_dir() and re.fullmatch(r'VT\d\d', p.name))
    ids = {p.name for p in action_dirs}
    assert REQUIRED_ACTIONS <= ids, f'missing first-library Actions: {REQUIRED_ACTIONS - ids}'
    unit_ids: set[str] = set()
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
                resolve_repo_path(inp['brief'])
            assert isinstance(inp['reference_pngs'], list) and isinstance(inp['visual_cases'], list)
            if doc['kind'] in ('reference_creation', 'reference_edit'):
                assert inp['reference_pngs'], f'{key} requires pinned PNG'
            for reference in inp['reference_pngs']:
                assert set(reference) == {'path', 'sha256'}
                assert re.fullmatch('[0-9a-f]{64}', reference['sha256'])
                file = resolve_repo_path(reference['path'])
                assert file.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n', file
                assert hashlib.sha256(file.read_bytes()).hexdigest() == reference['sha256'], file
            for case in inp['visual_cases']:
                assert re.fullmatch('clip-[a-z0-9]+', case)
                folder_path = REPO / 'practical-tests/visual/cases' / case
                assert (folder_path / 'brief.md').is_file()
                capture = json.loads((folder_path / 'capture.json').read_text())
                assert capture['frame_count'] == len(list((folder_path / 'frames').glob('frame_*.png')))
                assert (folder_path / 'contact_sheet.png').is_file()
            assert isinstance(v['legacy_sources'], list)
            for legacy in v['legacy_sources']:
                resolve_repo_path(legacy)
            assert isinstance(v['steps'], list) and v['steps']
            for step in v['steps']:
                assert set(step) in ({'unit_id', 'work_prompt', 'evaluation_prompt'},
                                    {'unit_id', 'work_prompt', 'evaluation_prompt', 'case_ids'})
                assert re.fullmatch(r'(?:VT\d\d|SV\d\d)\.[A-Za-z0-9.]+', step['unit_id'])
                assert step['unit_id'] not in unit_ids, step['unit_id']
                unit_ids.add(step['unit_id'])
                prompt_file = resolve_repo_path(step['work_prompt'])
                prompt_text = prompt_file.read_text(encoding='utf-8')
                if doc['kind'] != 'evaluation':
                    assert step['unit_id'] in prompt_text, step['unit_id']
                    assert 'submission.md' in prompt_text, prompt_file
                    assert 'image_gen' in prompt_text, prompt_file
                    assert f'actionId={folder.name}' in prompt_text, prompt_file
                    assert f'variantId={v["id"]}' in prompt_text, prompt_file
                for reference in inp['reference_pngs']:
                    if doc['kind'] != 'evaluation':
                        # Second stage of a reference-edit flow inherits the
                        # previously pinned PNG; the handoff binds both stages.
                        if len(v['steps']) == 1 or step == v['steps'][0]:
                            assert reference['path'] in prompt_text, prompt_file
                            assert reference['sha256'] in prompt_text, prompt_file
                if step['evaluation_prompt'] is None:
                    assert doc['kind'] == 'evaluation'
                else:
                    assert '_evaluator/' not in step['work_prompt']
                    resolve_repo_path(step['evaluation_prompt'])
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
    print('REFERENCE_INPUTS_ACCEPTED_IN_CURRENT_TREE')
    print(f'ACTION_CATALOG_PASS actions={len(action_dirs)} variants={len(variants)} stages={stage_count}')
    return len(action_dirs), stage_count


def main():
    check_catalog()


if __name__ == '__main__':
    main()
