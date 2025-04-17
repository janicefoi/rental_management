import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame, QLineEdit, QApplication, QGraphicsOpacityEffect, QHBoxLayout, QDialog, QFormLayout, QSpinBox, QMessageBox,
    QComboBox, QScrollArea, QSizePolicy

)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont, QPixmap
import psycopg2
from db import connect_db 
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal
from views.unit_management import UnitManagementPage


class PropertyCard(QFrame):
    clicked = pyqtSignal(int)
    edit_clicked = pyqtSignal(int)

    def __init__(self, property_id, name, address, total_units, payment_modes, parent=None):
        super().__init__(parent)
        self.property_id = property_id
        self.setFixedSize(300, 200)
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                padding: 10px;
                border-radius: 10px;
                border: 2px solid #1a1a1a;
            }
            QFrame:hover {
                border: 2px solid #FFD700;
            }
        """)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)  # Add consistent spacing between elements

        # Property Name Label
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #FFD700; padding-bottom: 5px;")

        # Other details
        payment_modes_str = ", ".join(payment_modes) if payment_modes else "None"
        details_label = QLabel(f"Address: {address}\nTotal Units: {total_units}\nPayment Modes: {payment_modes_str}")
        details_label.setFont(QFont("Arial", 11))
        details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        details_label.setStyleSheet("color: white;")

        # Edit button
        edit_button = QPushButton("✎")
        edit_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        edit_button.setFixedSize(30, 30)
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #1a1a1a;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: white;
            }
        """)
        edit_button.clicked.connect(lambda: self.edit_clicked.emit(self.property_id))

        # Add widgets to layout
        layout.addWidget(name_label)
        layout.addWidget(details_label)
        layout.addStretch()  # Add stretch to push edit button to bottom
        layout.addWidget(edit_button, alignment=Qt.AlignmentFlag.AlignLeft)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.property_id)



class PropertiesPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Properties Management")
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
        # Create a main widget and layout
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar {
                width: 0px;
                height: 0px;
            }
        """)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 0px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: transparent;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # Create a container widget for the scroll area
        scroll_widget = QWidget()
        self.main_layout = QVBoxLayout(scroll_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # Add your existing UI elements to main_layout
        # Back button section
        back_button_layout = QHBoxLayout()
        back_button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        back_button = QPushButton("← Back")
        back_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        back_button.setFixedSize(120, 40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #FFD700;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
                border: 2px solid #1a1a1a;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #1a1a1a;
                border: 2px solid #FFD700;
            }
        """)
        back_button.clicked.connect(self.go_back)
        back_button_layout.addWidget(back_button)

        self.main_layout.addLayout(back_button_layout)

        # Slideshow Container
        self.slideshow_label = QLabel()
        self.slideshow_label.setFixedSize(1100, 400)  # Match admin dashboard dimensions
        self.slideshow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slideshow_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border-radius: 15px;
                padding: 10px;
                margin: 20px;
            }
        """)

        # Create a container for slideshow and center it
        slideshow_container = QWidget()
        slideshow_layout = QVBoxLayout(slideshow_container)
        slideshow_layout.setContentsMargins(20, 20, 20, 20)
        slideshow_layout.addWidget(self.slideshow_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addWidget(slideshow_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Auto switch images every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.start(5000)

        # Add Property Button
        add_property_button = QPushButton("Add Property")
        add_property_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        add_property_button.setFixedWidth(200)
        add_property_button.setStyleSheet("""
            QPushButton {
                background-color: gold;
                color: black;
                font-weight: bold;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: black;
                color: gold;
            }
        """)
        add_property_button.clicked.connect(self.show_add_property_dialog)
        self.main_layout.addWidget(add_property_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Property Cards Section
        self.properties_grid = QGridLayout()
        self.properties_grid.setSpacing(20)  # Set uniform spacing
        self.properties_grid.setContentsMargins(0, 0, 0, 0)
        self.load_properties()

        properties_container = QWidget()
        properties_container.setLayout(self.properties_grid)
        self.main_layout.addWidget(properties_container)

        # Set the scroll widget as the main widget
        scroll_area.setWidget(scroll_widget)
        self.setCentralWidget(scroll_area)  # Use scroll_area as the central widget
        self.setStyleSheet("background-color: white;")

    def load_properties(self):
        # Clear existing items from the grid
        while self.properties_grid.count():
            item = self.properties_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        row, col = 0, 0
        for prop in self.properties:
            card = PropertyCard(prop["id"], prop["name"], prop["address"], 
                              prop["total_units"], prop["payment_modes"], parent=self)
            card.clicked.connect(self.open_unit_management)
            card.edit_clicked.connect(self.show_edit_property_dialog)
            
            self.properties_grid.addWidget(card, row, col)
            
            col += 1
            if col > 2:  # After 3 cards, move to next row
                col = 0
                row += 1

        # Add stretch at the bottom to push cards to the top
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.properties_grid.addWidget(spacer, (row + 1) * 2, 0, 1, 3)


    def show_add_property_dialog(self):
        # Create the dialog window
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Property")
        dialog.setFixedSize(400, 450)
        dialog.setStyleSheet("background-color: white; border-radius: 10px;")

        # Create the form layout
        layout = QFormLayout()
        layout.setVerticalSpacing(15)

        # Define font and styles
        label_font = QFont("Arial", 12, QFont.Weight.Bold)
        label_style = """
            QLabel {
                background-color: black;
                color: gold;
                padding: 5px;
                border-radius: 5px;
            }
        """
        field_style = """
            QLineEdit, QComboBox {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid gray;
                border-radius: 5px;
                padding: 5px;
                font-size: 11pt;
            }
        """

        # Name
        name_label = QLabel("Name:")
        name_label.setFont(label_font)
        name_label.setStyleSheet(label_style)
        name_input = QLineEdit()
        name_input.setStyleSheet(field_style)

        # Address
        address_label = QLabel("Address:")
        address_label.setFont(label_font)
        address_label.setStyleSheet(label_style)
        address_input = QLineEdit()
        address_input.setStyleSheet(field_style)

        # Mpesa Paybill
        mpesa_paybill_label = QLabel("Mpesa Paybill:")
        mpesa_paybill_label.setFont(label_font)
        mpesa_paybill_label.setStyleSheet(label_style)
        mpesa_paybill_input = QLineEdit()
        mpesa_paybill_input.setStyleSheet(field_style)

        # Mpesa Account No
        mpesa_account_label = QLabel("Mpesa Account No:")
        mpesa_account_label.setFont(label_font)
        mpesa_account_label.setStyleSheet(label_style)
        mpesa_account_input = QLineEdit()
        mpesa_account_input.setStyleSheet(field_style)

        # Bank Name (Dropdown)
        bank_name_label = QLabel("Bank Name:")
        bank_name_label.setFont(label_font)
        bank_name_label.setStyleSheet(label_style)
        bank_name_dropdown = QComboBox()
        bank_name_dropdown.setStyleSheet(field_style)
        bank_name_dropdown.addItems(["", "Equity", "KCB", "DTB", "Absa", "Co-operative"])  # Allow empty selection

        # Bank Account No
        bank_account_label = QLabel("Bank Account No:")
        bank_account_label.setFont(label_font)
        bank_account_label.setStyleSheet(label_style)
        bank_account_input = QLineEdit()
        bank_account_input.setStyleSheet(field_style)

        # Save Button
        save_button = QPushButton("Save")
        save_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: gold;
                color: black;
                font-weight: bold;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: black;
                color: gold;
            }
        """)
        save_button.clicked.connect(lambda: self.save_property(
            name_input.text(), 
            address_input.text(), 
            "Mpesa", 
            mpesa_paybill_input.text(), 
            mpesa_account_input.text(), 
            bank_name_dropdown.currentText(),  # Get selected bank
            bank_account_input.text(), 
            dialog
        ))

        # Adding widgets to the layout
        layout.addRow(name_label, name_input)
        layout.addRow(address_label, address_input)
        layout.addRow(mpesa_paybill_label, mpesa_paybill_input)
        layout.addRow(mpesa_account_label, mpesa_account_input)
        layout.addRow(bank_name_label, bank_name_dropdown)  # Add bank dropdown
        layout.addRow(bank_account_label, bank_account_input)
        layout.addRow(QLabel())  # Empty label for spacing
        layout.addRow(save_button)

        dialog.setLayout(layout)
        dialog.exec()


    def save_property(self, name, address, payment_mode, mpesa_paybill, mpesa_account_no, bank_name, bank_account_no, dialog):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Insert into apartments table and get the new apartment_id
            cursor.execute("INSERT INTO apartments (name, address) VALUES (%s, %s) RETURNING id;", (name, address))
            apartment_id = cursor.fetchone()[0]
            
            # Determine which payment methods to insert
            payment_methods = []
            
            # Add Mpesa if Mpesa details are provided
            if mpesa_paybill or mpesa_account_no:
                cursor.execute("""
                    INSERT INTO apartment_payment_methods 
                    (apartment_id, payment_mode, mpesa_paybill, mpesa_account_no) 
                    VALUES (%s, 'Mpesa', %s, %s);
                """, (apartment_id, mpesa_paybill or None, mpesa_account_no or None))
                payment_methods.append('Mpesa')
            
            # Add Bank if bank details are provided
            if bank_name or bank_account_no:
                cursor.execute("""
                    INSERT INTO apartment_payment_methods 
                    (apartment_id, payment_mode, bank_name, bank_account_no) 
                    VALUES (%s, 'Bank', %s, %s);
                """, (apartment_id, bank_name or None, bank_account_no or None))
                payment_methods.append('Bank')
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Refresh the properties list in UI
            self.properties = self.fetch_properties()
            self.load_properties()
            
            dialog.accept()
            QMessageBox.information(self, "Success", "Property added successfully!")
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to add property: {str(e)}")
            print(f"Database error: {e}")


    def show_edit_property_dialog(self, property_id):
        """Show edit property dialog with existing details."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.name, a.address, 
                COALESCE(apm.mpesa_paybill, '') AS mpesa_paybill, 
                COALESCE(apm.mpesa_account_no, '') AS mpesa_account_no, 
                COALESCE(apm.bank_name, '') AS bank_name,
                COALESCE(apm.bank_account_no, '') AS bank_account_no
            FROM apartments a
            LEFT JOIN apartment_payment_methods apm 
                ON a.id = apm.apartment_id
            WHERE a.id = %s;
        """, (property_id,))
        property_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if not property_data:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Property")
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet("background-color: white; border-radius: 10px;")

        layout = QFormLayout()
        layout.setVerticalSpacing(15)

        label_font = QFont("Arial", 12, QFont.Weight.Bold)
        label_style = """
            QLabel {
                background-color: black;
                color: gold;
                padding: 5px;
                border-radius: 5px;
            }
        """
        field_style = """
            QLineEdit, QComboBox {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid gray;
                border-radius: 5px;
                padding: 5px;
                font-size: 11pt;
            }
        """

        name_label = QLabel("Name:")
        name_label.setFont(label_font)
        name_label.setStyleSheet(label_style)
        name_input = QLineEdit(property_data[0])
        name_input.setStyleSheet(field_style)
        name_input.setReadOnly(True)

        address_label = QLabel("Address:")
        address_label.setFont(label_font)
        address_label.setStyleSheet(label_style)
        address_input = QLineEdit(property_data[1])
        address_input.setStyleSheet(field_style)
        address_input.setReadOnly(True)

        mpesa_paybill_label = QLabel("Mpesa Paybill:")
        mpesa_paybill_label.setFont(label_font)
        mpesa_paybill_label.setStyleSheet(label_style)
        mpesa_paybill_input = QLineEdit(property_data[2] if property_data[2] else "")
        mpesa_paybill_input.setStyleSheet(field_style)

        mpesa_account_label = QLabel("Mpesa Account No:")
        mpesa_account_label.setFont(label_font)
        mpesa_account_label.setStyleSheet(label_style)
        mpesa_account_input = QLineEdit(property_data[3] if property_data[3] else "")
        mpesa_account_input.setStyleSheet(field_style)

        bank_name_label = QLabel("Bank Name:")
        bank_name_label.setFont(label_font)
        bank_name_label.setStyleSheet(label_style)
        bank_name_dropdown = QComboBox()
        bank_name_dropdown.setStyleSheet(field_style)
        
        # Add bank names to the dropdown
        bank_names = ["", "Equity", "KCB", "DTB", "Absa", "Co-operative"]
        bank_name_dropdown.addItems(bank_names)

        # Set the currently saved bank name
        if property_data[4] in bank_names:
            bank_name_dropdown.setCurrentText(property_data[4])
        else:
            bank_name_dropdown.setCurrentIndex(-1)  # No selection if bank name is not found

        bank_account_label = QLabel("Bank Account No:")
        bank_account_label.setFont(label_font)
        bank_account_label.setStyleSheet(label_style)
        bank_account_input = QLineEdit(property_data[5] if property_data[5] else "")
        bank_account_input.setStyleSheet(field_style)

        save_button = QPushButton("Save")
        save_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        save_button.setStyleSheet("background-color: gold; color: black; padding: 10px; border-radius: 10px;")
        save_button.clicked.connect(lambda: self.update_property(
            property_id, mpesa_paybill_input.text(), mpesa_account_no.text(), 
            bank_account_input.text(), bank_name_dropdown.currentText(), dialog
        ))

        layout.addRow(name_label, name_input)
        layout.addRow(address_label, address_input)
        layout.addRow(mpesa_paybill_label, mpesa_paybill_input)
        layout.addRow(mpesa_account_label, mpesa_account_input)
        layout.addRow(bank_name_label, bank_name_dropdown)  # Corrected position
        layout.addRow(bank_account_label, bank_account_input)
        layout.addRow(save_button)

        dialog.setLayout(layout)
        dialog.exec()



    def update_property(self, property_id, mpesa_paybill, mpesa_account_no, bank_account_no, bank_name, dialog):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Check if the property already has a payment record
            cursor.execute("SELECT id FROM apartment_payment_methods WHERE apartment_id = %s", (property_id,))
            existing_record = cursor.fetchone()

            if existing_record:
                # If it exists, update it
                cursor.execute("""
                    UPDATE apartment_payment_methods
                    SET mpesa_paybill = %s, mpesa_account_no = %s, bank_account_no = %s, bank_name = %s
                    WHERE apartment_id = %s
                """, (mpesa_paybill, mpesa_account_no, bank_account_no, bank_name, property_id))
            else:
                # Determine the payment mode based on input fields
                payment_mode = "Mpesa" if mpesa_paybill else "Bank"

                # If it does not exist, insert a new one
                cursor.execute("""
                    INSERT INTO apartment_payment_methods (apartment_id, payment_mode, mpesa_paybill, mpesa_account_no, bank_account_no, bank_name)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (property_id, payment_mode, mpesa_paybill, mpesa_account_no, bank_account_no, bank_name))

            conn.commit()
            cursor.close()
            conn.close()

            QMessageBox.information(self, "Success", "Property payment details updated successfully")
            dialog.accept()  # Close the dialog after a successful update

            # Refresh the property card UI
            self.refresh_property_card(property_id, mpesa_paybill, mpesa_account_no, bank_account_no)


        except psycopg2.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to update property details: {e}")


    def refresh_property_card(self, property_id, mpesa_paybill, mpesa_account_no, bank_account_no):
        """
        Updates the property card with the latest payment details after an update.
        """
        for card in self.property_cards:  # Loop through all property cards
            if card.property_id == property_id:  # Find the card that matches
                # Update displayed details
                card.mpesa_paybill_label.setText(f"Mpesa PayBill: {mpesa_paybill if mpesa_paybill else 'N/A'}")
                card.mpesa_account_label.setText(f"Mpesa Account No: {mpesa_account_no if mpesa_account_no else 'N/A'}")
                card.bank_account_label.setText(f"Bank Account No: {bank_account_no if bank_account_no else 'N/A'}")

                # Trigger a UI refresh
                card.repaint()  # Ensures the UI updates immediately

                break  # Exit loop once the correct property card is updated


    def go_back(self):
        from views.admin_dashboard import MainWindow
        self.admin_dashboard = MainWindow()
        self.admin_dashboard.show()
        self.close()

    def update_slideshow(self):
        """Update the slideshow with the current image."""
        if not self.images:
            self.slideshow_label.setText("No images available")
            return
            
        pixmap = QPixmap(self.images[self.current_image_index])
        if not pixmap.isNull():
            self.slideshow_label.setPixmap(
                pixmap.scaled(
                    self.slideshow_label.width(),
                    self.slideshow_label.height(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            self.slideshow_label.setText("Image not found")

    def next_image(self):
        """Switch to the next image in the slideshow."""
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.update_slideshow()

    def open_unit_management(self, property_id):
        """Open the unit management page for the given property_id."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM apartments WHERE id = %s;", (property_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                apartment_name = result[0]
                self.unit_management_page = UnitManagementPage(property_id, apartment_name)
                self.unit_management_page.show()
            else:
                print(f"No apartment found with ID {property_id}")
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        self.close()  # Close the Property Management Page

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PropertiesPage()
    window.show()
    sys.exit(app.exec())
