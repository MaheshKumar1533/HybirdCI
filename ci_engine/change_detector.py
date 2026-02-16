import subprocess
import os
from pathlib import Path
from ci_engine.cache_manager import get_file_language

def get_changed_files():
    try:
        # Case 1: Normal diff
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True,
            text=True
        )
        files = result.stdout.splitlines()

        if files:
            return files

        # Case 2: No diff → use last commit files
        result = subprocess.run(
            ["git", "show", "--name-only", "--pretty=format:"],
            capture_output=True,
            text=True
        )
        files = result.stdout.splitlines()
        return [f for f in files if f.endswith(".py")]

    except:
        # Case 3: Git edge cases
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True
        )
        return result.stdout.splitlines()

def get_changed_files_by_language():
    """Get changed files grouped by programming language."""
    changed_files = get_changed_files()
    language_map = {}
    
    for file in changed_files:
        lang = get_file_language(file)
        if lang not in language_map:
            language_map[lang] = []
        language_map[lang].append(file)
    
    return language_map, changed_files

def filter_changes_by_language(changed_files, language=None):
    """Filter changed files by language. If language is None, returns all."""
    if language is None:
        return changed_files
    
    return [f for f in changed_files if get_file_language(f) == language]
