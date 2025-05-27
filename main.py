
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
import json
import subprocess

from account import SteamAccount, AddAccountDialog
from launcher import StartupManager, LaunchThread
from game import Game, GameDialog
from ui import ModernStyledButton, ModernStyledListWidget
from encryption import EncryptionHandler
from config import CONFIG_PATH, ENCRYPTION_KEY_PATH

class MultiSteamLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icon.png")) 

        self.accounts = []
        self.steam_path = ""
        self.encryption_handler = EncryptionHandler()
        
        # Add modern styling to the main window
        self.setStyleSheet("""
            QMainWindow {
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
            QComboBox {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #34495e;
                border-left-style: solid;
            }
        """)
        
        self.init_ui()
        self.load_config()
    
    def init_ui(self):
        self.setWindowTitle("Game Vault")
        self.setMinimumSize(1000, 600)
        
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left side - Account list
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Add search box for accounts
        account_search_layout = QHBoxLayout()
        account_search_label = QLabel("Search:")
        self.account_search_edit = QLineEdit()
        self.account_search_edit.setPlaceholderText("Filter accounts...")
        self.account_search_edit.textChanged.connect(self.filter_accounts)
        account_search_layout.addWidget(account_search_label)
        account_search_layout.addWidget(self.account_search_edit)
        
        # Account list with sorting
        self.account_list = ModernStyledListWidget()
        self.account_list.setIconSize(QSize(32, 32))
        self.account_list.currentRowChanged.connect(self.account_selected)
        self.account_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.account_list.customContextMenuRequested.connect(self.show_account_context_menu)
        
        # Account sorting options
        account_sort_layout = QHBoxLayout()
        account_sort_label = QLabel("Sort by:")
        self.account_sort_combo = QComboBox()
        self.account_sort_combo.addItems(["Name", "Username", "Number of Games"])
        self.account_sort_combo.setStyleSheet("""
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
        self.account_sort_combo.currentIndexChanged.connect(self.sort_accounts)
        account_sort_layout.addWidget(account_sort_label)
        account_sort_layout.addWidget(self.account_sort_combo)
        
        account_header = QLabel("Steam Accounts")
        account_header.setFont(QFont("Arial", 14, QFont.Bold))
        
        account_buttons_layout = QHBoxLayout()
        add_account_button = ModernStyledButton("Add Account")
        add_account_button.setIcon(QIcon.fromTheme("list-add"))
        add_account_button.clicked.connect(self.add_account)
        
        edit_account_button = ModernStyledButton("Edit Account")
        edit_account_button.setIcon(QIcon.fromTheme("document-edit"))
        edit_account_button.clicked.connect(self.edit_account)
        
        account_buttons_layout.addWidget(add_account_button)
        account_buttons_layout.addWidget(edit_account_button)
        
        left_layout.addWidget(account_header)
        left_layout.addLayout(account_search_layout)
        left_layout.addWidget(self.account_list)
        left_layout.addLayout(account_sort_layout)
        left_layout.addLayout(account_buttons_layout)
        
        left_panel.setLayout(left_layout)
        
        # Right side - Game library
        right_panel = QWidget()
        right_layout = QVBoxLayout()
      
        # Add search box for games
        game_search_layout = QHBoxLayout()
        game_search_label = QLabel("Search:")
        self.game_search_edit = QLineEdit()
        self.game_search_edit.setPlaceholderText("Filter games...")
        self.game_search_edit.textChanged.connect(self.filter_games)
        game_search_layout.addWidget(game_search_label)
        game_search_layout.addWidget(self.game_search_edit)
        
        # Game list with sorting
        self.game_list = ModernStyledListWidget()
        self.game_list.setIconSize(QSize(64, 64))
        self.game_list.itemDoubleClicked.connect(self.launch_game)
        self.game_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.game_list.customContextMenuRequested.connect(self.show_game_context_menu)
        
        # Game sorting options
        game_sort_layout = QHBoxLayout()
        game_sort_label = QLabel("Sort by:")
        self.game_sort_combo = QComboBox()
        self.game_sort_combo.addItems(["Name", "App ID", "Account"])
        self.game_sort_combo.setStyleSheet("""
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
        self.game_sort_combo.currentIndexChanged.connect(self.sort_games)
        game_sort_layout.addWidget(game_sort_label)
        game_sort_layout.addWidget(self.game_sort_combo)
        
        
        games_header = QLabel("Game Library")
        games_header.setFont(QFont("Arial", 14, QFont.Bold))
        
        game_buttons_layout = QHBoxLayout()
        add_game_button = ModernStyledButton("Add Game")
        add_game_button.setIcon(QIcon.fromTheme("list-add"))
        add_game_button.clicked.connect(self.add_game)
        
        edit_game_button = ModernStyledButton("Edit Game")
        edit_game_button.setIcon(QIcon.fromTheme("document-edit"))
        edit_game_button.clicked.connect(self.edit_game)
        
        delete_game_button = ModernStyledButton("Delete Game")
        delete_game_button.setIcon(QIcon.fromTheme("edit-delete"))
        delete_game_button.clicked.connect(self.delete_game)
        
        launch_button = ModernStyledButton("Launch Game")
        launch_button.setIcon(QIcon.fromTheme("media-playback-start"))
        launch_button.clicked.connect(self.launch_selected_game)
        
        game_buttons_layout.addWidget(add_game_button)
        game_buttons_layout.addWidget(edit_game_button)
        game_buttons_layout.addWidget(delete_game_button)
        game_buttons_layout.addWidget(launch_button)
        
        right_layout.addWidget(games_header)
        right_layout.addLayout(game_search_layout)
        right_layout.addWidget(self.game_list)
        right_layout.addLayout(game_sort_layout)
        right_layout.addLayout(game_buttons_layout)
        
        settings_layout = QHBoxLayout()
        steam_path_button = ModernStyledButton("Set Steam Path")
        steam_path_button.setIcon(QIcon.fromTheme("document-open"))
        steam_path_button.clicked.connect(self.set_steam_path)
        
        settings_layout.addWidget(steam_path_button)
        
        right_layout.addLayout(settings_layout)
        
        right_panel.setLayout(right_layout)

        
        # Add "Show All Games" button
        self.show_all_games_button = ModernStyledButton("Show Selected Account Games")
        self.show_all_games_button.setCheckable(True)
        self.show_all_games_button.setChecked(True)
        self.show_all_games_button.clicked.connect(self.toggle_show_all_games)
    
        # Add the button to the game buttons layout
        game_buttons_layout.addWidget(self.show_all_games_button)

        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
          
        # Add Startup Preference to Right Content Layout
        startup_layout = QHBoxLayout()
        self.startup_checkbox = QCheckBox("Launch at Windows Startup")
        self.startup_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ecf0f1;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #34495e;
                border-radius: 4px;
                background-color: #2c3e50;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                image: url(:/checkbox-checked.png);
            }
        """)
        
        # Set initial startup checkbox state
        self.startup_checkbox.setChecked(StartupManager.is_startup_enabled())
        
        # Connect checkbox state change
        self.startup_checkbox.stateChanged.connect(self.toggle_startup)
        
        startup_layout.addWidget(self.startup_checkbox)
        right_layout.addLayout(startup_layout)
        
    def toggle_show_all_games(self):
        """Toggle between showing all games and games from the selected account."""
        if self.show_all_games_button.isChecked():
            self.show_all_games_button.setText("Show Selected Account Games")
        else:
            self.show_all_games_button.setText("Show All Games")

        # Update the game list based on the new state
        self.update_game_list()

    def toggle_startup(self, state):
        """Handle startup preference changes"""
        try:
            # Get the current executable path
            app_path = sys.executable
            
            if state == Qt.Checked:
                # Enable startup
                success = StartupManager.enable_startup(app_path)
                if success:
                    self.show_status("Application will now launch at startup")
                else:
                    QMessageBox.warning(
                        self, 
                        "Startup Error", 
                        "<span style='color: black;'>Could not add application to startup. Please check permissions.</span>"
                    )
                    self.startup_checkbox.setChecked(False)
            else:
                # Disable startup
                success = StartupManager.disable_startup()
                if success:
                    self.show_status("Application will not launch at startup")
                else:
                    QMessageBox.warning(
                        self, 
                        "Startup Error", 
                        "<span style='color: black;'>Could not remove application from startup. Please check permissions.</span>"
                    )
                    self.startup_checkbox.setChecked(True)
        
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Unexpected Error", 
                f"<span style='color: black;'>An error occurred: {str(e)}</span>"
            )
    
    def show_status(self, message, timeout=0):
        """Show a status message with a modern style"""
        status_bar = self.statusBar()
        status_bar.showMessage(message, timeout)
        status_bar.setStyleSheet("color: white;")

    def filter_accounts(self):
        """Filter accounts based on search text"""
        search_text = self.account_search_edit.text().lower()
        
        for i in range(self.account_list.count()):
            item = self.account_list.item(i)
            account = self.accounts[i]
            
            if (search_text in account.name.lower() or 
                search_text in account.username.lower()):
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def filter_games(self):
        """Filter games based on search text."""
        search_text = self.game_search_edit.text().lower()

        for i in range(self.game_list.count()):
            item = self.game_list.item(i)
            account, game = item.data(Qt.UserRole)

            if (search_text in game.name.lower() or 
                search_text in game.app_id.lower() or
                (self.show_all_games_button.isChecked() and search_text in account.name.lower())):
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def sort_accounts(self):
        """Sort accounts based on selected criteria"""
        current_index = self.account_sort_combo.currentIndex()
        
        if current_index == 0:  # Sort by Name
            self.accounts.sort(key=lambda x: x.name.lower())
        elif current_index == 1:  # Sort by Username
            self.accounts.sort(key=lambda x: x.username.lower())
        elif current_index == 2:  # Sort by Number of Games
            self.accounts.sort(key=lambda x: len(x.games), reverse=True)
            
        self.update_account_list()
        
    def sort_games(self):
        """Sort games in the game list based on selected criteria."""
        current_index = self.game_sort_combo.currentIndex()

        # Create a temporary list of (account, game) tuples for sorting
        game_data = []

        if self.show_all_games_button.isChecked():
            # All games view
            for account in self.accounts:
                for game in account.games:
                    game_data.append((account, game))
        else:
            # Single account view
            selected_account_index = self.account_list.currentRow()
            if selected_account_index >= 0 and selected_account_index < len(self.accounts):
                account = self.accounts[selected_account_index]
                game_data = [(account, game) for game in account.games]

        # Apply sorting
        if current_index == 0:  # Sort by Name
            game_data.sort(key=lambda x: x[1].name.lower())
        elif current_index == 1:  # Sort by App ID
            game_data.sort(key=lambda x: x[1].app_id)
        elif current_index == 2:  # Sort by Account
            game_data.sort(key=lambda x: x[0].name.lower())

        # Rebuild game list with sorted data
        self.game_list.clear()

        for account, game in game_data:
            item = QListWidgetItem(game.name)
            item.setData(Qt.UserRole, (account, game))
            auto_login = "Auto-login" if account.auto_login else "Manual login"
            item.setToolTip(f"App ID: {game.app_id}\nAccount: {account.username} ({auto_login})" if game.is_steam_game else "Non-Steam Game")

            self.game_list.addItem(item)

    def show_account_context_menu(self, position):
        index = self.account_list.currentRow()
        if index < 0:
            return
            
        menu = QMenu()
        edit_action = menu.addAction("Edit Account")
        delete_action = menu.addAction("Delete Account")
        
        action = menu.exec_(self.account_list.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_account()
        elif action == delete_action:
            self.delete_account()
    
    def show_game_context_menu(self, position):
        item = self.game_list.currentItem()
        if not item:
            return
            
        menu = QMenu()
        edit_action = menu.addAction("Edit Game")
        delete_action = menu.addAction("Delete Game")
        launch_action = menu.addAction("Launch Game")
        
        action = menu.exec_(self.game_list.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_game()
        elif action == delete_action:
            self.delete_game()
        elif action == launch_action:
            self.launch_game(item)
        
    def add_account(self):
        dialog = AddAccountDialog(self)
        if dialog.exec_():
            data = dialog.get_account_data()
            
            if not data["name"] or not data["username"]:
                QMessageBox.warning(self, "<span style='color: black;'>Input Error", "Account name and username are required.</span>")
                return
            
            # Confirm password storage if auto-login is enabled
            if data["auto_login"] and data["password"]:
                confirm = QMessageBox.question(
                    self, "Confirm Password Storage",
                    "<span style='color: black;'>Your password will be stored securely on this device. Continue?</span>",
                    QMessageBox.Yes | QMessageBox.No
                )
                if confirm != QMessageBox.Yes:
                    data["password"] = ""
                    data["auto_login"] = False
            
            # If auto-login is enabled but no password is provided
            if data["auto_login"] and not data["password"]:
                QMessageBox.warning(self, "Password Required", 
                                  "<span style='color: black;'>Auto-login requires a password. Disabling auto-login.</span>")
                data["auto_login"] = False
                
            account = SteamAccount(
                data["name"], 
                data["username"], 
                data["password"],
                data["password_hint"],
                data["auto_login"]
            )
            
            self.accounts.append(account)
            self.update_account_list()
            self.save_config()
    
    def edit_account(self):
        if not self.account_list.currentItem():
            QMessageBox.information(self, "No Selection", "<span style='color: black;'>Please select an account to edit.</span>")
            return
            
        index = self.account_list.currentRow()
        account = self.accounts[index]
        
        # Create a dialog pre-filled with account data
        dialog = AddAccountDialog(self)
        dialog.setWindowTitle("Edit Steam Account")
        dialog.name_edit.setText(account.name)
        dialog.username_edit.setText(account.username)
        dialog.password_edit.setText(account.password)
        dialog.password_hint_edit.setText(account.password_hint)
        dialog.auto_login_check.setChecked(account.auto_login)
        
        if dialog.exec_():
            data = dialog.get_account_data()
            
            # Password confirmation if changed with auto-login
            if data["auto_login"] and data["password"] != account.password:
                confirm = QMessageBox.question(
                    self, "Confirm Password Change",
                    "<span style='color: black;'>Your password will be updated and stored securely. Continue?</span>",
                    QMessageBox.Yes | QMessageBox.No
                )
                if confirm != QMessageBox.Yes:
                    data["password"] = account.password
            
            # Update account data
            account.name = data["name"]
            account.username = data["username"]
            account.password = data["password"]
            account.password_hint = data["password_hint"]
            account.auto_login = data["auto_login"]
            
            self.update_account_list()
            self.save_config()
    
    def delete_account(self):
        index = self.account_list.currentRow()
        if index < 0:
            return
            
        account = self.accounts[index]
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"<span style='color: black;'>Are you sure you want to delete the account '{account.name}'?\n\n</span>"
            f"<span style='color: black;'>This will also remove {len(account.games)} associated games.</span>",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.accounts.pop(index)
            self.update_account_list()
            self.update_game_list()
            self.save_config()
  
    def add_game(self):
        if not self.accounts:
            QMessageBox.warning(self, "<span style='color: black;'>No Accounts", "Please add at least one Steam account first.</span>")
            return

        dialog = GameDialog(self.accounts, self)
        if dialog.exec_():
            data = dialog.get_game_data()

            if not data["name"]:
                QMessageBox.warning(self, "Input Error", "<span style='color: black;'>Game name is required.</span>")
                return

            account = self.accounts[data["account_index"]] if data["is_steam_game"] else None
            game = Game(data["name"], data["app_id"], data["path"], is_steam_game=data["is_steam_game"])

            if data["is_steam_game"]:
                account.games.append(game)
            else:
                # Add non-Steam game to the first account (or create a new account for non-Steam games)
                if self.accounts:
                    self.accounts[0].games.append(game)
                else:
                    # Create a dummy account for non-Steam games
                    dummy_account = SteamAccount("Non-Steam Games", "non-steam")
                    dummy_account.games.append(game)
                    self.accounts.append(dummy_account)

            self.update_game_list()
            self.save_config()

    def edit_game(self):
        if not self.game_list.currentItem():
            QMessageBox.information(self, "<span style='color: black;'>No Selection", "Please select a game to edit.</span>")
            return
            
        item = self.game_list.currentItem()
        current_account, current_game = item.data(Qt.UserRole)
        
        # Find account index
        account_index = 0
        for i, account in enumerate(self.accounts):
            if account == current_account:
                account_index = i
                break
            
        # Create edit dialog
        dialog = GameDialog(
            self.accounts, 
            self, 
            edit_mode=True,
            current_account_index=account_index, 
            current_game=current_game
        )
        
        if dialog.exec_():
            data = dialog.get_game_data()
            
            if not data["name"]:
                QMessageBox.warning(self, "<span style='color: black;'>Input Error", "Game name is required.</span>")
                return
            
            # Update game data
            current_game.name = data["name"]
            current_game.app_id = data["app_id"]
            current_game.path = data["path"]
            current_game.is_steam_game = data["is_steam_game"]
            
            # Check if account changed (only for Steam games)
            if data["is_steam_game"]:
                new_account_index = data["account_index"]
                if new_account_index != account_index:
                    # Remove from old account
                    current_account.games.remove(current_game)
                    
                    # Add to new account
                    self.accounts[new_account_index].games.append(current_game)
            
            self.update_game_list()
            self.save_config()
    
    def delete_game(self):
        item = self.game_list.currentItem()
        if not item:
            return

        account, game = item.data(Qt.UserRole)

        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"<span style='color: black;'>Are you sure you want to delete the game '{game.name}'?</span>",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            account.games.remove(game)
            self.update_game_list()
            self.save_config()
    
    def account_selected(self, index):
        """Handle account selection and automatically disable 'Show All Games' mode."""
        if index >= 0 and index < len(self.accounts):
            # Uncheck the "Show All Games" button
            if self.show_all_games_button.isChecked():
                self.show_all_games_button.setChecked(False)
                self.show_all_games_button.setText("Show All Games")

            # Update the game list to show only the selected account's games
            self.update_game_list()
    
    def update_account_list(self):
        self.account_list.clear()
        for account in self.accounts:
            item = QListWidgetItem(account.name)
            auto_login_status = "Auto-login enabled" if account.auto_login else "Manual login"
            item.setToolTip(f"Username: {account.username}\nGames: {len(account.games)}\n{auto_login_status}")
            self.account_list.addItem(item)
    
    def update_game_list(self):
        self.game_list.clear()

        if self.show_all_games_button.isChecked():
            # Show all games from every account
            for account in self.accounts:
                for game in account.games:
                    if game.is_steam_game:
                        item = QListWidgetItem(f"{game.name}")
                    else:
                        item = QListWidgetItem(f"{game.name}")
                    item.setData(Qt.UserRole, (account, game))
                    # Set tooltip with game info
                    auto_login = "Auto-login" if account.auto_login else "Manual login"
                    item.setToolTip(f"App ID: {game.app_id}\nAccount: {account.username} ({auto_login})" if game.is_steam_game else "Non-Steam Game")
                    self.game_list.addItem(item)
        else:
            # Show games for the selected account
            if self.account_list.currentRow() >= 0:
                account = self.accounts[self.account_list.currentRow()]
                for game in account.games:
                    if game.is_steam_game:
                        item = QListWidgetItem(game.name)
                    else:
                        item = QListWidgetItem(f"{game.name} (Non-Steam)")
                    item.setData(Qt.UserRole, (account, game))
                    item.setToolTip(f"App ID: {game.app_id}" if game.is_steam_game else "Non-Steam Game")
                    self.game_list.addItem(item)

    def launch_selected_game(self):
        current_item = self.game_list.currentItem()
        if current_item:
            self.launch_game(current_item)
    
    def launch_game(self, item):
        account, game = item.data(Qt.UserRole)
        
        if game.is_steam_game:
            if not self.steam_path:
                QMessageBox.warning(self, "Steam Path Not Set", 
                                  "<span style='color: black;'>Please set the path to Steam.exe first.</span>")
                self.set_steam_path()
                return
            
            # Prepare progress dialog
            progress = QProgressDialog("Launching game...", "Cancel", 0, 0, self)
            progress.setWindowTitle(f"Launching {game.name}")
            progress.setMinimumDuration(500)
            progress.setCancelButton(None)
            progress.setWindowModality(Qt.WindowModal)
            
            # Password check for non-auto-login accounts
            password = None
            if account.auto_login and account.password:
                password = account.password
            
            # Launch the game with the associated account
            self.launch_thread = LaunchThread(
                self.steam_path, 
                account.username,
                password,
                game.app_id
            )
            
            # Connect signals
            self.launch_thread.launch_progress.connect(progress.setLabelText)
            self.launch_thread.launch_finished.connect(lambda: progress.close())
            
            # Show the password hint if needed
            if not account.auto_login and account.password_hint:
                hint_msg = QMessageBox()
                hint_msg.setWindowTitle("Password Hint")
                hint_msg.setText(f"You may be prompted for a password.")
                hint_msg.setInformativeText(f"Password hint: {account.password_hint}")
                hint_msg.setStandardButtons(QMessageBox.Ok)
                hint_msg.show()
            
            # Start the launch process
            progress.show()
            self.launch_thread.start()
        else:
            # Launch non-Steam game directly
            try:
                subprocess.Popen(game.path)
            except Exception as e:
                QMessageBox.warning(self, "Launch Error", f"<span style='color: black;'>Failed to launch game: {str(e)}</span>")

    def set_steam_path(self):
        default_paths = [
            "C:\\Program Files (x86)\\Steam\\steam.exe",
            "C:\\Program Files\\Steam\\steam.exe"
        ]
        
        # Check if Steam exists in default locations
        initial_dir = ""
        for path in default_paths:
            if os.path.exists(path):
                initial_dir = os.path.dirname(path)
                break
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Steam Executable", initial_dir, "Steam (steam.exe)"
        )
        
        if file_path:
            self.steam_path = file_path
            self.save_config()
    
    def save_config(self, force=False):
        # Prevent excessive saves
        if hasattr(self, '_saving_config') and not force:
            return

        try:
            self._saving_config = True
            config = {
                "steam_path": self.steam_path,
                "accounts": [account.to_dict(self.encryption_handler) for account in self.accounts]
            }

            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Config Save Error", f"<span style='color: black;'>Failed to save configuration: {str(e)}</span>")
        finally:
            delattr(self, '_saving_config')

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                    
                    self.steam_path = config.get("steam_path", "")
                    
                    # Clear existing accounts to prevent duplication
                    self.accounts.clear()
                    
                    for account_data in config.get("accounts", []):
                        account = SteamAccount.from_dict(account_data, self.encryption_handler)
                        self.accounts.append(account)
                    
                    self.update_account_list()
                    self.update_game_list()
            except Exception as e:
                QMessageBox.warning(self, "Config Load Error", f"<span style='color: black;'>Failed to load configuration: {str(e)}</span>")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MultiSteamLauncher()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()