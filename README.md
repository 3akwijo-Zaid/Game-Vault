# Game Vault

Game Vault is a modern, modular application for managing and launching multiple Steam accounts and their games from a single interface. Built with PyQt5, it features a clean UI, account/game management, encryption, and Windows startup integration.

---

## Features

- Manage multiple Steam accounts with secure credential storage
- Add, edit, and launch games for each account
- Modern, dark-themed PyQt5 interface
- Search and sort accounts/games
- Windows startup integration (optional)
- Encrypted configuration and account data

---

## Project Structure

```
Game_Vault/
├── __init__.py
├── account.py         # Account-related logic and dialogs
├── config.py          # Configuration file paths
├── encryption.py      # Encryption handler
├── game.py            # Game-related logic and dialogs
├── launcher.py        # Threads and startup logic
├── main.py            # Entry point
├── ui.py              # Custom UI elements
├── icon.png           # Application icon
├── requirements.txt   # All dependencies
├── Game_Vault.exe     # Prebuilt Windows executable
└── _internal/         # Internal modules (if any)
```

---

## Installation


1. **Install all dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```

   Or, to install manually:
   ```powershell
   pip install PyQt5 cryptography psutil pypiwin32
   ```

2. **Use the provided executable (Windows only):**

   You can simply run the included **Game_Vault.exe** in the project root to start the application without building anything.  
   **Note:** The provided executable is for Windows. If you're using Linux or macOS, please run from source or build your own executable for your OS.

---

## How to Run


To run the application, you have two options:

**1. Run from source:**
```powershell
python -m main
```

**2. Use the provided executable:**
```powershell
./Game_Vault.exe
```

---

## Usage Notes

- The app icon (`icon.png`) should be present in the root directory for best appearance.
- On first run, you may need to set your Steam installation path.
- Windows startup integration can be toggled in the app settings.
- All account data is encrypted using the `cryptography` library.

---

## Troubleshooting

- If you see errors about missing DLLs or modules, ensure all dependencies are installed and you are using a supported version of Python (3.8+ recommended).
- For Windows startup integration, you may need to run as administrator.
- If you encounter issues with the UI, try updating PyQt5.

---

## License

No license specified. All rights reserved.

---

## Credits

Developed by Amirache Zaid.

## Description

This project is structured to keep all components modular:
- `account.py`: Account-related logic and dialogs.
- `launcher.py`: Threads and startup logic.
- `game.py`: Game-related logic and dialogs.
- `ui.py`: Custom UI elements.
- `encryption.py`: Encryption handler.
- `config.py`: Configuration file paths.
- `main.py`: Entry point.
