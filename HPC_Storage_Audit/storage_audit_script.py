# Script Developed By:
# Wai Lung Justin Yiu | Georgia Tech | HAAG Admin | OMSCS | CS 6999 Spring 2026
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


def run_du_human(target: Path) -> list[tuple[str, str]]:
    cmd = ['du', '-h', '-d', '1', str(target)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    rows: list[tuple[str, str]] = []
    for line in p.stdout.splitlines():
        parts = line.split('\t', 1)
        if len(parts) != 2:
            continue
        size_str, path_str = parts
        rows.append((size_str, path_str))
    return rows


def run_du_bytes(target: Path) -> dict[str, int]:
    cmd = ['du', '-B1', '-d', '1', str(target)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    sizes: dict[str, int] = {}
    for line in p.stdout.splitlines():
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
    now = datetime.now().astimezone()
    report_name = f"storage_audit_report_{now.strftime('%Y%m%d')}.txt"
    report_path = DEFAULT_TARGET / report_name
    lines: list[str] = []

    lines.append(f'=== Storage Report for: {target} ===')
    lines.append(f"Generated at: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    lines.append('')

    lines.append('[1] Filesystem capacity and current usage')
    lines.append(run_text(['df', '-h', target_str]))
    lines.append('')

    rows = run_du_human(target)
    size_bytes = run_du_bytes(target)

    lines.append('[2] Top-level folders (size + last modified)')
    top_rows: list[tuple[int, str, str, str]] = []
    for size_str, path_str in rows:
        if depth_of(path_str, target_str) == 1:
            mtime = 'N/A'
            try:
                mtime = datetime.fromtimestamp(Path(path_str).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            except OSError:
                pass
            top_rows.append((size_bytes.get(path_str, -1), size_str, mtime, path_str))
    top_rows.sort(key=lambda row: row[0], reverse=True)
    if top_rows:
        for _size_bytes, size_str, mtime, path_str in top_rows:
            lines.append(f"{size_str}\t{mtime}\t{path_str}")
    else:
        lines.append('No top-level folders found or inaccessible.')

    report_text = '\n'.join(lines) + '\n'
    report_path.write_text(report_text, encoding='utf-8')
    print(report_text, end='')
    print(f"Saved report to: {report_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
