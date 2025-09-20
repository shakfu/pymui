#!/usr/bin/env python3
"""
Script to remove trailing whitespace from files.

Usage:
    python scripts/remove_trailing_whitespace.py [file1] [file2] ...

If no files are specified, processes all files in the current directory recursively.
"""

import argparse
import os
import sys
from pathlib import Path


def remove_trailing_whitespace(file_path):
    """Remove trailing whitespace from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        cleaned_lines = []

        for line in lines:
            # Remove trailing whitespace but preserve the line ending
            if line.endswith('\n'):
                cleaned_line = line.rstrip() + '\n'
            else:
                cleaned_line = line.rstrip()

            if cleaned_line != line:
                modified = True

            cleaned_lines.append(cleaned_line)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            print(f"Cleaned: {file_path}")
            return True
        else:
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def should_process_file(file_path):
    """Check if file should be processed (text files only)."""
    # Skip binary files and common non-text extensions
    skip_extensions = {'.so', '.o', '.pyc', '.pyo', '.pyd', '.exe', '.dll',
                      '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.zip',
                      '.tar', '.gz', '.bz2', '.7z', '.pdf', '.doc', '.docx'}

    if file_path.suffix.lower() in skip_extensions:
        return False

    # Skip hidden files and directories
    if any(part.startswith('.') for part in file_path.parts):
        return False

    # Skip build directories
    skip_dirs = {'build', '__pycache__', '.git', 'node_modules', 'venv', '.venv'}
    if any(part in skip_dirs for part in file_path.parts):
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description='Remove trailing whitespace from files')
    parser.add_argument('files', nargs='*', help='Files to process (default: all files recursively)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')

    args = parser.parse_args()

    if args.files:
        files_to_process = [Path(f) for f in args.files]
    else:
        # Process all files recursively
        files_to_process = [f for f in Path('.').rglob('*') if f.is_file() and should_process_file(f)]

    modified_count = 0

    for file_path in files_to_process:
        if not file_path.exists():
            print(f"Warning: {file_path} does not exist")
            continue

        if not file_path.is_file():
            continue

        if args.dry_run:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                has_trailing_ws = any(line.rstrip() != line.rstrip('\n') for line in lines)
                if has_trailing_ws:
                    print(f"Would clean: {file_path}")
                    modified_count += 1
            except Exception as e:
                print(f"Error checking {file_path}: {e}")
        else:
            if remove_trailing_whitespace(file_path):
                modified_count += 1

    if args.dry_run:
        print(f"\nDry run complete. {modified_count} files would be modified.")
    else:
        print(f"\nComplete. {modified_count} files modified.")


if __name__ == '__main__':
    main()