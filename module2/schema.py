"""Small offline validator for the Draft 2020-12 subset used by Module 2.

The shipped JSON Schemas remain the public contract. This implementation keeps
the CLI usable in restricted/offline environments without weakening validation.
"""
import json
import math
import re
from pathlib import Path


def _type_ok(value, expected):
    types = expected if isinstance(expected, list) else [expected]
    for kind in types:
        if kind == 'object' and isinstance(value, dict): return True
        if kind == 'array' and isinstance(value, list): return True
        if kind == 'string' and isinstance(value, str): return True
        if kind == 'boolean' and isinstance(value, bool): return True
        if kind == 'null' and value is None: return True
        if kind == 'number' and isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value): return True
        if kind == 'integer' and isinstance(value, int) and not isinstance(value, bool): return True
    return False


def _json_equal(left, right):
    # Python considers True == 1; JSON Schema correctly distinguishes booleans.
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    return type(left) is type(right) and left == right


def errors(instance, schema, root=None, path='$'):
    root = schema if root is None else root
    if '$ref' in schema:
        ref = schema['$ref']
        if not ref.startswith('#/'):
            yield f'{path}: unsupported reference {ref}'
            return
        target = root
        for key in ref[2:].split('/'):
            target = target[key.replace('~1', '/').replace('~0', '~')]
        yield from errors(instance, target, root, path)
        return
    if 'type' in schema and not _type_ok(instance, schema['type']):
        yield f'{path}: expected {schema["type"]}'
        return
    if 'const' in schema and not _json_equal(instance, schema['const']):
        yield f'{path}: must equal const'
    if 'enum' in schema and not any(_json_equal(instance, value) for value in schema['enum']):
        yield f'{path}: value outside enum'
    for keyword, fn in [('minimum', lambda x, n: x >= n), ('maximum', lambda x, n: x <= n),
                        ('exclusiveMinimum', lambda x, n: x > n), ('exclusiveMaximum', lambda x, n: x < n)]:
        if keyword in schema and isinstance(instance, (int, float)) and not isinstance(instance, bool) and not fn(instance, schema[keyword]):
            yield f'{path}: violates {keyword}'
    if isinstance(instance, str):
        if len(instance) < schema.get('minLength', 0): yield f'{path}: string too short'
        if 'pattern' in schema and re.search(schema['pattern'], instance) is None: yield f'{path}: pattern mismatch'
    if isinstance(instance, list):
        if len(instance) < schema.get('minItems', 0): yield f'{path}: array too short'
        if len(instance) > schema.get('maxItems', math.inf): yield f'{path}: array too long'
        if schema.get('uniqueItems') and len({json.dumps(x, sort_keys=True) for x in instance}) != len(instance): yield f'{path}: array items not unique'
        if 'items' in schema:
            for i, value in enumerate(instance): yield from errors(value, schema['items'], root, f'{path}[{i}]')
    if isinstance(instance, dict):
        for key in schema.get('required', []):
            if key not in instance: yield f'{path}: missing {key}'
        props = schema.get('properties', {})
        for key, value in instance.items():
            if key in props: yield from errors(value, props[key], root, f'{path}.{key}')
            elif schema.get('additionalProperties') is False: yield f'{path}: unsupported property {key}'
            elif isinstance(schema.get('additionalProperties'), dict): yield from errors(value, schema['additionalProperties'], root, f'{path}.{key}')
    for keyword, predicate in [('oneOf', lambda n: n == 1), ('anyOf', lambda n: n > 0)]:
        if keyword in schema:
            count = sum(not list(errors(instance, branch, root, path)) for branch in schema[keyword])
            if not predicate(count): yield f'{path}: {keyword} branch count {count}'
    if 'not' in schema and not list(errors(instance, schema['not'], root, path)):
        yield f'{path}: matches forbidden schema'


def validate_instance(instance, schema):
    found = list(errors(instance, schema))
    if found:
        raise ValueError('Schema: ' + found[0])


def load_schema(path):
    return json.loads(Path(path).read_text())
