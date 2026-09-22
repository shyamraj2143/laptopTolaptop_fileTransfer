<div align="center">

# 🚀 DirectDrop

### 📦 One-click Windows EXE installer

<a href="https://github.com/shyamraj2143/laptopTolaptop_fileTransfer/releases/download/v0.2.0/DirectDrop-Setup.exe">
  <img src="https://img.shields.io/badge/DOWNLOAD%20%26%20INSTALL%20FOR%20WINDOWS-DirectDrop--Setup.exe-2ea44f?style=for-the-badge&logo=windows&logoColor=white" alt="Download and install DirectDrop for Windows">
</a>

<br><br>

**Click INSTALL → download `DirectDrop-Setup.exe` → open it → approve Windows permission → install. Repeat on BOTH laptops.**

</div>

---

# 🚀 DirectDrop — Install & Run

## ⭐ START HERE — Install on BOTH laptops

1. Open this repo.
2. Click **INSTALL FOR WINDOWS** above.
3. Open `DirectDrop-Setup.exe` when Windows finishes downloading it.
4. Approve the Windows permission prompt and complete the Setup wizard.
5. Repeat the installation on the second laptop.

After installation: connect the supported USB4 / USB-network cable, DirectDrop detects the link, the GUI opens, and files can be dragged across automatically.

> USB-C connector alone is not enough. The exact laptops, cable, USB controller and Windows driver stack must expose a supported USB networking interface.

## Features
- Drag and drop
- Automatic receiving
- SHA-256 integrity verification
- Background agent
- Automatic GUI launch
- Offline transfer over a supported local link
- No browser, cloud upload, or manual IP entry in the normal workflow

## Development (for contributors)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

Background agent:
```powershell
python run.py --agent
```

Received files are saved to:
`%USERPROFILE%\DirectDrop\Received`

## Status
Implemented: TCP transfer, automatic receiver, GUI, SHA-256 verification, peer discovery, USB-backed network-interface detection, background agent, automatic GUI launch, Windows installer/uninstaller, and Windows CI smoke tests.

Still required for production cable-only support: hardware/driver-specific USB4 validation, authenticated pairing, encrypted transport, pause/resume, folder queues, and a signed native Windows installer.