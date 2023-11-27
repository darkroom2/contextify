import argparse
from pathlib import Path

import pyperclip
import python_minifier


def validate_arguments(args: argparse.Namespace) -> None:
    directory = args.directory
    if not directory.exists():
        raise FileNotFoundError(f"Directory {directory} does not exist.")
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory.")
    if not args.prompt:
        raise ValueError("Prompt cannot be empty.")
    if args.exclude:
        args.exclude += ",.git/**/*"
    else:
        args.exclude = ".git/**/*"


def get_gitignore_patterns(directory: Path) -> set[str]:
    return set()


def get_include_patterns(include_str: str) -> set[str]:
    include_patterns = include_str.split(",") if include_str else ["*"]
    return set(include_patterns)


def get_exclude_patterns(exclude_str: str) -> set[str]:
    exclude_patterns = exclude_str.split(",") if exclude_str else []
    return set(exclude_patterns)


def get_file_paths(
    directory: Path, include_patterns: set[str], exclude_patterns: set[str]
) -> set[Path]:
    included_files = {
        path
        for pattern in include_patterns
        for path in directory.rglob(pattern)
        if path.is_file()
    }
    excluded_files = {
        path
        for pattern in exclude_patterns
        for path in directory.rglob(pattern)
        if path.is_file()
    }
    return included_files - excluded_files


def minify_file(file_path: Path) -> tuple[Path, str]:
    raw_content = file_path.read_text(encoding="utf-8")

    if file_path.suffix != ".py":
        return file_path, raw_content

    minified_content = python_minifier.minify(
        raw_content,
        remove_literal_statements=True,
        rename_locals=False,
        remove_annotations=False,
    )
    return file_path, minified_content


def minify_files(file_paths: set[Path]) -> dict[Path, str]:
    return {file_path: content for file_path, content in map(minify_file, file_paths)}


def create_final_prompt(
    files: dict[Path, str],
    root_directory: Path,
    prompt: str,
    prompt_header: str = "Here is the context of my current project:",
    prompt_footer: str = "Use best practices and clean code techniques. Try your best!",
) -> str:
    files_str = "\n".join(
        [
            f"File `{file_path.relative_to(root_directory).as_posix()}`.\n```python\n{file_content}\n```"
            for file_path, file_content in files.items()
        ]
    )
    return f"{prompt_header}\n{files_str}.\n{prompt}\n{prompt_footer}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gather project files, minify Python ones, and concatenate all of them into one prompt."
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
    validate_arguments(args)

    include_patterns = get_include_patterns(args.include)
    exclude_patterns = get_exclude_patterns(args.exclude)
    gitignore_patterns = get_gitignore_patterns(args.directory)

    file_paths = get_file_paths(
        args.directory, include_patterns, exclude_patterns | gitignore_patterns
    )
    files = minify_files(file_paths)
    final_prompt = create_final_prompt(files, args.directory, args.prompt)
    pyperclip.copy(final_prompt)


if __name__ == "__main__":
    main()
