import sys
from PyQt6.QtWidgets import QApplication
from views.login_page import LoginPage  # Import the login page
from apply_late_fees import apply_late_fees

if __name__ == "__main__":
    # 💡 Apply late fees on startup
    apply_late_fees()

    # 🔐 Start the application
    app = QApplication(sys.argv)
    login_window = LoginPage()
    login_window.show()
    sys.exit(app.exec())
