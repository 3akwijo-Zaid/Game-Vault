
from config import *

import base64
import hashlib
import os
import shutil
import time
import uuid

from cryptography.fernet import Fernet

class EncryptionHandler:
    def __init__(self):
        self.key = self._load_or_create_key()
        if self.key:
            self.cipher = Fernet(self.key)
        else:
            self.cipher = None
            
    def _load_or_create_key(self):
        key_file = ENCRYPTION_KEY_PATH
        
        try:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    key_data = f.read()
                
                if self._is_valid_key(key_data):
                    return key_data
                else:
                    self._backup_invalid_key(key_file)
            
            return self._generate_new_key(key_file)
            
        except Exception as e:
            print(f"Error handling encryption key: {str(e)}")
            return self._generate_fallback_key()
    
    def _is_valid_key(self, key_data):
        """Validate that the key is correctly formatted for Fernet"""
        try:
            if len(key_data) != 44:
                return False
                
            Fernet(key_data)
            return True
        except:
            return False
    
    def _backup_invalid_key(self, key_file):
        """Backup invalid key file before replacing it"""
        try:
            backup_file = f"{key_file}.invalid-{int(time.time())}"
            shutil.copy2(key_file, backup_file)
        except:
            pass
    
    def _generate_new_key(self, key_file):
        """Generate a cryptographically secure key and save it"""
        try:
            key = Fernet.generate_key()
            
            with open(key_file, 'wb') as f:
                f.write(key)
            
            if os.name != 'nt':
                os.chmod(key_file, 0o600)
                
            return key
            
        except Exception as e:
            print(f"Failed to generate/save secure key: {str(e)}")
            return None
    
    def _generate_fallback_key(self):
        """Generate a key based on machine ID as fallback"""
        try:
            machine_id = self._get_machine_id()
            
            key_material = hashlib.pbkdf2_hmac(
                'sha256', 
                machine_id.encode(), 
                b'MultiSteamLauncher', 
                100000
            )
            
            key = base64.urlsafe_b64encode(key_material)
            return key
            
        except:
            return Fernet.generate_key()
    
    def _get_machine_id(self):
        """Get a unique identifier for this machine"""
        try:
            if os.name == 'nt':  # Windows
                import subprocess
                result = subprocess.check_output('wmic csproduct get uuid').decode()
                return result.split('\n')[1].strip()
            else:  # Linux/Mac
                for path in ['/etc/machine-id', '/var/lib/dbus/machine-id']:
                    if os.path.exists(path):
                        with open(path, 'r') as f:
                            return f.read().strip()
                            
                mac = uuid.getnode()
                return str(mac)
        except:
            return f"msl-{int(time.time())}-{os.getpid()}"
    
    def encrypt(self, data):
        if not data:
            return ""
        if not self.cipher:
            return self._fallback_encrypt(data)
            
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            return self._fallback_encrypt(data)
    
    def decrypt(self, encrypted_data):
        if not encrypted_data:
            return ""
        if not self.cipher:
            return self._fallback_decrypt(encrypted_data)
            
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return self._fallback_decrypt(encrypted_data)
    
    def _fallback_encrypt(self, data):
        """Simple obfuscation as fallback (not secure, but better than plaintext)"""
        try:
            key = "MultiSteamLauncher"
            s = list(data)
            for i, char in enumerate(s):
                s[i] = chr(ord(char) ^ ord(key[i % len(key)]))
            return base64.b64encode(''.join(s).encode()).decode()
        except:
            return ""
    
    def _fallback_decrypt(self, encrypted_data):
        """Fallback decryption for the simple obfuscation"""
        try:
            key = "MultiSteamLauncher"
            s = base64.b64decode(encrypted_data.encode()).decode()
            result = []
            for i, char in enumerate(s):
                result.append(chr(ord(char) ^ ord(key[i % len(key)])))
            return ''.join(result)
        except:
            return ""
