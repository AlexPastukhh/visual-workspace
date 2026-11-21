"""Strict dependency-free reader for the small YAML subset emitted by test Actions.

This is NOT a general-purpose YAML implementation: it accepts only indented
maps/lists, simple scalars, double-quoted JSON strings and folded plain scalar
lines. Reject unknown syntax instead of guessing. JSON/PyYAML users can still
read the YAML files normally. The catalog verifier does not need pip.
"""
from __future__ import annotations

import json
import re
from typing import Any

_KEY = re.compile(r"[a-z][a-z0-9_]*")
_INT = re.compile(r"(?:0|[1-9][0-9]*)")


class CatalogYamlError(ValueError):
    """Invalid or unsupported syntax in the local catalog YAML subset."""


def parse(text: str) -> dict[str, Any]:
    lines: list[tuple[int, str]] = []
    if not isinstance(text, str) or not text.strip() or len(text) > 64_000:
        raise CatalogYamlError("YAML must be nonempty and no longer than 64 KiB")
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" in line:
            raise CatalogYamlError(f"tabs are not supported: line {number}")
        indent = len(line) - len(line.lstrip(" "))
        if indent % 2 or line.rstrip() != line:
            raise CatalogYamlError(f"invalid indentation/whitespace: line {number}")
        body = line[indent:]
        if body.startswith(('---', '...', '<<', '!', '&', '*', '|', '>')):
            raise CatalogYamlError(f"unsupported YAML construct: line {number}")
        lines.append((indent, body))

    def scalar(raw: str) -> Any:
        if raw == "null":
            return None
        if raw == "true":
            return True
        if raw == "false":
            return False
        if raw == "[]":
            return []
        if _INT.fullmatch(raw):
            return int(raw)
        if raw.startswith('"'):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise CatalogYamlError(f"bad JSON-compatible quoted scalar: {raw}") from exc
            if not isinstance(value, str):
                raise CatalogYamlError("only quoted strings supported")
            return value
        if not raw or raw.startswith(("{", "[", "'", "!", "&", "*", "|", ">", "- ")):
            raise CatalogYamlError(f"unsupported scalar: {raw!r}")
        if ' #' in raw or raw.endswith(':') or raw.startswith(('---', '...')):
            raise CatalogYamlError(f"ambiguous scalar: {raw!r}")
        return raw

    def mapping(items: list[tuple[int, str]], start: int, indent: int) -> tuple[dict, int]:
        out: dict[str, Any] = {}
        at = start
        while at < len(items):
            level, body = items[at]
            if level < indent:
                break
            if level != indent or body.startswith('- '):
                raise CatalogYamlError(f"expected map key at indentation {indent}: {body}")
            key, sep, rest = body.partition(':')
            if not sep or not _KEY.fullmatch(key) or key in out:
                raise CatalogYamlError(f"unknown or duplicate map key: {body}")
            if rest and not rest.startswith(' '):
                raise CatalogYamlError(f"mapping colon must have a space: {body}")
            rest = rest.lstrip(' ')
            at += 1
            if not rest:
                if at == len(items) or items[at][0] <= indent:
                    raise CatalogYamlError(f"missing nested value for {key}")
                if items[at][0] != indent + 2:
                    raise CatalogYamlError(f"nested key {key} requires two-space indent")
                value, at = block(items, at, indent + 2)
            else:
                if at < len(items) and items[at][0] > indent:
                    # Folded multiline plain scalar, never arbitrary nested data.
                    if rest.startswith('"'):
                        raise CatalogYamlError(f"quoted multiline scalar unsupported for {key}")
                    chunks = [rest]
                    while at < len(items) and items[at][0] > indent:
                        child_indent, child = items[at]
                        if child_indent != indent + 2 or ': ' in child or child.startswith('- '):
                            raise CatalogYamlError(f"unexpected nested value for {key}: {child}")
                        chunks.append(child)
                        at += 1
                    value = scalar(' '.join(chunks))
                else:
                    value = scalar(rest)
            out[key] = value
        if not out:
            raise CatalogYamlError('empty mapping')
        return out, at

    def sequence(items: list[tuple[int, str]], start: int, indent: int) -> tuple[list, int]:
        out: list[Any] = []
        at = start
        while at < len(items):
            level, body = items[at]
            if level < indent:
                break
            if level != indent or not body.startswith('- '):
                raise CatalogYamlError(f"expected list item at indentation {indent}: {body}")
            first = body[2:]
            at += 1
            children: list[tuple[int, str]] = [(indent + 2, first)]
            while at < len(items) and items[at][0] > indent:
                children.append(items[at])
                at += 1
            if re.match(r'[a-z][a-z0-9_]*:', first):
                obj, consumed = mapping(children, 0, indent + 2)
                if consumed != len(children):
                    raise CatalogYamlError('extra list item map content')
                out.append(obj)
            else:
                if len(children) != 1:
                    raise CatalogYamlError('nested plain scalar list item unsupported')
                out.append(scalar(first))
        if not out:
            raise CatalogYamlError('empty list')
        return out, at

    def block(items: list[tuple[int, str]], start: int, indent: int) -> tuple[Any, int]:
        if items[start][0] != indent:
            raise CatalogYamlError('unexpected indentation')
        if items[start][1].startswith('- '):
            return sequence(items, start, indent)
        return mapping(items, start, indent)

    if not lines or lines[0][0] != 0:
        raise CatalogYamlError('root mapping must begin at column 0')
    value, index = block(lines, 0, 0)
    if index != len(lines) or not isinstance(value, dict):
        raise CatalogYamlError('incomplete or non-mapping document')
    return value
