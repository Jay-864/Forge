import shlex


BLOCKED_COMMANDS = {
    "rm",
    "rmdir",
    "del",
    "format",
    "shutdown",
    "reboot",
}


def validate_command(command: str) -> tuple[bool, str]:
    try:
        parts = shlex.split(command)
    except ValueError as e:
        return False, f"Invalid command: {e}"

    if not parts:
        return False, "Empty command."

    executable = parts[0].lower()

    if executable in BLOCKED_COMMANDS:
        return False, f"Command '{executable}' is blocked."

    return True, ""