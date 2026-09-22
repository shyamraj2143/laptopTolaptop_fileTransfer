from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

APP_NAME = "DirectDrop"
INSTALL_DIR = Path.home() / "AppData" / "Local" / APP_NAME
TASK_NAME = "DirectDrop Background Agent"


def payload_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "payload"  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent / "payload"


def powershell(command: str) -> None:
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or "Windows operation failed."
        )


def register_agent(agent_exe: Path) -> None:
    task_name = TASK_NAME.replace("'", "''")
    exe = str(agent_exe).replace("'", "''")

    command = (
        "$action = New-ScheduledTaskAction "
        f"-Execute '{exe}'; "
        "$trigger = New-ScheduledTaskTrigger -AtLogOn "
        "-User $env:USERNAME; "
        "$principal = New-ScheduledTaskPrincipal "
        "-UserId $env:USERNAME -LogonType Interactive "
        "-RunLevel Limited; "
        f"Register-ScheduledTask -TaskName '{task_name}' "
        "-Action $action -Trigger $trigger -Principal $principal "
        "-Description 'DirectDrop background file transfer agent' "
        "-Force | Out-Null"
    )
    powershell(command)


def add_firewall_rules() -> None:
    rules = [
        ("DirectDrop TCP 8765", "TCP", "8765"),
        ("DirectDrop UDP 8766", "UDP", "8766"),
    ]

    for name, protocol, port in rules:
        subprocess.run(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                f"name={name}",
                "dir=in",
                "action=allow",
                f"protocol={protocol}",
                f"localport={port}",
                "profile=private",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )


def install() -> None:
    source = payload_dir()
    gui_exe = source / "DirectDrop.exe"
    agent_exe = source / "DirectDropAgent.exe"

    if not gui_exe.exists() or not agent_exe.exists():
        raise FileNotFoundError("Installer payload is incomplete.")

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    # Copy to a temporary file first so a previous running install
    # cannot leave a half-written executable behind.
    for file in (gui_exe, agent_exe):
        destination = INSTALL_DIR / file.name
        with tempfile.NamedTemporaryFile(
            prefix=file.stem + "_",
            suffix=".tmp",
            dir=INSTALL_DIR,
            delete=False,
        ) as temp:
            temp_path = Path(temp.name)

        try:
            shutil.copy2(file, temp_path)
            temp_path.replace(destination)
        finally:
            temp_path.unlink(missing_ok=True)

    register_agent(INSTALL_DIR / "DirectDropAgent.exe")
    add_firewall_rules()

    subprocess.Popen(
        [str(INSTALL_DIR / "DirectDropAgent.exe")],
        cwd=str(INSTALL_DIR),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        install()
    except Exception as exc:
        messagebox.showerror(
            APP_NAME,
            "Installation failed.\n\n" + str(exc),
            parent=root,
        )
        raise SystemExit(1)

    messagebox.showinfo(
        APP_NAME,
        "DirectDrop installed successfully.\n\n"
        "Install it on BOTH laptops.\n"
        "The background agent is now running.",
        parent=root,
    )


if __name__ == "__main__":
    main()
