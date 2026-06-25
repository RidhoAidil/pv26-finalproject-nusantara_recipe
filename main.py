import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from database.db import init_db
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Nusantara Recipe")
    app.setOrganizationName("PV2026")

    # Initialize DB (creates tables and seeds data on first run)
    init_db()

    # Show login
    login = LoginDialog()
    current_user = {}

    def on_login(user: dict):
        nonlocal current_user
        current_user = user

    login.login_success.connect(on_login)

    if login.exec() != LoginDialog.Accepted or not current_user:
        sys.exit(0)

    window = MainWindow(current_user)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()