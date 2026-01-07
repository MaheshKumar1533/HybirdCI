import subprocess
import os

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
