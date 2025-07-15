"""Simple sandbox for executing Python code with tracing."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from opentelemetry import trace


def run_python(code: str, timeout: int = 30) -> str:
    """Run a Python code snippet in an isolated temp directory.

    The code is executed in a separate process so that any installed packages
    or side effects do not leak into the main application. All output is
    returned as a string. Execution time is limited by ``timeout`` seconds.
    """

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("sandbox.run_python") as span:
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = Path(tmpdir) / "snippet.py"
            script_path.write_text(code)

            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            span.set_attribute("exit_code", result.returncode)
            if result.stderr:
                span.set_attribute("stderr", result.stderr.strip())

            return result.stdout + result.stderr
