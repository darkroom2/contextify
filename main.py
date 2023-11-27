#!/usr/bin/env python3

import argparse
from pathlib import Path

import pyperclip
import python_minifier
import tiktoken


def validate_directory(directory: Path) -> None:
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory.")


def validate_arguments(args: argparse.Namespace) -> None:
    validate_directory(args.directory)

    if not args.prompt:
        raise ValueError("Prompt cannot be empty.")

    if args.exclude:
        args.exclude += ",.git/**/*"
    else:
        args.exclude = ".git/**/*"


def get_gitignore_patterns(directory: Path) -> set[str]:
    # TODO: parse .gitignore file to pathlib.Path.glob compatible patterns
    return set()


def get_patterns(pattern_str: str, default_pattern: str = "*") -> set[str]:
    return set(pattern_str.split(",")) if pattern_str else {default_pattern}


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
    return {file_path: content for (file_path, content) in map(minify_file, file_paths)}


def create_file_str(file_name: str, file_content: str) -> str:
    return f"File `{file_name}`:\n```python\n{file_content}\n```"


def create_final_prompt(
    files: dict[Path, str],
    root_directory: Path,
    prompt: str,
    prompt_header: str = "Here is the context of my current project.",
    prompt_footer: str = "Use best practices and clean code techniques. Try your best!",
) -> str:
    files_str = "\n".join(
        [
            create_file_str(
                file_path.relative_to(root_directory).as_posix(), file_content
            )
            for (file_path, file_content) in files.items()
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

    include_patterns = get_patterns(args.include)
    exclude_patterns = get_patterns(args.exclude)
    gitignore_patterns = get_gitignore_patterns(args.directory)

    file_paths = get_file_paths(
        args.directory, include_patterns, exclude_patterns | gitignore_patterns
    )
    files = minify_files(file_paths)
    final_prompt = create_final_prompt(files, args.directory, args.prompt)
    pyperclip.copy(final_prompt)

    print("Following files were minified:")
    for file_path in files:
        print(f"    {file_path.relative_to(args.directory).as_posix()}")
    print()

    tokens_count = len(tiktoken.get_encoding("cl100k_base").encode(final_prompt))
    print(f"Total tokens: {tokens_count}")
    print("Prompt copied to clipboard!")


if __name__ == "__main__":
    main()
