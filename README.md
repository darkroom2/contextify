# contextify

**contextify** is a Python utility designed to seamlessly compile and minify project files, creating a comprehensive context prompt tailored for language models like GPT.

## Overview

When working with language models, providing a meaningful context is crucial for generating relevant responses. **contextify** simplifies this process by:

- Compiling and minifying project files.
- Creating a comprehensive context prompt.

## Features

- **File Compilation:** Automatically compiles and minifies project files, optimizing them for language model input.

- **Context Prompt Generation:** Builds a context prompt by concatenating the minified content of project files. This ensures that the language model understands the context of your project.

## Usage

### Installation

```shell
pip install contextify
```

### Running

```shell
contextify --directory /path/to/your/project --include "*.py" --exclude "tests/*.py" "Your custom prompt here."
```

Replace `/path/to/your/project` with the path to your project directory. Adjust the `--include` and `--exclude` options to specify file patterns for inclusion and exclusion. Finally, provide your custom prompt within the quotes.

The compiled and minified files, along with your prompt, will be copied to the clipboard.

## Example

Consider the following Python project structure:

```
/project
|-- main.py
|-- module1.py
|-- module2.py
|-- README.md
```

Running the command:

```shell
contextify --directory /path/to/project --include "*.py" "Here is the context of my current project."
```

Will generate a context prompt with the minified content of `main.py`, `module1.py`, and `module2.py`, along with your custom prompt.

## Best Practices

- **Optimized Compilation:** Project files are compiled and minified for optimal token usage.

- **Prompt Structure:** Generated prompts adhere to a structured format for effective utilization by language models.

## TODO

- [ ] create python package installable from git or PyPI
- [ ] add tests
- [ ] add CI/CD  
