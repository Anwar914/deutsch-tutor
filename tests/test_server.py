"""Start the real server on a temporary local port and verify its health endpoint."""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def test_server_starts(tmp_path):
    """Keep the smoke server private and always terminate it after the check."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = {**os.environ, "TUTOR_DB_PATH": str(tmp_path / "smoke.sqlite3")}
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.address=127.0.0.1",
            f"--server.port={port}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ],
        cwd=Path(__file__).resolve().parent.parent,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            assert process.poll() is None, "Streamlit exited before becoming healthy"
            try:
                with urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1) as response:
                    assert response.status == 200
                    assert response.read() == b"ok"
                    return
            except URLError:
                time.sleep(0.2)
        raise AssertionError("Streamlit did not become healthy")
    finally:
        process.terminate()
        process.wait(timeout=10)
