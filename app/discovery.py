from __future__ import annotations
import json
import socket
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Callable

DISCOVERY_PORT = 8766

@dataclass(frozen=True)
class Peer:
    device_id: str
    name: str
    host: str
    port: int

class DiscoveryService:
    def __init__(self, port: int = DISCOVERY_PORT,
                 on_peer: Callable[[Peer], None] | None = None,
                 name: str | None = None):
        self.port = port
        self.on_peer = on_peer or (lambda peer: None)
        self.name = name or socket.gethostname()
        self.device_id = str(uuid.uuid4())
        self.stop_event = threading.Event()
        self.seen: dict[str, float] = {}

    def start(self) -> None:
        threading.Thread(target=self._listen, daemon=True).start()
        threading.Thread(target=self._announce, daemon=True).start()

    def stop(self) -> None:
        self.stop_event.set()

    def _listen(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("", self.port))
            sock.settimeout(1)
        except OSError:
            sock.close()
            return
        with sock:
            while not self.stop_event.is_set():
                try:
                    data, address = sock.recvfrom(4096)
                    msg = json.loads(data.decode("utf-8"))
                except (socket.timeout, OSError, ValueError, UnicodeDecodeError):
                    continue
                if msg.get("magic") != "DIRECTDROP_V1":
                    continue
                if msg.get("device_id") == self.device_id:
                    continue
                peer = Peer(
                    device_id=str(msg["device_id"]),
                    name=str(msg.get("name") or address[0]),
                    host=address[0],
                    port=int(msg.get("port", 8765)),
                )
                now = time.monotonic()
                if now - self.seen.get(peer.device_id, 0) >= 3:
                    self.seen[peer.device_id] = now
                    self.on_peer(peer)

    def _announce(self) -> None:
        message = json.dumps({
            "magic": "DIRECTDROP_V1",
            "device_id": self.device_id,
            "name": self.name,
            "port": 8765,
        }).encode("utf-8")
        while not self.stop_event.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.sendto(message, ("255.255.255.255", self.port))
                sock.close()
            except OSError:
                pass
            self.stop_event.wait(2)
