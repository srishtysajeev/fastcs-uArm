import subprocess
import sys

from fastcs_uArm import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "fastcs_uArm", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
