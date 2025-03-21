import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGridLayout, QFrame
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QTimer
from views.property_management import PropertiesPage
from views.tenant_management import TenantManagementPage
from views.payment_management import PaymentManagementPage

class HoverButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.default_size = (220, 50)
        self.hover_size = (230, 55)
        self.setFixedSize(*self.default_size)
        self.setFont(QFont("Poppins", 12, QFont.Weight.Bold))

    def enterEvent(self, event):
        self.setFixedSize(*self.hover_size)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setFixedSize(*self.default_size)
        super().leaveEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(100, 100, 1200, 700)

        main_layout = QHBoxLayout()

        # Sidebar layout
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(15, 15, 15, 15)
        sidebar.setSpacing(20)

        # Define buttons
        btn_dashboard = HoverButton("🏠 Dashboard")
        btn_properties = HoverButton("🏢 Properties")
        btn_tenants = HoverButton("👤 Tenants")
        btn_payments = HoverButton("💰 Payments")
        btn_maintenance = HoverButton("🛠 Maintenance")
        btn_reports = HoverButton("📊 Reports")

        # Connect buttons to respective functions
        btn_properties.clicked.connect(self.open_property_management)
        btn_tenants.clicked.connect(self.open_tenant_management)
        btn_payments.clicked.connect(self.open_payment_management)
       

        buttons = [btn_dashboard, btn_properties, btn_tenants, btn_payments, btn_maintenance, btn_reports]
        for btn in buttons:
            sidebar.addWidget(btn)

        sidebar_container = QWidget()
        sidebar_container.setLayout(sidebar)
        sidebar_container.setFixedWidth(250)

        # Main content
        main_content = QWidget()
        main_content.setObjectName("main_content")

        # Background slideshow
        self.slideshow_label = QLabel()
        self.slideshow_label.setFixedSize(1000, 400)
        self.slideshow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Overlay title on slideshow
        self.title_label = QLabel("🏠 Admin Dashboard")
        self.title_label.setFont(QFont("Montserrat", 24, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_layout = QVBoxLayout()
        title_layout.addWidget(self.slideshow_label)
        title_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        title_container = QWidget()
        title_container.setLayout(title_layout)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        stats = [
            ("Occupied Units", "🏠", "120"),
            ("Vacant Units", "📭", "30"),
            ("Total Revenue", "💰", "$50,000"),
            ("Pending Payments", "⚠️", "$5,000")
        ]

        for i, (label, icon, value) in enumerate(stats):
            card = QFrame()
            card.setStyleSheet("background-color: black; border-radius: 10px; padding: 10px;")
            card_layout = QVBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Arial", 24))
            text_label = QLabel(label)
            text_label.setFont(QFont("Poppins", 12, QFont.Weight.Bold))
            value_label = QLabel(value)
            value_label.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
            text_label.setStyleSheet("color: gold;")
            value_label.setStyleSheet("color: gold;")
            icon_label.setStyleSheet("color: gold;")

            card_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignCenter)

            card.setLayout(card_layout)
            grid_layout.addWidget(card, i // 2, i % 2)

        content_layout = QVBoxLayout()
        content_layout.addWidget(title_container)
        content_layout.addLayout(grid_layout)
        main_content.setLayout(content_layout)

        main_layout.addWidget(sidebar_container)
        main_layout.addWidget(main_content)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Styling
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: "Poppins", "Montserrat", "Roboto", Arial;
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
                background-color: gold;
                color: black;
            }
            QLabel {
                color: black;
            }
        """)

        # Image Slideshow
        self.images = ["admin_dashboard.jpg", "admin_dashboard2.jpg", "admin_dashboard3.jpg", "admin_dashboard5.jpg", "admin_dashboard6.jpg"]
        self.current_image_index = 0
        self.update_slideshow()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.start(5000)

    def update_slideshow(self):
        """Update the slideshow with the current image."""
        pixmap = QPixmap(self.images[self.current_image_index])
        if not pixmap.isNull():
            self.slideshow_label.setPixmap(pixmap.scaled(self.slideshow_label.width(), self.slideshow_label.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.slideshow_label.setText("Image not found")

    def next_image(self):
        """Switch to the next image in the slideshow."""
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.update_slideshow()

    # Navigation Functions
    def open_property_management(self):
        self.hide()  # Hide Admin Dashboard instead of closing it
        self.property_window = PropertiesPage()
        self.property_window.show()

    def open_tenant_management(self):
        self.hide()  # Hide Admin Dashboard instead of closing it
        self.property_window = TenantManagementPage()
        self.property_window.show()

    
    def open_payment_management(self):
        self.hide()  # Hide Admin Dashboard instead of closing it
        self.property_window = PaymentManagementPage()
        self.property_window.show()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
