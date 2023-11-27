import argparse
from pathlib import Path

import pyperclip
import python_minifier


def get_gitignore_patterns(directory: Path) -> set[str]:
    return set()


def get_include_patterns(include_str: str | None) -> set[str]:
    include_patterns = include_str.split(",") if include_str else ["*"]
    return set(include_patterns)


def get_exclude_patterns(exclude_str: str | None) -> set[str]:
    exclude_patterns = exclude_str.split(",") if exclude_str else []
    return set(exclude_patterns)


def get_file_paths(
    directory: Path, include_patterns: set[str], exclude_patterns: set[str]
) -> set[Path]:
    included_files = set()
    for pattern in include_patterns:
        filtered_paths = filter(lambda path: path.is_file(), directory.rglob(pattern))
        included_files.update(filtered_paths)

    excluded_files = set()
    for pattern in exclude_patterns:
        filtered_paths = filter(lambda path: path.is_file(), directory.rglob(pattern))
        excluded_files.update(filtered_paths)

    return included_files - excluded_files


def main():
    parser = argparse.ArgumentParser(
        description="Gather project files, minify Python ones and concatenate all of them into one prompt."
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path.cwd(),
        help="directory to search for files",
    )
    parser.add_argument(
        "--include", type=str, default="*", help="pattern for files to include"
    )
    parser.add_argument(
        "--exclude", type=str, default=None, help="pattern for files to exclude"
    )
    parser.add_argument("prompt", type=str, help="prompt to be appended to the end")
    args = parser.parse_args()

    if not args.directory.exists():
        raise FileNotFoundError(f"Directory {args.directory} does not exist.")

    if not args.directory.is_dir():
        raise NotADirectoryError(f"{args.directory} is not a directory.")

    if not args.prompt:
        raise ValueError("Prompt cannot be empty.")

    if args.exclude:
        args.exclude += ",.git/**/*"
    else:
        args.exclude = ".git/**/*"

    include_patterns = get_include_patterns(args.include)
    exclude_patterns = get_exclude_patterns(args.exclude)
    gitignore_patterns = get_gitignore_patterns(args.directory)

    file_paths = get_file_paths(
        args.directory, include_patterns, exclude_patterns | gitignore_patterns
    )

    files = {
        file_path.relative_to(args.directory).as_posix(): python_minifier.minify(
            file_path.read_text(encoding="utf-8"),
            remove_literal_statements=True,
            rename_locals=False,
        )
        for file_path in file_paths
        if file_path.suffix == ".py"
    }

    files_str = "\n".join(
        [
            f"File `{file_name}`.\n```python\n{file_content}\n```"
            for file_name, file_content in files.items()
        ]
    )

    prompt_header = "Here is the context of my current project:"
    prompt_footer = "Use best practices and clean code techniques. Try your best!"

    final_prompt = f"{prompt_header}\n{files_str}.\n{args.prompt}\n{prompt_footer}"

    pyperclip.copy(final_prompt)


if __name__ == "__main__":
    main()
