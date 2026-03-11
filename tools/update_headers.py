#!/usr/bin/env python3
"""
Enrich existing non-functional headers (those containing HEADER_ADDED_BY_) with
# Module: update_headers.py.
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs)
# Outputs: plots (matplotlib) and images
# Dependencies: numpy, pandas, matplotlib, tkinter, sqlite3
# Example: Example: import update_headers or run as script if __main__ present.
to generate a short, unique description per file. It updates only text files
that already have the marker inserted by tools/add_headers.py to avoid
touching other files.

Run from repo root: python tools/update_headers.py
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MARKER_RE = re.compile(r'HEADER_ADDED_BY_')

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write(path, contents):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(contents)

def make_py_block(lines):
    return '\n'.join('# ' + l if l else '#' for l in lines) + '\n'

def make_md_block(lines):
    block = '\n'.join('<!-- ' + l + ' -->' if l else '<!-- -->' for l in lines)
    return block + '\n'

def infer_description(path, contents):
    name = os.path.basename(path)
    rel = os.path.relpath(path, ROOT)
    lines = []

    # Short one-line summary from file name and any top docstring
    summary = None
    # try to capture module docstring
    m = re.search(r"^[uU]?[rR]?\"\"\"([\s\S]{0,200}?)\"\"\"", contents)
    if not m:
        m = re.search(r"^[uU]?[rR]?\'\'\'([\s\S]{0,200}?)\'\'\'", contents)
    if m:
        summary = m.group(1).strip().splitlines()[0]

    if not summary:
        # fallbacks based on filename patterns
        if name.startswith('BuildEvent'):
            summary = f"Event-builder module for {name.replace('BuildEvent','').replace('.py','')}."
        elif 'FileUtil' in name:
            summary = 'Utility helpers to open files/folders and load .sqlite/.json inputs via tkinter.'
        elif 'TaskLogger' in name:
            summary = 'Small helper to read/write the `LOG` table in experiment sqlite databases.'
        elif name.startswith('Parameters') or 'Parameter' in name:
            summary = 'Project parameters/constants (thresholds, sizes, speeds) for animals.'
        elif name.startswith('Measure') or 'Measure' in name:
            summary = 'Computation helpers for measures (distance, speed, durations).' 
        elif 'README' in name or name.endswith('.md'):
            summary = 'Repository README / documentation.'
        elif '/examples/' in rel or rel.startswith('LMT/examples'):
            summary = 'Example script demonstrating common analysis flows (uses FileUtil dialogs).'
        else:
            summary = f'Module: {name}.'

    lines.append(summary)
    lines.append('')

    # Inputs/Outputs/Dependencies/Example sections
    # Inputs
    if '.sqlite' in contents or 'sqlite' in contents.lower() or 'getFilesToProcess' in contents:
        inp = '.sqlite tracking DB files (Live Mouse Tracker outputs)'
    elif '/.json' in contents or 'json' in contents.lower():
        inp = 'json configuration or profile files'
    elif '/.csv' in contents or 'csv' in contents.lower():
        inp = 'CSV files'
    else:
        inp = 'varies; see module for specifics (often .sqlite or json)'
    lines.append('Inputs: ' + inp)

    # Outputs
    if 'plot' in contents or 'matplotlib' in contents:
        out = 'plots (matplotlib) and images'
    elif 'INSERT INTO LOG' in contents or 'LOG' in contents:
        out = 'log table updates in sqlite DB' 
    elif 'csv' in contents or 'to_csv' in contents:
        out = 'CSV reports or tables'
    else:
        out = 'in-memory objects, event tables, or files depending on callers'
    lines.append('Outputs: ' + out)

    # Dependencies (best-effort)
    deps = []
    if 'numpy' in contents:
        deps.append('numpy')
    if 'pandas' in contents:
        deps.append('pandas')
    if 'matplotlib' in contents:
        deps.append('matplotlib')
    if 'tkinter' in contents or 'askopenfilename' in contents:
        deps.append('tkinter')
    if 'sqlite3' in contents or 'sqlite' in contents.lower():
        deps.append('sqlite3')
    if not deps:
        deps = ['standard library or project modules']
    lines.append('Dependencies: ' + ', '.join(deps))

    # Example (very short)
    if '/examples/' in rel or rel.startswith('LMT/examples'):
        ex = f'Run as: python {rel}'
    elif name.endswith('.py'):
        ex = f'Example: import {os.path.splitext(name)[0]} or run as script if __main__ present.'
    else:
        ex = 'See examples in LMT/examples for usage.'
    lines.append('Example: ' + ex)

    return lines

def update_file(path):
    contents = read(path)
    if not MARKER_RE.search(contents):
        return False

    # detect comment style by looking at first lines
    if path.endswith('.py'):
        comment_block = make_py_block(infer_description(path, contents))
        # Insert after existing marker lines (keep existing marker and date lines)
        # Replace the initial simple header (first 4 lines) with enriched block
        parts = contents.splitlines(True)
        # find index of marker line
        idx = 0
        for i, line in enumerate(parts[:10]):
            if 'HEADER_ADDED_BY_' in line:
                idx = i
                break
        # find end of the three-line auto header (marker + added on + non-functional)
        end_idx = min(len(parts), idx+4)
        new = ''.join(parts[:idx+1]) + comment_block + ''.join(parts[end_idx:])
        write(path, new)
        return True

    if path.endswith('.md'):
        comment_block = make_md_block(infer_description(path, contents))
        parts = contents.splitlines(True)
        idx = 0
        for i, line in enumerate(parts[:10]):
            if 'HEADER_ADDED_BY_' in line:
                idx = i
                break
        end_idx = min(len(parts), idx+3)
        new = ''.join(parts[:idx+1]) + comment_block + ''.join(parts[end_idx:])
        write(path, new)
        return True

    if path.endswith('.txt'):
        comment_block = make_py_block(infer_description(path, contents))
        parts = contents.splitlines(True)
        idx = 0
        for i, line in enumerate(parts[:10]):
            if 'HEADER_ADDED_BY_' in line:
                idx = i
                break
        end_idx = min(len(parts), idx+3)
        new = ''.join(parts[:idx+1]) + comment_block + ''.join(parts[end_idx:])
        write(path, new)
        return True

    return False

def main():
    changed = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # skip hidden dirs
        if any(p.startswith('.') for p in dirpath.split(os.sep)):
            continue
        for name in filenames:
            path = os.path.join(dirpath, name)
            if not (path.endswith('.py') or path.endswith('.md') or path.endswith('.txt')):
                continue
            try:
                if update_file(path):
                    changed.append(path)
            except Exception as e:
                print('Error processing', path, e)

    print(f'Updated headers in {len(changed)} files')
    for p in changed[:50]:
        print(p)

if __name__ == '__main__':
    main()
