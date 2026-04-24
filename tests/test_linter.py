import os
import subprocess
import typing

import pytest


class RuffLinter:
    CMD: typing.ClassVar[list[str]] = []

    def find_cwd(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get_bin(self) -> None:
        if not typing.TYPE_CHECKING:
            ruff = pytest.importorskip(
                "ruff", reason="No ruff linter avalible"
            )
        else:  # pragma: no branch
            import ruff
        return ruff.find_ruff_bin()

    def run_cmd(self) -> None:
        try:
            subprocess.run(
                [self.get_bin()] + self.CMD,
                check=True,
                capture_output=True,
                cwd=self.find_cwd(),
            )
        except subprocess.CalledProcessError as ex:
            output = ex.stdout.decode()
            output += "\n"
            output += ex.stderr.decode()
            raise AssertionError(
                f"ruff validation failed: {ex}\n{output}"
            ) from None

    def test_source_code(self) -> None:
        self.run_cmd()


class TestFormatting(RuffLinter):
    CMD = ["format", "--check", "--diff"]


class TestSouceCode(RuffLinter):
    CMD = ["check"]
