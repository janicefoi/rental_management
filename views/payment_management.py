import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame, QHBoxLayout, QApplication, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont, QPixmap

class PaymentCard(QFrame):
    def __init__(self, text, callback, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 150)
        self.setStyleSheet("""
            QFrame {
                background-color: black;
                padding: 10px;
                border-radius: 10px;
            }
            QFrame:hover {
                background-color: gold;
            }
        """)
        
        button = QPushButton(text)
        button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: gold;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: gold;
                color: black;
            }
        """)
        button.clicked.connect(callback)
        
        layout = QVBoxLayout(self)
        layout.addWidget(button)

class PaymentManagementPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Payment Management")
        self.setGeometry(100, 100, 1200, 700)
        
        self.images = [
            os.path.join(os.getcwd(), "payment_management.jpg"),
            os.path.join(os.getcwd(), "payment_management2.jpg"),
            os.path.join(os.getcwd(), "payment_management3.jpg"),
            os.path.join(os.getcwd(), "payment_management4.jpg")
        ]
        self.current_image_index = 0
        
        self.initUI()
    
    def initUI(self):
        self.main_layout = QVBoxLayout()
        
        # **Back Button Section**
        back_button_layout = QHBoxLayout()
        back_button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        back_button = QPushButton("← Back")
        back_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        back_button.setFixedSize(120, 40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: gold;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: gold;
                color: black;
            }
        """)
        back_button.clicked.connect(self.go_back)
        back_button_layout.addWidget(back_button)
        self.main_layout.addLayout(back_button_layout)
        
        # Slideshow
        self.slideshow_label = QLabel()
        self.slideshow_label.setFixedSize(1200, 400)
        self.slideshow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slideshow_label.setStyleSheet("border-radius: 10px; background-color: black;")
        self.main_layout.addWidget(self.slideshow_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Animation Effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.slideshow_label.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(1000)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.start(5000)
        
        # Payment Management Cards
        self.payment_grid = QGridLayout()
        
        rent_payments_card = PaymentCard("Rent Payments", self.open_rent_payments, self)
        invoices_card = PaymentCard("Invoices", self.open_invoices, self)
        reports_card = PaymentCard("Reports & Analytics", self.open_reports, self)
        
        self.payment_grid.addWidget(rent_payments_card, 0, 0)
        self.payment_grid.addWidget(invoices_card, 0, 1)
        self.payment_grid.addWidget(reports_card, 0, 2)
        
        container = QWidget()
        container.setLayout(self.payment_grid)
        self.main_layout.addWidget(container)
        
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: white;")
        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)
        
        self.update_slideshow()
    
    def go_back(self):
        from views.admin_dashboard import MainWindow
        self.admin_dashboard = MainWindow()
        self.admin_dashboard.show()
        self.close()
    
    def update_slideshow(self):
        if not self.images:
            self.slideshow_label.setText("No images available")
            return
        image_path = self.images[self.current_image_index]
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.slideshow_label.setPixmap(pixmap.scaled(
                self.slideshow_label.width(), self.slideshow_label.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.slideshow_label.setText("Image not found")
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.update_slideshow()
    
    def open_rent_payments(self):
        from views.rent_payments import RentPaymentsPage
        self.rent_payments_page = RentPaymentsPage()
        self.rent_payments_page.show()
        self.close()
    
    def open_invoices(self):
        from views.invoices import InvoicesPage
        self.invoices_page = InvoicesPage()
        self.invoices_page.show()
        self.close()
    
    def open_reports(self):
        from views.report_analytics import ReportsPage
        self.reports_page = ReportsPage()
        self.reports_page.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaymentManagementPage()
    window.show()
    sys.exit(app.exec())
