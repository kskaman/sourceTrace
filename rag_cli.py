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


def valid_data_folder(value: str) -> str:
    """Trim a data folder name and reject reserved or empty values."""
    data_folder = value.strip()
    if not data_folder:
        raise argparse.ArgumentTypeError("folder name cannot be empty")
    if data_folder.casefold() == "default":
        raise argparse.ArgumentTypeError(
            "folder name 'default' is reserved; choose a specific name"
        )
    return data_folder


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
        description="Ingest, query, and manage named folders of indexed local data."
    )
    subparsers = parser.add_subparsers(
        dest="mode",
        required=True,
        title="modes",
        metavar="MODE",
        help="Operation mode for indexed data and folder management.",
    )
    
    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest and index a file or folder."
    )
    ingest_parser.add_argument(
        "path",
        type=valid_source_path,
        help="Path to an existing text file or folder.",
    )
    ingest_parser.add_argument(
        "--folder",
        required=True,
        type=valid_data_folder,
        help="Named data folder to store the indexed content in.",
    )

    chat_parser = subparsers.add_parser(
        "chat", help="Search interactively through already indexed text."
    )
    chat_parser.add_argument(
        "--folder",
        required=True,
        type=valid_data_folder,
        help="Named data folder to search.",
    )
    chat_parser.add_argument(
        "--results",
        type=int,
        default=10,
        help="Maximum retrieved chunks per question (default: 10).",
    )

    delete_parser = subparsers.add_parser(
        "delete-folder", help="Delete all indexed data in a named folder."
    )
    delete_parser.add_argument(
        "--folder",
        required=True,
        type=valid_data_folder,
        help="Named data folder to delete.",
    )
    delete_parser.add_argument(
        "--yes",
        action="store_true",
        help="Delete without asking for confirmation.",
    )

    subparsers.add_parser(
        "list-folders", help="List indexed data folders and their contents."
    )

    rename_parser = subparsers.add_parser(
        "rename-folder", help="Rename an indexed data folder."
    )
    rename_parser.add_argument(
        "--folder",
        required=True,
        type=valid_data_folder,
        help="Current data folder name.",
    )
    rename_parser.add_argument(
        "--new-name",
        required=True,
        type=valid_data_folder,
        help="New data folder name.",
    )

    return parser

def chat_loop(data_folder: str, max_results: int = 10, answer_fn=None):
    print(f"Entering chat mode for folder '{data_folder}'. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        if answer_fn is None:
            from src.retrieve import answer

            answer_fn = answer

        response = answer_fn(
            question=user_input,
            data_folder=data_folder,
            k=max(50, max_results),
            n=max_results,
            use_reranker=True,
        )
        print(f"Assistant: {response['answer']}")
        print(f"\nContext: {response['context']}\n")


def delete_folder(data_folder: str, assume_yes: bool = False) -> int:
    """Confirm and delete every indexed chunk in a named data folder."""
    if not assume_yes:
        confirmation = input(
            f"Type the folder name '{data_folder}' to permanently delete it: "
        )
        if confirmation != data_folder:
            print("Deletion cancelled.")
            return 0

    from src.database import delete_data_folder, get_connection

    conn = get_connection()
    try:
        deleted_count = delete_data_folder(data_folder, conn)
    finally:
        conn.close()

    if deleted_count:
        print(f"Deleted folder '{data_folder}' ({deleted_count} chunks).")
    else:
        print(f"Folder '{data_folder}' was not found; nothing was deleted.")
    return deleted_count


def list_folders() -> list[dict]:
    """Print named data folders with document and chunk counts."""
    from src.database import get_connection, list_data_folders

    conn = get_connection()
    try:
        folders = list_data_folders(conn)
    finally:
        conn.close()

    if not folders:
        print("No data folders found.")
        return folders

    print("Data folders:")
    for folder in folders:
        print(
            f"  {folder['name']}: {folder['document_count']} documents, "
            f"{folder['chunk_count']} chunks"
        )
    return folders


def rename_folder(data_folder: str, new_name: str) -> int:
    """Rename a data folder and report the number of chunks updated."""
    from src.database import get_connection, rename_data_folder

    conn = get_connection()
    try:
        renamed_count = rename_data_folder(data_folder, new_name, conn)
    finally:
        conn.close()

    if renamed_count:
        print(
            f"Renamed folder '{data_folder}' to '{new_name}' "
            f"({renamed_count} chunks)."
        )
    else:
        print(f"Folder '{data_folder}' was not found; nothing was renamed.")
    return renamed_count


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.mode == "ingest":
            # Imported lazily: this pulls in the embedding model, which is slow to
            # load and only needed once we know ingestion is actually happening.
            from src.ingest import ingest_corpus
            ingest_corpus(str(args.path), args.folder)
        elif args.mode == "chat":
            chat_loop(args.folder, args.results)
        elif args.mode == "delete-folder":
            delete_folder(args.folder, args.yes)
        elif args.mode == "list-folders":
            list_folders()
        elif args.mode == "rename-folder":
            rename_folder(args.folder, args.new_name)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())