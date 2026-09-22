from __future__ import annotations
import hashlib, json, socket, struct, threading, uuid
from pathlib import Path
from typing import Callable

MAGIC = b"DROP1"
HEADER = struct.Struct("!5sBQ")

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def _read_exact(sock: socket.socket, n: int) -> bytes:
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data.extend(chunk)
    return bytes(data)

def _unique(path: Path) -> Path:
    if not path.exists():
        return path
    for i in range(1, 10000):
        candidate = path.with_name(f"{path.stem} ({i}){path.suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError("No free destination name")

def send_file(host: str, port: int, path: Path, progress: Callable[[int,int],None] | None = None) -> None:
    size = path.stat().st_size
    meta = {"type":"file","name":path.name,"size":size,"sha256":sha256_file(path),"transfer_id":str(uuid.uuid4())}
    payload = json.dumps(meta).encode("utf-8")
    with socket.create_connection((host, port), timeout=15) as sock:
        sock.sendall(HEADER.pack(MAGIC, 1, len(payload)))
        sock.sendall(payload)
        sent = 0
        with path.open("rb") as f:
            while sent < size:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                sock.sendall(chunk)
                sent += len(chunk)
                if progress:
                    progress(sent, size)

def start_receiver(bind_host: str, port: int, receive_dir: Path,
                   on_progress: Callable[[str,int,int],None] | None = None,
                   on_complete: Callable[[Path],None] | None = None) -> socket.socket:
    receive_dir.mkdir(parents=True, exist_ok=True)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((bind_host, port))
    server.listen(8)
    server.settimeout(1.0)

    def handle(conn: socket.socket) -> None:
        tmp: Path | None = None
        try:
            magic, version, length = HEADER.unpack(_read_exact(conn, HEADER.size))
            if magic != MAGIC or version != 1:
                raise ValueError("Unsupported protocol")
            meta = json.loads(_read_exact(conn, length).decode("utf-8"))
            name = Path(str(meta["name"])).name
            size = int(meta["size"])
            expected = str(meta["sha256"])
            tmp = receive_dir / f".{uuid.uuid4().hex}.part"
            final = _unique(receive_dir / name)
            digest = hashlib.sha256()
            received = 0
            with tmp.open("wb") as f:
                while received < size:
                    chunk = conn.recv(min(1024 * 1024, size - received))
                    if not chunk:
                        raise ConnectionError("Connection closed before completion")
                    f.write(chunk)
                    digest.update(chunk)
                    received += len(chunk)
                    if on_progress:
                        on_progress(name, received, size)
            if digest.hexdigest() != expected:
                raise ValueError("SHA-256 verification failed")
            tmp.replace(final)
            if on_complete:
                on_complete(final)
        finally:
            if tmp and tmp.exists():
                tmp.unlink(missing_ok=True)
            conn.close()

    def serve() -> None:
        with server:
            while True:
                try:
                    conn, _ = server.accept()
                except socket.timeout:
                    continue
                threading.Thread(target=handle, args=(conn,), daemon=True).start()

    threading.Thread(target=serve, daemon=True).start()
    return server
