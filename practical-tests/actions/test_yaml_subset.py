#!/usr/bin/env python3
"""Dependency-free self-check for the deliberately bounded catalog YAML reader."""
from __future__ import annotations

from pathlib import Path
import unittest

from yaml_subset import CatalogYamlError, parse

ROOT = Path(__file__).resolve().parent


class StrictSubsetTests(unittest.TestCase):
    def test_every_catalog_definition(self):
        files = sorted(ROOT.glob('VT*/action.yaml'))
        files += sorted(ROOT.glob('VT*/visual-testing.yaml'))
        files += sorted((ROOT / 'collections').glob('*.yaml'))
        self.assertGreaterEqual(len(files), 26)
        for file in files:
            with self.subTest(file=file.relative_to(ROOT)):
                content = parse(file.read_text(encoding='utf-8'))
                self.assertIsInstance(content, dict)
                self.assertTrue(content)

    def test_nested_and_folded_values(self):
        obj = parse('''name: Example
instruction: multi line
  folded here
category: visual_testing
variants:
  - id: example
    difficulty:
      level: L2
      basis: visual_detail
    refs: []
    active: true
    count: 12
    other: null
''')
        self.assertEqual(obj['instruction'], 'multi line folded here')
        self.assertEqual(obj['variants'][0]['difficulty']['level'], 'L2')
        self.assertEqual(obj['variants'][0]['refs'], [])
        self.assertEqual(obj['variants'][0]['count'], 12)
        self.assertIsNone(obj['variants'][0]['other'])

    def test_human_review_policy_of_existing_variants(self):
        creation = {'VT01', 'VT02', 'VT03', 'VT04', 'VT07', 'VT08', 'VT09', 'VT10'}
        chat_only = {'VT11', 'VT12', 'VT15'}
        for id in sorted(creation | chat_only):
            definition = parse((ROOT / id / 'visual-testing.yaml').read_text(encoding='utf-8'))
            for variant in definition['variants']:
                with self.subTest(action=id, variant=variant['id']):
                    flag = variant['human_review_required']
                    self.assertIs(type(flag), bool)
                    self.assertEqual(flag, id in creation)

    def test_visual_review_uses_keyed_scoring_not_second_detection(self):
        for id in ('VT11', 'VT12'):
            doc = parse((ROOT / id / 'visual-testing.yaml').read_text(encoding='utf-8'))
            self.assertEqual(doc['kind'], 'visual_review')
            for variant in doc['variants']:
                self.assertIs(variant['human_review_required'], False)
                self.assertEqual(len(variant['steps']), 2)
                for number, step in enumerate(variant['steps'], 1):
                    with self.subTest(action=id, stage=number):
                        path = step['evaluation_prompt']
                        self.assertTrue(path.startswith(f'practical-tests/actions/{id}/prompts/'))
                        content = (ROOT.parent.parent / path).read_text(encoding='utf-8')
                        self.assertIn('DEFECT-SCORING.md', content)
                        if number == 1:
                            self.assertIn('только процессный gate', content)
                        else:
                            self.assertIn('answer-key.json', content)
                            self.assertIn('defect-score.md', content)

    def test_reject_non_contract_yaml(self):
        invalid = [
            'name: x\nname: y\n',               # duplicates
            'name: x\n  sub: data\n',           # nested under plain scalar
            'name: &ref hello\n',               # anchors
            'name: *ref\n',                     # aliases
            'name: !python/object hi\n',        # tags
            'name: {value: x}\n',               # flow syntax
            'name: [hello, world]\n',           # flow list
            "name: 'single quoted'\n",         # unsupported quotes
            'name:\tX\n',                      # tabs
            ' name: X\n',                       # indentation
            'name: foo\n\n---\nother: bar\n', # multi-document
            'name: foo # ignored?\n',           # ambiguous inline comment
            'items:\n    - value\n',           # uneven nested indentation
            'items:\n  - id: one\n    id: two\n', # duplicated list-item key
            'name: "unterminated\n',            # invalid JSON-style quote
        ]
        for value in invalid:
            with self.subTest(sample=value), self.assertRaises(CatalogYamlError):
                parse(value)


if __name__ == '__main__':
    unittest.main(verbosity=2)
