import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame, QLineEdit, QApplication, QGraphicsOpacityEffect, QHBoxLayout, QDialog, QFormLayout, QSpinBox, QMessageBox,
    QComboBox

)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont, QPixmap
import psycopg2
from db import connect_db 
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal



class PropertyCard(QFrame):
    clicked = pyqtSignal(int)
    edit_clicked = pyqtSignal(int)  # Signal for edit button

    def __init__(self, property_id, name, address, total_units, parent=None):
        super().__init__(parent)
        self.property_id = property_id
        self.setFixedSize(300, 200)
        self.setStyleSheet("""
            QFrame {
                background-color: black;
                padding: 10px;
                border-radius: 10px;
                position: relative;
            }
            QFrame:hover {
                background-color: gold;
            }
        """)


        text_label = QLabel(f"{name}\nAddress: {address}\nTotal Units: {total_units}")
        text_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("""
            color: gold;
            QFrame:hover & {
                color: black;
            }
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.property_id)



class MaintenancePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maintenance Management")
        self.setGeometry(100, 100, 1200, 700)

        # Image paths
        self.images = [
            os.path.join(os.getcwd(), "property_management.jpg"),
            os.path.join(os.getcwd(), "property_management2.jpg"),
            os.path.join(os.getcwd(), "property_management3.jpg"),
            os.path.join(os.getcwd(), "property_management4.jpg")
        ]
        self.current_image_index = 0  # Track current image

        self.properties = self.fetch_properties()
        self.property_cards = []  # Ensure property_cards is initialized as an empty list
        self.initUI()

    def fetch_properties(self):
        """Fetch properties from the database."""
        properties = []
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, a.name, a.address, COUNT(u.id) AS total_units,
                    ARRAY(SELECT payment_mode FROM apartment_payment_methods apm WHERE apm.apartment_id = a.id) AS payment_modes
                FROM apartments a
                LEFT JOIN units u ON a.id = u.apartment_id
                GROUP BY a.id;
            """)
            rows = cursor.fetchall()
            for row in rows:
                properties.append({
                    "id": row[0], "name": row[1], "address": row[2], 
                    "total_units": row[3], "payment_modes": row[4]
                })
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        return properties

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

        # Slideshow Container
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

        # Auto switch images every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.start(5000)

        # Maintenance Management Title
        title_label = QLabel("Maintenance Management")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: black; margin-top: 15px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title_label)


        # Property Cards Section
        self.properties_grid = QGridLayout()
        self.properties_grid.setSpacing(10)
        self.load_properties()

        properties_container = QWidget()
        properties_container.setLayout(self.properties_grid)
        self.main_layout.addWidget(properties_container)

        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: white;")
        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)
        self.update_slideshow()


    def load_properties(self):
        row, col = 0, 0
        for prop in self.properties:
            card = PropertyCard(prop["id"], prop["name"], prop["address"], prop["total_units"], parent=self)
            card.clicked.connect(lambda _, pid=prop["id"]: self.property_maintenace_management(pid))
            self.properties_grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

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
            self.slideshow_label.setPixmap(pixmap.scaled(self.slideshow_label.width(), self.slideshow_label.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.slideshow_label.setText("Image not found")
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.update_slideshow()


    def property_maintenace_management(self, property_id):
        """Open the unit management page for the given property_id."""
        from views.property_maintenance_management import PropertyMaintenanceManagement
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM apartments WHERE id = %s;", (property_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                apartment_name = result[0]
                self.property_window = PropertyMaintenanceManagement(property_id, apartment_name)
                self.property_window.show()
            else:
                print(f"No apartment found with ID {property_id}")
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        self.close()  # Close the Property Management Page

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MaintenancePage()
    window.show()
    sys.exit(app.exec())
