"""Shell command execution utilities"""

import subprocess
from typing import List, Optional
from cloudsoc.utils.logger import logger


class ShellCommandError(Exception):
    """Raised when a shell command fails"""
    pass


def run_command(
    cmd: List[str],
    cwd: Optional[str] = None,
    check: bool = True,
    capture_output: bool = False
) -> subprocess.CompletedProcess:
    """
    Execute a shell command safely.

    Args:
        cmd: List of command and arguments
        cwd: Working directory for the command
        check: Raise exception on non-zero exit (default: True)
        capture_output: Capture stdout/stderr (default: False)

    Returns:
        CompletedProcess instance

    Raises:
        ShellCommandError: If command fails and check=True
    """
    logger.debug(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=False,
            capture_output=capture_output,
            text=capture_output
        )

        if check and result.returncode != 0:
            error_msg = f"Command failed with exit code {result.returncode}"
            if result.stderr:
                error_msg += f"\nStderr: {result.stderr}"
            raise ShellCommandError(error_msg)

        return result

    except FileNotFoundError as e:
        raise ShellCommandError(f"Command not found: {cmd[0]}") from e
    except Exception as e:
        raise ShellCommandError(f"Error running command: {str(e)}") from e
