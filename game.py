
from PyQt5.QtWidgets import *
import os

class Game:
    def __init__(self, name, app_id, path, icon_path="",is_steam_game=True):
        self.name = name
        self.app_id = app_id
        self.path = path
        self.icon_path = icon_path
        self.is_steam_game = is_steam_game
        
    def to_dict(self):
        return {
            "name": self.name,
            "app_id": self.app_id,
            "path": self.path,
            "icon_path": self.icon_path,
            "is_steam_game": self.is_steam_game
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"], 
            data["app_id"], 
            data["path"], 
            data.get("icon_path", ""),
            data.get("is_steam_game", True)
        )


class GameDialog(QDialog):
    def __init__(self, accounts, parent=None, edit_mode=False, current_account_index=0, current_game=None):
        super().__init__(parent)
        self.setWindowTitle("Add Game" if not edit_mode else "Edit Game")
        self.setMinimumWidth(500)
        
        # Modern styling
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
        """)
        
        self.accounts = accounts
        self.edit_mode = edit_mode
        
        self.layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Game name")
        self.name_validation = QLabel()
        self.name_validation.setStyleSheet("color: red")
        
        self.steam_game_check = QCheckBox("Steam Game")
        self.steam_game_check.setChecked(True)
        self.steam_game_check.stateChanged.connect(self.toggle_steam_game_fields)
        
        self.app_id_edit = QLineEdit()
        self.app_id_edit.setPlaceholderText("Steam App ID (can be found on Steam store page)")
        self.app_id_validation = QLabel()
        self.app_id_validation.setStyleSheet("color: red")
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Path to game executable")
        self.path_validation = QLabel()
        self.path_validation.setStyleSheet("color: red")
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_for_game)
        
        self.account_combo = QComboBox()
        self.account_combo.setStyleSheet("""
            QComboBox {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 4px;
            padding: 5px;
            }
            QComboBox QAbstractItemView {
            background-color: #2c3e50;
            color: #ecf0f1;
            selection-background-color: #3498db;
            selection-color: white;
            }
        """)

        for account in self.accounts:
            self.account_combo.addItem(account.name)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_button)
        
        self.layout.addRow("Game Name:", self.name_edit)
        self.layout.addRow("", self.name_validation)
        self.layout.addRow("Steam Game:", self.steam_game_check)
        self.layout.addRow("Steam App ID:", self.app_id_edit)
        self.layout.addRow("", self.app_id_validation)
        self.layout.addRow("Executable Path:", path_layout)
        self.layout.addRow("", self.path_validation)
        self.layout.addRow("Steam Account:", self.account_combo)
        
        self.buttons_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.save_button = QPushButton("Save")
        
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.validate_and_accept)
        
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addWidget(self.save_button)
        
        self.layout.addRow("", self.buttons_layout)
        self.setLayout(self.layout)
        
        if edit_mode and current_game:
            self.name_edit.setText(current_game.name)
            self.app_id_edit.setText(current_game.app_id)
            self.path_edit.setText(current_game.path)
            self.account_combo.setCurrentIndex(current_account_index)
            self.steam_game_check.setChecked(current_game.is_steam_game)
        
        self.name_edit.textChanged.connect(self.validate_name)
        self.app_id_edit.textChanged.connect(self.validate_app_id)
        self.path_edit.textChanged.connect(self.validate_path)
        
        self.validate_name()
        self.validate_app_id()
        self.validate_path()
        self.toggle_steam_game_fields()
    
    def toggle_steam_game_fields(self):
        """Enable/disable Steam-specific fields based on the checkbox state."""
        is_steam_game = self.steam_game_check.isChecked()
        self.app_id_edit.setEnabled(is_steam_game)
        self.account_combo.setEnabled(is_steam_game)
        
        if not is_steam_game:
            self.app_id_validation.clear()
    
    def validate_name(self):
        """Validate game name"""
        name = self.name_edit.text().strip()
        
        if not name:
            self.name_validation.setText("Game name is required")
            self.save_button.setEnabled(False)
            return False
        
        if len(name) < 2:
            self.name_validation.setText("Game name must be at least 2 characters")
            self.save_button.setEnabled(False)
            return False
        
        self.name_validation.clear()
        self.update_save_button_state()
        return True
    
    def validate_app_id(self):
        """Validate Steam App ID"""
        if not self.steam_game_check.isChecked():
            return True
        
        app_id = self.app_id_edit.text().strip()
        
        if not app_id:
            self.app_id_validation.setText("Steam App ID is required")
            self.save_button.setEnabled(False)
            return False
        
        if not app_id.isdigit():
            self.app_id_validation.setText("App ID must be a numeric value")
            self.save_button.setEnabled(False)
            return False
        
        self.app_id_validation.clear()
        self.update_save_button_state()
        return True
    
    def validate_path(self):
        """Validate game executable path"""
        path = self.path_edit.text().strip()
        
        if not path:
            self.path_validation.setText("Game executable path is required")
            self.save_button.setEnabled(False)
            return False
        
        if not os.path.isfile(path):
            self.path_validation.setText("Invalid file path")
            self.save_button.setEnabled(False)
            return False
        
        if not path.lower().endswith(('.exe', '')):
            self.path_validation.setText("Path must point to an executable")
            self.save_button.setEnabled(False)
            return False
        
        self.path_validation.clear()
        self.update_save_button_state()
        return True
    
    def update_save_button_state(self):
        """Enable save button only if all validations pass"""
        is_valid = (
            self.is_name_valid() and 
            self.is_path_valid() and
            (not self.steam_game_check.isChecked() or self.is_app_id_valid())
        )
        self.save_button.setEnabled(is_valid)

    def is_name_valid(self):
        """Check if the game name is valid"""
        name = self.name_edit.text().strip()
        if not name or len(name) < 2:
            return False
        return True

    def is_app_id_valid(self):
        """Check if the Steam App ID is valid"""
        if not self.steam_game_check.isChecked():
            return True
        
        app_id = self.app_id_edit.text().strip()
        if not app_id or not app_id.isdigit():
            return False
        return True

    def is_path_valid(self):
        """Check if the game executable path is valid"""
        path = self.path_edit.text().strip()
        if not path or not os.path.isfile(path) or not path.lower().endswith(('.exe', '')):
            return False
        return True
    
    def browse_for_game(self):
        """Open file dialog to select game executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Game Executable", 
            "", 
            "Executables (*.exe);;All Files (*)"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
            
            if not self.edit_mode:
                game_name = os.path.splitext(os.path.basename(file_path))[0]
                if game_name and not self.name_edit.text():
                    self.name_edit.setText(game_name)
            
            self.validate_path()
    
    def validate_and_accept(self):
        """Final validation before accepting dialog"""
        if (self.validate_name() and 
            self.validate_path() and
            (not self.steam_game_check.isChecked() or self.validate_app_id())):
            self.accept()
    
    def get_game_data(self):
        """Retrieve validated game data"""
        return {
            "name": self.name_edit.text().strip(),
            "app_id": self.app_id_edit.text().strip() if self.steam_game_check.isChecked() else "",
            "path": self.path_edit.text().strip(),
            "account_index": self.account_combo.currentIndex() if self.steam_game_check.isChecked() else -1,
            "is_steam_game": self.steam_game_check.isChecked()
        }
