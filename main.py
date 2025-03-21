import sys
from PyQt6.QtWidgets import QApplication
from views.login_page import LoginPage  # Import the login page

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginPage()  # Start with login page
    login_window.show()
    sys.exit(app.exec())
