# DirectDrop

DirectDrop is a Windows-first laptop-to-laptop file transfer application designed for a zero-configuration user experience.

Target experience:
Install DirectDrop once on both laptops.
Connect the supported USB-C network link -> the background agent runs -> the link is detected -> the GUI opens -> drag a file -> the other laptop saves it automatically.

No browser, cloud upload, manual download, or terminal is needed during normal use.

Architecture:
Windows -> DirectDrop background agent -> USB-network detection + peer discovery + receiver -> DirectDrop GUI -> TCP file transfer.

USB-C limitation:
USB-C is a connector standard, not a guarantee that two laptops become a network.
For cable-only operation, the exact laptop hardware, USB controller, cable and Windows driver stack must expose a usable USB networking interface.
This project does not fake USB support. It detects a real USB-backed network adapter and uses TCP/IP over that link.

Windows installation:
Run PowerShell in the repository directory and execute:
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1

The installer copies the app to %LOCALAPPDATA%\DirectDrop, creates a virtual environment, installs dependencies, registers a Windows logon task, and starts the background agent.

Receiving location:
%USERPROFILE%\DirectDrop\Received

Implemented:
- TCP file transfer
- automatic receiver
- drag-and-drop GUI
- SHA-256 integrity verification
- UDP peer discovery
- USB-backed network interface detection
- background agent
- automatic GUI launch
- Windows installer and uninstaller

Next production work:
- hardware/driver-specific USB networking integration
- authenticated pairing
- encrypted transport
- pause/resume and recovery
- folder transfer queues
- signed native Windows installer
- robust selection when multiple DirectDrop peers exist

Project goal:
install once -> connect cable -> GUI appears -> drag -> done.