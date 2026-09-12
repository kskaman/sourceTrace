import os
import sys
import argparse
from pathlib import Path

from .ingest import ingest_corpus

def valid_source_path(value: str) -> Path:
    """Convert a CLI value to a Path and reject paths that do not exist."""
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise argparse.ArgumentTypeError(f"path does not exist: {path}")
    if not (path.is_file() or path.is_dir()):
        raise argparse.ArgumentTypeError(f"path is not a file or directory: {path}")
    return path

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest local text into an index or chat with an existing index."
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest and index a file or folder."
    )
    ingest_parser.add_argument(
        "path",
        type=valid_source_path,
        help="Path to an existing text file or folder.",
    )
    

    chat_parser = subparsers.add_parser(
        "chat", help="Search interactively through already indexed text."
    )
    
    chat_parser.add_argument(
        "--results",
        type=int,
        default=10,
        help="Maximum retrieved chunks per question (default: 10).",
    )

    return parser

def main():
    args = build_parser().parse_args()

    try:
        if args.mode == "ingest":
            ingest_corpus(str(args.path))
        elif args.mode == "chat":
            print(f"Chatting with max results: {args.results}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())