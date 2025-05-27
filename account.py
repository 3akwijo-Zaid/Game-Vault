
from game import Game
from ui import ModernStyledButton

from PyQt5.QtWidgets import *

class SteamAccount:
    def __init__(self, name, username, password="", password_hint="", auto_login=False):
        self.name = name
        self.username = username
        self.password = password
        self.password_hint = password_hint
        self.auto_login = auto_login
        self.games = []
        
    def to_dict(self, encryption_handler):
        return {
            "name": self.name,
            "username": self.username,
            "password": encryption_handler.encrypt(self.password) if self.password else "",
            "password_hint": self.password_hint,
            "auto_login": self.auto_login,
            "games": [game.to_dict() for game in self.games]
        }
    
    @classmethod
    def from_dict(cls, data, encryption_handler):
        encrypted_password = data.get("password", "")
        password = encryption_handler.decrypt(encrypted_password) if encrypted_password else ""
        
        account = cls(
            data["name"], 
            data["username"], 
            password,
            data.get("password_hint", ""),
            data.get("auto_login", False)
        )
        
        for game_data in data.get("games", []):
            account.games.append(Game.from_dict(game_data))
        return account


class AddAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Steam Account")
        self.setMinimumWidth(400)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2634;
            }
            QLabel {
                color: #ecf0f1;
            }
            QLineEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 5px;
            }
            QCheckBox {
                color: #ecf0f1;
            }
        """)
        
        self.layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_hint_edit = QLineEdit()
        self.auto_login_check = QCheckBox("Enable auto-login (saves password)")
        
        self.layout.addRow("Display Name:", self.name_edit)
        self.layout.addRow("Steam Username:", self.username_edit)
        self.layout.addRow("Password (optional):", self.password_edit)
        self.layout.addRow("Password Hint:", self.password_hint_edit)
        self.layout.addRow("", self.auto_login_check)
        
        self.auto_login_check.toggled.connect(self.toggle_password_required)
        
        self.buttons_layout = QHBoxLayout()
        self.cancel_button = ModernStyledButton("Cancel")
        self.save_button = ModernStyledButton("Save")
        
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.accept)
        
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addWidget(self.save_button)
        
        self.layout.addRow("", self.buttons_layout)
        self.setLayout(self.layout)
    
    def toggle_password_required(self, checked):
        if checked and not self.password_edit.text():
            QMessageBox.information(self, "Password Required", 
                                 "<span style='color: black;'>Auto-login requires a password. Please enter your Steam password.</span>")
    
    def get_account_data(self):
        return {
            "name": self.name_edit.text(),
            "username": self.username_edit.text(),
            "password": self.password_edit.text(),
            "password_hint": self.password_hint_edit.text(),
            "auto_login": self.auto_login_check.isChecked()
        }
