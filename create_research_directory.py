#!/usr/bin/env python3
"""Create a dated research directory without replacing earlier results."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional


def slugify(topic: str) -> str:
    slug = re.sub(r"\s+", "-", topic.strip())
    slug = re.sub(r"[^\w.-]+", "-", slug, flags=re.UNICODE)
    slug = re.sub(r"[-_.]{2,}", "-", slug).strip("-_.")
    return slug[:72].rstrip("-_.") or "research"


def create_unique_directory(target: Path) -> Path:
    target = target.expanduser().absolute()
    if not target.name:
        raise ValueError("Provide an output directory below the filesystem root")
    # Keep the requested leaf so an existing link counts as a collision.
    target = target.parent.resolve() / target.name
    if target.exists() and not target.is_dir() and not target.is_symlink():
        raise NotADirectoryError(f"Output path is not a directory: {target}")

    suffix = 1
    while True:
        candidate = target if suffix == 1 else target.with_name(f"{target.name}-{suffix:02d}")
        try:
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate
        except FileExistsError:
            suffix += 1


def create_research_directory(
    base_dir: Path,
    topic: str,
    date_value: Optional[str] = None,
) -> Path:
    run_date = date.fromisoformat(date_value) if date_value else date.today()
    base = base_dir.expanduser().resolve()
    if base.exists() and not base.is_dir():
        raise NotADirectoryError(f"Output base is not a directory: {base}")
    return create_unique_directory(base / f"{run_date.isoformat()}-{slugify(topic)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", help="Short demand topic used in the directory name")
    parser.add_argument("--base-dir", type=Path, default=None, help="Defaults to ./outputs")
    parser.add_argument("--date", dest="date_value", help="ISO date override (YYYY-MM-DD)")
    parser.add_argument("--output-dir", type=Path, help="Exact requested output directory")
    args = parser.parse_args()

    if args.output_dir is None and not args.topic:
        parser.error("provide --topic or --output-dir")

    try:
        if args.output_dir is not None:
            ignored = [
                flag
                for flag, value in (("--topic", args.topic), ("--base-dir", args.base_dir), ("--date", args.date_value))
                if value is not None
            ]
            if ignored:
                # stdout carries only the created path, so the note goes to stderr.
                print(f"note: {', '.join(ignored)} ignored because --output-dir was given", file=sys.stderr)
            output = create_unique_directory(args.output_dir)
        else:
            base_dir = args.base_dir if args.base_dir is not None else Path.cwd() / "outputs"
            output = create_research_directory(base_dir, args.topic, args.date_value)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))

    print(output)


if __name__ == "__main__":
    main()

