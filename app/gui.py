from __future__ import annotations

import os
import threading
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QLabel, QListWidget, QMainWindow,
    QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWidget
)

from app.discovery import DiscoveryService, Peer
from app.main import send_file, start_receiver

PORT = 8765


class DropArea(QListWidget):
    files_dropped = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(220)
        self.addItem("Drag & drop files here")

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        paths = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile()
        ]
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()


class MainWindow(QMainWindow):
    peer_found = Signal(str, str, int)
    progress_changed = Signal(int)
    status_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DirectDrop")
        self.resize(720, 520)

        self.peer_host = os.getenv("DIRECTDROP_PEER_IP", "")
        self.peer_port = int(os.getenv("DIRECTDROP_PEER_PORT", str(PORT)))
        self.discovery: DiscoveryService | None = None
        self.receiver = None

        self.receive_dir = Path.home() / "DirectDrop" / "Received"
        self.receive_dir.mkdir(parents=True, exist_ok=True)

        root = QWidget()
        layout = QVBoxLayout(root)

        title = QLabel("DirectDrop")
        title.setStyleSheet("font-size: 30px; font-weight: 700;")
        layout.addWidget(title)

        self.connection = QLabel("Waiting for another DirectDrop laptop…")
        self.connection.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.connection)

        self.drop = DropArea()
        self.drop.files_dropped.connect(self.send_paths)
        layout.addWidget(self.drop)

        self.choose = QPushButton("Choose Files")
        self.choose.clicked.connect(self.choose_files)
        layout.addWidget(self.choose)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.status = QLabel("Files received here: " + str(self.receive_dir))
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.peer_found.connect(self.on_peer_found)
        self.progress_changed.connect(self.progress.setValue)
        self.status_changed.connect(self.status.setText)

        self.setCentralWidget(root)
        self.start_local_receiver()
        self.start_discovery()

        if self.peer_host:
            self.on_peer_found("Peer", self.peer_host, self.peer_port)

    def start_local_receiver(self) -> None:
        try:
            self.receiver = start_receiver("0.0.0.0", PORT, self.receive_dir)
        except OSError:
            # The background agent may already own the port.
            self.receiver = None

    def start_discovery(self) -> None:
        self.discovery = DiscoveryService(on_peer=self._peer_callback)
        self.discovery.start()

    def _peer_callback(self, peer: Peer) -> None:
        self.peer_found.emit(peer.name, peer.host, peer.port)

    def on_peer_found(self, name: str, host: str, port: int) -> None:
        self.peer_host = host
        self.peer_port = port
        self.connection.setText(f"🟢 Connected: {name} ({host})")

    def choose_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Select files")
        self.send_paths(files)

    def send_paths(self, paths: list[str]) -> None:
        if not self.peer_host:
            QMessageBox.information(
                self,
                "No laptop connected",
                "Connect the other DirectDrop laptop first.",
            )
            return

        for raw in paths:
            path = Path(raw)
            if path.is_file():
                threading.Thread(
                    target=self._send_one,
                    args=(path,),
                    daemon=True,
                ).start()

    def _send_one(self, path: Path) -> None:
        try:
            self.status_changed.emit(f"Sending {path.name}…")
            send_file(
                self.peer_host,
                self.peer_port,
                path,
                progress=lambda sent, total: self.progress_changed.emit(
                    int(sent * 100 / total) if total else 0
                ),
            )
            self.status_changed.emit(f"Sent: {path.name}")
        except Exception as exc:
            self.status_changed.emit(f"Transfer failed: {path.name} — {exc}")


def run() -> None:
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
