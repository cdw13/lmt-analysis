#!/usr/bin/env python3
"""
Scan the repository Python files for imports from the `lmtanalysis` package
and produce a CSV `xref_callers_callees.csv` with columns:
caller,callee_module,callee_member,line,import_type

Run from repo root: python tools/generate_xref.py
"""
import os
import re
import csv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

IMPORT_FROM_RE = re.compile(r'^\s*from\s+lmtanalysis(?:\.|\s+import\s+)([A-Za-z0-9_.*, \n]+)')
FROM_SPEC_RE = re.compile(r'^\s*from\s+lmtanalysis\.([A-Za-z0-9_]+)\s+import\s+(.+)$')
IMPORT_RE = re.compile(r'^\s*import\s+lmtanalysis\.([A-Za-z0-9_]+)(?:\s+as\s+\w+)?')
FROM_PACKAGE_RE = re.compile(r'^\s*from\s+lmtanalysis\s+import\s+(.+)$')

rows = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    # skip hidden dirs
    if any(p.startswith('.') for p in dirpath.split(os.sep)):
        continue
    for fname in filenames:
        if not fname.endswith('.py'):
            continue
        path = os.path.join(dirpath, fname)
        rel = os.path.relpath(path, ROOT)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, start=1):
                    m = FROM_SPEC_RE.match(line)
                    if m:
                        module = m.group(1)
                        members = [s.strip() for s in m.group(2).split(',')]
                        for mem in members:
                            rows.append((rel, module + '.py', mem, i, 'from_module'))
                        continue

                    m2 = IMPORT_RE.match(line)
                    if m2:
                        module = m2.group(1)
                        rows.append((rel, module + '.py', '', i, 'import_module'))
                        continue

                    m3 = FROM_PACKAGE_RE.match(line)
                    if m3:
                        members = [s.strip() for s in m3.group(1).split(',')]
                        for mem in members:
                            # mem often names modules imported from package
                            rows.append((rel, mem + '.py', '', i, 'from_package'))
                        continue
        except Exception:
            continue

outpath = os.path.join(ROOT, 'xref_callers_callees.csv')
with open(outpath, 'w', newline='', encoding='utf-8') as csvf:
    writer = csv.writer(csvf)
    writer.writerow(['caller', 'callee_module', 'callee_member', 'line', 'import_type'])
    for r in rows:
        writer.writerow(r)

print(f'Wrote {len(rows)} rows to {outpath}')
