from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path

from app.discovery import DiscoveryService, Peer
from app.main import start_receiver

PORT = 8765

class DirectDropAgent:
    def __init__(self) -> None:
        self.receive_dir = Path.home() / "DirectDrop" / "Received"
        self.receive_dir.mkdir(parents=True, exist_ok=True)
        self.gui_open = False

    def run(self) -> None:
        start_receiver("0.0.0.0", PORT, self.receive_dir)
        discovery = DiscoveryService(on_peer=self.peer_found)
        discovery.start()
        try:
            threading.Event().wait()
        finally:
            discovery.stop()

    def peer_found(self, peer: Peer) -> None:
        if self.gui_open:
            return
        self.gui_open = True

        root = Path(__file__).resolve().parent.parent
        run_py = root / "run.py"

        env = os.environ.copy()
        env["DIRECTDROP_PEER_IP"] = peer.host
        env["DIRECTDROP_PEER_PORT"] = str(peer.port)

        try:
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.Popen(
                [sys.executable, str(run_py), "--gui"],
                cwd=str(root),
                env=env,
                creationflags=flags,
            )
        except OSError:
            self.gui_open = False

def run_agent() -> None:
    DirectDropAgent().run()
