#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_TARGET = Path('/storage/ice-shared/cs8903onl')


def human_size(num_bytes: int) -> str:
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == 'B':
                return f'{int(value)} {unit}'
            return f'{value:.1f} {unit}'
        value /= 1024
    return f'{num_bytes} B'


def run_text(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout.strip() if p.stdout.strip() else p.stderr.strip()


def run_du_bytes(target: Path) -> dict[str, int]:
    # One traversal for target + immediate child folders only.
    cmd = ['du', '-B1', '-d', '1', str(target)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout
    sizes: dict[str, int] = {}
    for line in out.splitlines():
        parts = line.split('\t', 1)
        if len(parts) != 2:
            continue
        size_str, path_str = parts
        try:
            sizes[path_str] = int(size_str)
        except ValueError:
            continue
    return sizes


def depth_of(path: str, root: str) -> int:
    if path == root:
        return 0
    rel = os.path.relpath(path, root)
    if rel == '.':
        return 0
    return rel.count(os.sep) + 1


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TARGET

    if not target.is_dir():
        print(f'Error: directory not found: {target}', file=sys.stderr)
        return 1

    target_str = str(target)

    print(f'=== Storage Report for: {target} ===')
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print()

    print('[1] Filesystem capacity and current usage (where target is mounted)')
    print(run_text(['df', '-h', target_str]))
    print()

    sizes = run_du_bytes(target)

    print('[2] Size of target directory itself')
    if target_str in sizes:
        target_mtime = datetime.fromtimestamp(target.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{human_size(sizes[target_str])}\t{target_mtime}\t{target_str}")
    else:
        print('Unavailable (could not read size).')
    print()

    print('[3] Top-level folders in target (size + last modified)')
    top_rows: list[tuple[int, str, str]] = []
    for path_str, size in sizes.items():
        if depth_of(path_str, target_str) == 1:
            mtime = 'N/A'
            try:
                mtime = datetime.fromtimestamp(Path(path_str).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            except OSError:
                pass
            top_rows.append((size, mtime, path_str))
    top_rows.sort(key=lambda x: x[0])
    if top_rows:
        for size, mtime, path_str in top_rows:
            print(f"{human_size(size)}\t{mtime}\t{path_str}")
    else:
        print('No top-level folders found or inaccessible.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
