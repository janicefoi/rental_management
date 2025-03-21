import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont, QPalette, QBrush, QPixmap
from PyQt6.QtCore import Qt

class HoverButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.default_size = (240, 50)  # Original size
        self.hover_size = (260, 55)  # Enlarged size

        self.setFixedSize(*self.default_size)
        self.setFont(QFont("Poppins", 14, QFont.Weight.Bold))

    def enterEvent(self, event):
        """ Enlarge button on hover """
        self.setFixedSize(*self.hover_size)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """ Restore button size when mouse leaves """
        self.setFixedSize(*self.default_size)
        super().leaveEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Rental Management System")
        self.setGeometry(100, 100, 1200, 700)

        # Main layout
        main_layout = QHBoxLayout()

        # Sidebar layout
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(15, 15, 15, 15)
        sidebar.setSpacing(15)  # Space between buttons

        # Sidebar Buttons
        btn_dashboard = HoverButton("🏠 Dashboard")
        btn_tenants = HoverButton("👤 Tenants")
        btn_payments = HoverButton("💰 Payments")
        btn_settings = HoverButton("⚙️ Settings")

        buttons = [btn_dashboard, btn_tenants, btn_payments, btn_settings]
        for btn in buttons:
            sidebar.addWidget(btn)

        # Sidebar container
        sidebar_container = QWidget()
        sidebar_container.setLayout(sidebar)
        sidebar_container.setFixedWidth(240)

        # Main content area with Background Image
        main_content = QWidget()
        main_content.setObjectName("main_content")

        # Title Label
        title = QLabel("🏠 Rental Management Dashboard", main_content)
        title.setFont(QFont("Montserrat", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout for Main Content
        content_layout = QVBoxLayout(main_content)
        content_layout.addWidget(title)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Split layout
        main_layout.addWidget(sidebar_container)
        main_layout.addWidget(main_content)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Apply Styles
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: "Poppins", "Montserrat", "Roboto", Arial;
            }

            /* Sidebar */
            QWidget#sidebar_container {
                background-color: #222;
                border-radius: 12px;
                padding: 10px;
            }

            QPushButton {
                background-color: black;
                color: gold;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                padding: 14px;
                transition: all 0.3s ease-in-out;
            }

            QPushButton:hover {
                background-color: #FFD700;
                color: black;
            }

            /* Main Content with Background Image */
            QWidget#main_content {
                background-image: url('rental_image');  /* Replace with actual image path */
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
                border-radius: 15px;
            }

            QLabel {
                color: white;
                font-size: 24px;
                background: rgba(0, 0, 0, 0.6);
                padding: 10px;
                border-radius: 10px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
