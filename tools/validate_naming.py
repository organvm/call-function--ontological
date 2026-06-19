#!/usr/bin/env python3
"""
Validate file names against the FUNCTIONcalled naming convention.

Pattern: {Layer}.{Role}.{Domain}.{Extension}
Layers: core|interface|logic|application (or aliases: bones|skins|breath|body)

Python source files (.py) in layer directories are exempt because Python's import
system requires module_name.py format — dot-separated names would break imports.
Test files, example scripts, and standard project config files are also excluded.
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Canonical layers and their aliases
LAYERS = {
    'core': 'bones',
    'interface': 'skins',
    'logic': 'breath',
    'application': 'body',
}
LAYER_ALIASES = {v: k for k, v in LAYERS.items()}
ALL_LAYERS = set(LAYERS.keys()) | set(LAYERS.values())

# Pattern: optional "example." prefix, then Layer.Role.Domain.Extension
# Role and Domain can have multiple segments separated by dots
NAMING_PATTERN = re.compile(
    r'^(?:example\.)?'  # Optional example prefix
    r'(?P<profile>light|full\.)?'  # Optional profile for example files
    r'(?P<layer>' + '|'.join(ALL_LAYERS) + r')\.'  # Layer (required)
    r'(?P<role>[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)*)\.'  # Role (one or more segments)
    r'(?P<domain>[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)*)\.'  # Domain (one or more segments)
    r'(?P<ext>[a-z]+)$',  # File extension
    re.IGNORECASE
)

# Files/directories to exclude from validation
EXCLUDE_PATTERNS = [
    r'^\..*',  # Dotfiles
    r'^_.*',  # Underscore-prefixed files (includes __init__.py)
    r'^README.*',
    r'^LICENSE.*',
    r'^CLAUDE\.md$',  # Claude Code config file
    r'^GEMINI\.md$',  # Gemini CLI config file
    r'^AGENTS\.md$',  # AI Agents guidelines
    r'^seed\.yaml$',  # Project seed metadata
    r'^sexy_metadata_engine\.html$',  # Legacy metadata tool
    r'^Makefile$',
    r'^.*\.meta\.json$',  # Metadata sidecars validated separately
    r'^\.gitkeep$',
    r'^template\.[a-z]+$',  # Template files are exempt
    r'^.*\.schema\.json$',  # Schema files
    r'^registry\.json$',
    r'^.*\.example\.json$',
    r'^CHANGELOG\.md$',  # Project changelog
    r'^CONTRIBUTING\.md$',  # Contribution guidelines
    r'^CODE_OF_CONDUCT\.md$',  # Code of conduct
    r'^.*\.code-snippets$',  # VS Code snippets
    r'^pyproject\.toml$',  # Python project configuration
    r'^setup\.py$',  # Legacy Python packaging
    r'^setup\.cfg$',  # Legacy Python packaging
    r'^\d{4}-\d{2}-\d{2}-.*',  # Date-prefixed session/log files
    r'^ecosystem\.yaml$',  # Project-level ecosystem configuration
]

EXCLUDE_DIRS = [
    '.git',
    '.github',
    '.venv',  # Virtual environment
    '.vscode',  # VS Code settings
    '.pytest_cache',  # Pytest cache
    '__pycache__',
    'node_modules',
    'tools',  # Tools directory exempt
    'standards',  # Standards directory exempt
    'registry',  # Registry directory exempt
    'archive',  # Archive directory exempt
    'docs',  # Documentation directory exempt
    'tests',  # Test files follow pytest conventions, not FUNCTIONcalled
    'examples',  # Example scripts follow their own conventions
    'ecosystem',  # Ecosystem configuration directory exempt
]


def is_python_package_dir(dirpath: Path) -> bool:
    """Check if a directory is a Python package (contains __init__.py)."""
    return (dirpath / '__init__.py').exists()


def is_excluded(path: Path, root: Path) -> bool:
    """Check if a file or its parent directories should be excluded."""
    # Check directory exclusions
    parts = path.relative_to(root).parts
    for part in parts[:-1]:  # Check all parent directories
        if part in EXCLUDE_DIRS:
            return True

    # Check file exclusions
    filename = path.name
    for pattern in EXCLUDE_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            return True

    # Python source files in layer directories that are Python packages
    # are exempt — Python imports require module_name.py format,
    # not Layer.Role.Domain.py
    if filename.endswith('.py'):
        parent = path.parent
        parent_name = parent.name
        if parent_name.lower() in ALL_LAYERS and is_python_package_dir(parent):
            return True

    return False


def validate_name(filename: str) -> tuple[bool, str]:
    """
    Validate a filename against the FUNCTIONcalled naming convention.

    Returns:
        (is_valid, message)
    """
    match = NAMING_PATTERN.match(filename)
    if match:
        layer = match.group('layer').lower()
        # Normalize alias to canonical name
        canonical_layer = LAYER_ALIASES.get(layer, layer)
        return True, f"Valid: layer={canonical_layer}, role={match.group('role')}, domain={match.group('domain')}"

    return False, f"Does not match pattern {{Layer}}.{{Role}}.{{Domain}}.{{Extension}}"


def validate_directory(root: str, verbose: bool = False) -> list[tuple[str, str]]:
    """
    Walk directory and validate all non-excluded files.

    Returns:
        List of (filepath, error_message) tuples for invalid files
    """
    root_path = Path(root).resolve()
    errors = []
    checked = 0

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter out excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        current_path = Path(dirpath)

        for filename in filenames:
            filepath = current_path / filename

            if is_excluded(filepath, root_path):
                if verbose:
                    print(f"⏭️  Skipped: {filepath.relative_to(root_path)}")
                continue

            checked += 1
            is_valid, message = validate_name(filename)

            if is_valid:
                if verbose:
                    print(f"✅ {filepath.relative_to(root_path)}: {message}")
            else:
                errors.append((str(filepath.relative_to(root_path)), message))
                print(f"❌ {filepath.relative_to(root_path)}: {message}")

    if not errors:
        print(f"\n✅ All {checked} checked files follow the naming convention.")
    else:
        print(f"\n❌ {len(errors)} of {checked} files do not follow the naming convention.")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate file names against FUNCTIONcalled naming convention"
    )
    parser.add_argument(
        '--root',
        default='.',
        help='Root directory to validate (default: current directory)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show all files including skipped and valid ones'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Specific files to validate (overrides --root scan)'
    )

    args = parser.parse_args()

    if args.files:
        # Validate specific files
        errors = []
        for filepath in args.files:
            filename = Path(filepath).name
            is_valid, message = validate_name(filename)
            if is_valid:
                print(f"✅ {filepath}: {message}")
            else:
                errors.append((filepath, message))
                print(f"❌ {filepath}: {message}")

        if errors:
            sys.exit(1)
    else:
        # Scan directory
        errors = validate_directory(args.root, verbose=args.verbose)
        if errors:
            sys.exit(1)


if __name__ == '__main__':
    main()
