import winreg
import os
import subprocess
import time
from PyQt5.QtCore import *

from encryption import EncryptionHandler

class StartupManager:
    @staticmethod
    def is_startup_enabled():
        """Check if the application is set to run at startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                0, 
                winreg.KEY_READ
            )
            winreg.QueryValueEx(key, "MultiSteamLauncher")
            return True
        except FileNotFoundError:
            return False
        except WindowsError:
            return False

    @staticmethod
    def enable_startup(app_path):
        """Add application to startup registry"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                0, 
                winreg.KEY_ALL_ACCESS
            )
            winreg.SetValueEx(key, "Game Vault", 0, winreg.REG_SZ, f'"{app_path}"')
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error enabling startup: {e}")
            return False

    @staticmethod
    def disable_startup():
        """Remove application from startup registry"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                0, 
                winreg.KEY_ALL_ACCESS
            )
            winreg.DeleteValue(key, "Game Vault")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return True
        except Exception as e:
            print(f"Error disabling startup: {e}")
            return False

class SteamLoginThread(QThread):
    login_finished = pyqtSignal(bool)
    login_progress = pyqtSignal(str)
    
    def __init__(self, steam_path, username, password=None):
        super().__init__()
        self.steam_path = steam_path
        self.username = username
        self.password = password
        
    def run(self):
        self.login_progress.emit("Closing any running Steam instances...")
        try:
            if os.name == 'nt':  # Windows
                subprocess.call("taskkill /F /IM steam.exe", shell=True)
            else:  # Linux/Mac
                subprocess.call("pkill -f steam", shell=True)
        except:
            pass
        
        time.sleep(1)
        
        self.login_progress.emit("Launching Steam with account credentials...")
        
        if self.password:
            self.create_auto_login_file(self.username, self.password)
            cmd = f'"{self.steam_path}" -login {self.username} {self.password}'
        else:
            cmd = f'"{self.steam_path}" -login {self.username}'
            
        proc = subprocess.Popen(cmd, shell=True)
        
        for i in range(5):
            self.login_progress.emit(f"Logging in... ({i+1}/5)")
            time.sleep(1)
            
        self.login_progress.emit("Verifying login...")
        success = self.is_steam_running()
        
        self.login_finished.emit(success)
    
    def create_auto_login_file(self, username, password):
        self.login_progress.emit("Creating auto-login file...")
        enc = EncryptionHandler()
        encrypted_username = enc.encrypt(username)
        encrypted_password = enc.encrypt(password)

        auto_login_path = os.path.join(os.getenv('TEMP'), 'steam_auto_login.enc')
        try:
            with open(auto_login_path, 'w') as f:
                f.write(f"{encrypted_username}\n{encrypted_password}\n")
            self.login_progress.emit(f"Auto-login credentials securely stored at {auto_login_path}")
        except Exception as e:
            self.login_progress.emit(f"Failed to store auto-login credentials: {e}")

    
    def is_steam_running(self):
        try:
            if os.name == 'nt':  # Windows
                output = subprocess.check_output("tasklist | findstr steam.exe", shell=True)
                return b"steam.exe" in output
            else:  # Linux/Mac
                output = subprocess.check_output("ps aux | grep -v grep | grep steam", shell=True)
                return len(output) > 0
        except:
            return False

class LaunchThread(QThread):
    launch_finished = pyqtSignal(bool)
    launch_progress = pyqtSignal(str)
    
    def __init__(self, steam_path, username, password=None, app_id=None):
        super().__init__()
        self.steam_path = steam_path
        self.username = username
        self.password = password
        self.app_id = app_id
        
    def run(self):
        self.login_thread = SteamLoginThread(self.steam_path, self.username, self.password)
        self.login_thread.login_progress.connect(self.relay_progress)
        self.login_thread.start()
        self.login_thread.wait()
        
        if self.app_id:
            self.launch_progress.emit(f"Launching game (App ID: {self.app_id})...")
            
            cmd = f'"{self.steam_path}" -applaunch {self.app_id}'
            subprocess.Popen(cmd, shell=True)
            
            time.sleep(2)
            
        self.launch_finished.emit(True)
    
    def relay_progress(self, msg):
        self.launch_progress.emit(msg)
