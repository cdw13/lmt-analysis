# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: add_headers.py.
#
# Inputs: varies; see module for specifics (often .sqlite or json)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: standard library or project modules
# Example: Example: import add_headers or run as script if __main__ present.
#!/usr/bin/env python3
"""
Utility to prepend a non-functional header comment to text source files
in this repository. Adds a marker to avoid duplicate insertion.

Run from repo root: python tools/add_headers.py
"""
import os
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HEADER_DATE = '2026-02-11'
AUTHOR = 'GitHub Copilot'
MARKER = f'HEADER_ADDED_BY_{AUTHOR.replace(" ","_").upper()}_{HEADER_DATE}'

def should_process(path):
    if any(part.startswith('.') for part in path.split(os.sep)):
        return False
    if '/__pycache__/' in path or path.endswith('.pyc'):
        return False
    if path.endswith('.py') or path.endswith('.md') or path.endswith('.txt'):
        return True
    return False

def make_header(path):
    if path.endswith('.py'):
        return [f"# {MARKER}", f"# Added on {HEADER_DATE} by {AUTHOR}", "# Non-functional header — no code changes", "\n"]
    if path.endswith('.md'):
        return [f"<!-- {MARKER} -->", f"<!-- Added on {HEADER_DATE} by {AUTHOR} -->", "<!-- Non-functional header -->", "\n"]
    if path.endswith('.txt'):
        return [f"# {MARKER}", f"# Added on {HEADER_DATE} by {AUTHOR}", "# Non-functional header", "\n"]
    return []

def has_marker(contents):
    return MARKER in contents

def process_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            contents = f.read()
    except Exception:
        return False

    if has_marker(contents):
        return False

    header_lines = make_header(path)
    if not header_lines:
        return False

    new_contents = '\n'.join(header_lines) + contents
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_contents)
        return True
    except Exception:
        return False

def main():
    changed = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # skip .git and hidden dirs
        if any(p.startswith('.') for p in dirpath.split(os.sep)):
            continue
        for name in filenames:
            path = os.path.join(dirpath, name)
            if should_process(path):
                if process_file(path):
                    changed.append(path)

    print(f"Header added to {len(changed)} files")
    for p in changed:
        print(p)

if __name__ == '__main__':
    main()
