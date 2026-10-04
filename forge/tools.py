import subprocess
from pathlib import Path
from .safety.permissions import validate_command


WORKSPACE = Path.cwd().resolve()


def safe_path(path: str) -> Path:
    target = (WORKSPACE / path).resolve()

    if not target.is_relative_to(WORKSPACE):
        raise ValueError("Path is outside the workspace.")

    return target


def list_files(path: str = ".") -> str:
    target = safe_path(path)

    if not target.exists():
        return f"Error: {path} does not exist."

    if not target.is_dir():
        return f"Error: {path} is not a directory."

    entries = []

    for item in sorted(target.iterdir()):
        prefix = "[DIR]" if item.is_dir() else "[FILE]"
        entries.append(f"{prefix} {item.name}")

    return "\n".join(entries) or "(empty directory)"


def read_file(path: str) -> str:
    target = safe_path(path)

    if not target.exists():
        return f"Error: {path} does not exist."

    if not target.is_file():
        return f"Error: {path} is not a file."

    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Error: {path} is not a UTF-8 text file."


def write_file(path: str, content: str) -> str:
    target = safe_path(path)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return f"Successfully wrote {path}"


def edit_file(path: str, old: str, new: str) -> str:
    target = safe_path(path)

    if not target.exists():
        return f"Error: {path} does not exist."

    content = target.read_text(encoding="utf-8")

    occurrences = content.count(old)

    if occurrences == 0:
        return "Error: target text was not found."

    if occurrences > 1:
        return (
            f"Error: target text appears {occurrences} times. "
            "Provide a more specific target."
        )

    updated = content.replace(old, new)

    target.write_text(updated, encoding="utf-8")

    return f"Successfully edited {path}"

def run_command(command: str, timeout: int = 30) -> str:
    allowed, reason = validate_command(command)

    if not allowed:
        return f"BLOCKED: {reason}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = [
            f"Exit code: {result.returncode}"
        ]

        if result.stdout:
            output.append(f"\nSTDOUT:\n{result.stdout}")

        if result.stderr:
            output.append(f"\nSTDERR:\n{result.stderr}")

        return "\n".join(output)

    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout} seconds."

    except Exception as e:
        return f"Error running command: {e}"