from __future__ import annotations

import json
import subprocess
import threading
from typing import Callable

USB_KEYWORDS = (
    "USB",
    "RNDIS",
    "REMOTE NDIS",
    "USB ETHERNET",
    "ETHERNET GADGET",
)

def usb_network_adapters() -> set[str]:
    command = [
        "powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
        "Get-CimInstance Win32_NetworkAdapter | "
        "Where-Object { $_.NetConnectionStatus -eq 2 } | "
        "Select-Object Name,NetConnectionID,PNPDeviceID | ConvertTo-Json -Compress"
    ]
    try:
        raw = subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL, timeout=5).strip()
    except (OSError, subprocess.SubprocessError):
        return set()
    if not raw:
        return set()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return set()
    if isinstance(data, dict):
        data = [data]
    result = set()
    for item in data:
        haystack = " ".join(str(item.get(k, "")) for k in ("Name", "NetConnectionID", "PNPDeviceID")).upper()
        if any(keyword in haystack for keyword in USB_KEYWORDS):
            result.add(haystack)
    return result

class UsbNetworkMonitor:
    def __init__(self, on_connected: Callable[[], None], interval: float = 1.5):
        self.on_connected = on_connected
        self.interval = interval
        self.stop_event = threading.Event()
        self.previous: set[str] | None = None

    def start(self) -> None:
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self) -> None:
        self.stop_event.set()

    def _loop(self) -> None:
        while not self.stop_event.is_set():
            current = usb_network_adapters()
            if self.previous is None:
                if current:
                    self.on_connected()
            elif current - self.previous:
                self.on_connected()
            self.previous = current
            self.stop_event.wait(self.interval)
