from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QComboBox, QFrame, QMessageBox
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
import sys
import os

# Get the absolute path of the project root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import check_user_credentials  # Import database function
from views.admin_dashboard import MainWindow # Import the AdminDashboard class

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Login - Rental Management System")
        self.setGeometry(100, 100, 500, 600)
        self.setStyleSheet("background-color: white;")

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        self.logo = QLabel(self)
        pixmap = QPixmap("rental_image.png")  
        self.logo.setPixmap(pixmap.scaled(400, 500, Qt.AspectRatioMode.KeepAspectRatio))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        self.title = QLabel("Rental Management System", self)
        self.title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: black; margin-top: 10px;")

        # Login container
        self.container = QFrame(self)
        self.container.setFixedWidth(500)
        self.container.setStyleSheet("background-color: black; border-radius: 10px; padding: 20px;")
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)

        input_width = 210
        button_width = 300

        # Username field
        username_layout = QHBoxLayout()
        self.username_label = QLabel("Username:")
        self.username_label.setFixedWidth(100)
        self.username_label.setStyleSheet("background-color: gold; color: black; font-size: 12px; padding: 4px; border-radius: 4px; text-align: center;")
        self.username_input = QLineEdit()
        self.username_input.setFixedWidth(input_width)
        self.username_input.setStyleSheet("background-color: white; color: black; border-radius: 4px; padding: 6px;")
        username_layout.addWidget(self.username_label)
        username_layout.addWidget(self.username_input)

        # Password field
        password_layout = QHBoxLayout()
        self.password_label = QLabel("Password:")
        self.password_label.setFixedWidth(100)
        self.password_label.setStyleSheet("background-color: gold; color: black; font-size: 12px; padding: 4px; border-radius: 4px; text-align: center;")
        self.password_input = QLineEdit()
        self.password_input.setFixedWidth(input_width)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("background-color: white; color: black; border-radius: 4px; padding: 6px;")
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)

        # Role selection
        role_layout = QHBoxLayout()
        self.role_label = QLabel("Login as:")
        self.role_label.setFixedWidth(100)
        self.role_label.setStyleSheet("background-color: gold; color: black; font-size: 12px; padding: 4px; border-radius: 4px; text-align: center;")
        self.role_dropdown = QComboBox()
        self.role_dropdown.setFixedWidth(input_width)
        self.role_dropdown.addItems(["Admin", "Staff", "Tenant"])
        self.role_dropdown.setStyleSheet("background-color: white; color: black; border-radius: 4px; padding: 4px;")
        role_layout.addWidget(self.role_label)
        role_layout.addWidget(self.role_dropdown)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(button_width)
        self.login_button.setStyleSheet("background-color: gold; color: black; font-size: 13px; border-radius: 4px; padding: 8px;")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)  # Connect to login function

        # Forgot password link
        self.forgot_password = QLabel("<a href='#'>Forgot Password?</a>")
        self.forgot_password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.forgot_password.setStyleSheet("color: white; font-size: 10px; margin-top: 5px;")

        # Add widgets to login container
        self.container_layout.addLayout(username_layout)
        self.container_layout.addLayout(password_layout)
        self.container_layout.addLayout(role_layout)
        self.container_layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.container_layout.addWidget(self.forgot_password)

        # Add widgets to main layout
        layout.addWidget(self.logo)
        layout.addWidget(self.title)
        layout.addWidget(self.container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set main layout
        self.setLayout(layout)

    def handle_login(self):
        """Handles login authentication."""
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_dropdown.currentText()

        print(f"User Input - Username: {username}, Password: {password}, Role: {role}")  # Print user input

        if not username or not password:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Login Failed")
            msg_box.setText("Please enter both username and password.")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")  # Ensure text is visible
            msg_box.exec()
            return

        is_valid, db_username, db_hashed_password = check_user_credentials(username, password, role)

        print(f"DB Data - Username: {db_username}, Hashed Password: {db_hashed_password}")  # Print system-retrieved values

        if is_valid:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Login Successful")
            msg_box.setText(f"Welcome, {username}!")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")  # Ensure text is visible
            msg_box.exec()

            if role == "Admin":
                self.open_admin_dashboard()
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Access Denied")
                msg_box.setText("This feature is only available for admins.")
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")  # Ensure text is visible
                msg_box.exec()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Login Failed")
            msg_box.setText("Invalid username, password, or role.")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")  # Ensure text is visible
            msg_box.exec()
 
    def open_admin_dashboard(self):
            """Opens the Admin Dashboard."""
            self.admin_dashboard = MainWindow()  # Assuming AdminDashboard is another PyQt6 class
            self.admin_dashboard.show()
            self.close()  # Close login window

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginPage()
    window.show()
    sys.exit(app.exec())
