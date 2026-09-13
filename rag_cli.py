import os
import sys
import argparse
from pathlib import Path

def valid_source_path(value: str) -> Path:
    """Convert a CLI value to a Path and reject paths that do not exist."""
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise argparse.ArgumentTypeError(f"path does not exist: {path}")
    if not (path.is_file() or path.is_dir()):
        raise argparse.ArgumentTypeError(f"path is not a file or directory: {path}")
    return path


class HelpfulArgumentParser(argparse.ArgumentParser):
    """Argument parser that shows full usage help (not just a usage line) on bad input."""

    def error(self, message):
        show_help(self, message)


def show_help(parser: argparse.ArgumentParser, reason: str | None = None) -> None:
    """Print the required parameters, and why the given arguments were rejected."""
    parser.print_help(sys.stderr)
    if reason:
        print(f"\nWhy this failed: {reason}", file=sys.stderr)
    sys.exit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = HelpfulArgumentParser(
        description="Ingest local text into an index or chat with an existing index."
    )
    subparsers = parser.add_subparsers(
        dest="mode",
        required=True,
        title="modes",
        metavar="MODE",
        help="Operation mode: ingest or chat.",
    )
    
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

def chat_loop(max_results: int = 10, answer_fn=None):
    print("Entering chat mode. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        if answer_fn is None:
            from src.retrieve.pipeline import answer

            answer_fn = answer

        response = answer_fn(
            question=user_input,
            k=max(50, max_results),
            n=max_results,
            use_reranker=True,
        )
        print(f"Assistant: {response['answer']}")
        print(f"\nContext: {response['context']}\n")


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.mode == "ingest":
            # Imported lazily: this pulls in the embedding model, which is slow to
            # load and only needed once we know ingestion is actually happening.
            from src.ingest import ingest_corpus
            ingest_corpus(str(args.path))
        elif args.mode == "chat":
            chat_loop(args.results)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())