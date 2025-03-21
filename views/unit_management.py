import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog,
    QFormLayout, QLineEdit, QSpinBox, QComboBox, QMessageBox, QApplication,
    QSizePolicy, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import psycopg2
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db  # Ensure this imports your database connection function


class UnitManagementPage(QMainWindow):
    def __init__(self, apartment_id, apartment_name):
        super().__init__()
        self.apartment_id = apartment_id
        self.apartment_name = apartment_name
        self.setWindowTitle(f"Unit Management - {self.apartment_name}")
        self.setGeometry(100, 100, 900, 600)  # Increased window width
        self.initUI()
        self.load_units()  # Load the units into the table

    def initUI(self):
        self.main_layout = QVBoxLayout()

        # **Top Button Section (Back & Filter)**
        top_button_layout = QHBoxLayout()

        # **Back Button**
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

        # **Spacer Item (to push buttons apart)**
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # **Filter Button**
        filter_button = QPushButton("Filter")
        filter_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        filter_button.setFixedSize(120, 40)
        filter_button.setStyleSheet("""
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
        filter_button.clicked.connect(self.toggle_filter_panel)
        # **Reset Button**
        reset_button = QPushButton("⟳")
        reset_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))  # Slightly bigger font for icon
        reset_button.setFixedSize(40, 40)  # Make it round
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: gray;
                color: white;
                border-radius: 20px;  /* Makes the button round */
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: lightgray;
                color: black;
            }
        """)
        reset_button.clicked.connect(self.reset_filters)  # Connect it to reset function

        # **Modify Layout to Include Reset Button**
        top_button_layout.addWidget(back_button)
        top_button_layout.addWidget(spacer)
        top_button_layout.addWidget(filter_button)
        top_button_layout.addWidget(reset_button)  # Add Reset Button next to Filter Button

        self.main_layout.addLayout(top_button_layout)


        # **Title Label**
        title_label = QLabel(f"{self.apartment_name} Units Management")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: black;")
        self.main_layout.addWidget(title_label)

        # **Units Table**
        self.units_table = QTableWidget()
        self.units_table.setColumnCount(6)
        self.units_table.setHorizontalHeaderLabels(["Unit Number", "Floor Number", "Rent Amount", "Status", "Unit Type", "Actions"])
        self.units_table.verticalHeader().setDefaultSectionSize(30)

        # Adjust column widths
        self.units_table.setColumnWidth(0, 150)
        self.units_table.setColumnWidth(1, 120)
        self.units_table.setColumnWidth(2, 150)
        self.units_table.setColumnWidth(3, 150)
        self.units_table.setColumnWidth(4, 150)
        self.units_table.setColumnWidth(5, 200)

        self.units_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: transparent;
                border: 2px solid black;
                border-radius: 10px;
            }
            QTableWidget::item {
                border: none;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                border: none;
            }
        """)

        # **Sliding Filter Panel (Initially Hidden)**
        self.filter_panel = QWidget()
        self.filter_panel.setFixedWidth(300)  # Panel Width (300px)
        self.filter_panel.setStyleSheet("background-color: black; border-left: 2px solid gold;")

        filter_layout = QVBoxLayout()
        filter_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # **Filter Panel Title**
        filter_title = QLabel("Filter Units")
        filter_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        filter_title.setStyleSheet("color: gold;")
        filter_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        filter_layout.addWidget(filter_title)

        # **Status Group**
        status_label = QLabel("Status")
        status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_label.setStyleSheet("color: white;")
        filter_layout.addWidget(status_label)

        self.available_checkbox = QCheckBox("Available")
        self.occupied_checkbox = QCheckBox("Occupied")
        self.maintenance_checkbox = QCheckBox("Under Maintenance")

        for checkbox in [self.available_checkbox, self.occupied_checkbox, self.maintenance_checkbox]:
            checkbox.setStyleSheet("color: gold;")
            filter_layout.addWidget(checkbox)

        # **Unit Type Group**
        unit_type_label = QLabel("Unit Type")
        unit_type_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        unit_type_label.setStyleSheet("color: white;")
        filter_layout.addWidget(unit_type_label)

        self.studio_checkbox = QCheckBox("Studio")
        self.one_bedroom_checkbox = QCheckBox("One Bedroom")
        self.two_bedroom_checkbox = QCheckBox("Two Bedroom")

        for checkbox in [self.studio_checkbox, self.one_bedroom_checkbox, self.two_bedroom_checkbox]:
            checkbox.setStyleSheet("color: gold;")
            filter_layout.addWidget(checkbox)

        # **Apply Button**
        apply_button = QPushButton("Apply Filter")
        apply_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        apply_button.setFixedSize(150, 40)
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: gold;
                color: black;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: black;
                color: gold;
            }
        """)
        apply_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(apply_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.filter_panel.setLayout(filter_layout)
        self.filter_panel.hide()  # Hide initially

        # **Main Content Layout (Table & Filter Panel Side-by-Side)**
        self.content_layout = QHBoxLayout()
        self.content_layout.addWidget(self.units_table)
        self.content_layout.addWidget(self.filter_panel)

        self.main_layout.addLayout(self.content_layout)

        # **Add Unit Button**
        add_unit_button = QPushButton("Add Unit")
        add_unit_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        add_unit_button.setStyleSheet("""
            QPushButton {
                background-color: gold;
                color: black;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: black;
                color: gold;
            }
        """)
        add_unit_button.clicked.connect(self.show_add_unit_dialog)
        self.main_layout.addWidget(add_unit_button, alignment=Qt.AlignmentFlag.AlignRight)

        # **Set Main Layout**
        container = QWidget()
        container.setStyleSheet("background-color: white;")
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)


    def load_units(self):
        """Fetch and display units for the current apartment."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, unit_number, floor_number, rent_amount, status, unit_type
                FROM units
                WHERE apartment_id = %s;
            """, (self.apartment_id,))
            units = cursor.fetchall()
            self.units_table.setRowCount(len(units))
            for row_idx, unit in enumerate(units):
                unit_id, unit_number, floor_number, rent_amount, status, unit_type = unit
                self.units_table.setItem(row_idx, 0, QTableWidgetItem(unit_number))
                self.units_table.setItem(row_idx, 1, QTableWidgetItem(str(floor_number)))
                self.units_table.setItem(row_idx, 2, QTableWidgetItem(f"{rent_amount:.2f}"))
                self.units_table.setItem(row_idx, 3, QTableWidgetItem(status))
                self.units_table.setItem(row_idx, 4, QTableWidgetItem(unit_type))


                # Actions (Edit/Delete)
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                edit_button = QPushButton("Edit")
                delete_button = QPushButton("Delete")

                edit_button.setStyleSheet("background-color: green; color: black;")
                delete_button.setStyleSheet("background-color: red; color: black;")
                
                edit_button.setFixedWidth(80)
                delete_button.setFixedWidth(80)

                edit_button.clicked.connect(lambda _, uid=unit_id: self.show_edit_unit_dialog(uid))
                delete_button.clicked.connect(lambda _, uid=unit_id: self.delete_unit(uid))
                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                actions_widget.setLayout(actions_layout)
                self.units_table.setCellWidget(row_idx, 5, actions_widget)

            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            print(f"Database error: {e}")


    def show_add_unit_dialog(self):
        """Display a styled dialog to add a new unit."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Unit")
        dialog.setFixedSize(550, 280)  # Reduced height slightly
        dialog.setStyleSheet("background-color: white;")  # White background

        layout = QFormLayout()
        layout.setHorizontalSpacing(50)  # Increased spacing between labels and inputs
        layout.setVerticalSpacing(10)  # Reduced vertical spacing for a compact layout

        # Define font and styles
        label_font = QFont("Arial", 12, QFont.Weight.Bold)

        label_style = """
            QLabel {
                background-color: black;
                color: gold;
                padding: 5px;
                border-radius: 5px;
                min-width: 140px;  
                max-width: 140px;
                min-height: 20px;  /* Ensuring all labels have the same height */
                max-height: 20px;
                text-align: right;
            }
        """
        field_style = """
            QLineEdit, QSpinBox, QComboBox {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid gray;
                border-radius: 5px;
                padding: 2px;  /* Reduced padding for height control */
                font-size: 11pt;
                min-width: 180px;
                max-width: 180px;
                min-height: 20px;  /* Matching the height of the labels */
                max-height: 20px;
            }
        """
        button_style = """
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
        """

        # Create input fields
        unit_number_input = QLineEdit()
        floor_number_input = QSpinBox()
        floor_number_input.setMinimum(1)
        rent_amount_input = QLineEdit()
        status_input = QComboBox()
        status_input.addItems(["available", "occupied", "under maintenance"])
        unit_type_input = QComboBox()
        unit_type_input.addItems(["studio", "one_bedroom", "two_bedroom", "three_bedroom"])

        # Apply styles
        for widget in [unit_number_input, floor_number_input, rent_amount_input, status_input, unit_type_input]:
            widget.setStyleSheet(field_style)

        # Create labels and ensure uniform size
        labels = [
            ("Unit Number:", unit_number_input),
            ("Floor Number:", floor_number_input),
            ("Rent Amount:", rent_amount_input),
            ("Status:", status_input),
            ("Unit Type:", unit_type_input),
        ]

        for text, widget in labels:
            label = QLabel(text)
            label.setFont(label_font)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)  # Aligning text to right
            layout.addRow(label, widget)

        # Styled Save button
        save_button = QPushButton("Save")
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(lambda: self.add_unit(
            unit_number_input.text(),
            floor_number_input.value(),
            rent_amount_input.text(),
            status_input.currentText(),
            unit_type_input.currentText(),
            dialog
        ))

        layout.addRow("", save_button)  # Center align the save button

        dialog.setLayout(layout)
        dialog.exec()



    def add_unit(self, unit_number, floor_number, rent_amount, status, unit_type, dialog):
        """Add a new unit to the database while ensuring uniqueness per apartment."""
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Check if the unit number already exists for this apartment
            cursor.execute("""
                SELECT COUNT(*) FROM units WHERE apartment_id = %s AND unit_number = %s;
            """, (self.apartment_id, unit_number))
            (exists,) = cursor.fetchone()

            if exists > 0:
                QMessageBox.warning(self, "Duplicate Unit", 
                    "This unit number already exists for the selected apartment.")
                return  # Stop execution if duplicate exists

            # Insert new unit
            cursor.execute("""
                INSERT INTO units (apartment_id, unit_number, floor_number, rent_amount, status, unit_type)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (self.apartment_id, unit_number, floor_number, rent_amount, status, unit_type))
            conn.commit()

            # Close connections
            cursor.close()
            conn.close()

            # Reload the unit list
            self.load_units()
            dialog.accept()

        except psycopg2.Error as e:
            print(f"Database error: {e}")
            QMessageBox.critical(self, "Error", "Failed to add unit. Please try again.")


    def show_edit_unit_dialog(self, unit_id):
        """Display a styled dialog to edit an existing unit."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT unit_number, floor_number, rent_amount, status, unit_type
                FROM units
                WHERE id = %s;
            """, (unit_id,))
            unit = cursor.fetchone()
            cursor.close()
            conn.close()
            if not unit:
                QMessageBox.warning(self, "Unit Not Found", f"No unit found with ID {unit_id}.")
                return
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while fetching the unit: {e}")
            return

        # Create Dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Unit")
        dialog.setFixedSize(550, 280)  # Same size as Add Unit dialog
        dialog.setStyleSheet("background-color: white;")

        layout = QFormLayout()
        layout.setHorizontalSpacing(50)  # Increased spacing between labels and inputs
        layout.setVerticalSpacing(10)  # Reduce vertical spacing for compactness

        # Define font and styles
        label_font = QFont("Arial", 12, QFont.Weight.Bold)

        label_style = """
            QLabel {
                background-color: black;
                color: gold;
                padding: 5px;
                border-radius: 5px;
                min-width: 140px;  
                max-width: 140px;
                min-height: 20px;  /* Ensuring all labels have the same height */
                max-height: 20px;
                text-align: right;
            }
        """
        field_style = """
            QLineEdit, QSpinBox, QComboBox {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid gray;
                border-radius: 5px;
                padding: 2px;  /* Reduced padding for height control */
                font-size: 11pt;
                min-width: 180px;
                max-width: 180px;
                min-height: 20px;  /* Matching the height of the labels */
                max-height: 20px;
            }
        """
        button_style = """
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
        """

        # Create input fields
        unit_number_input = QLineEdit(unit[0])
        floor_number_input = QSpinBox()
        floor_number_input.setValue(unit[1])
        rent_amount_input = QLineEdit(str(unit[2]))
        status_input = QComboBox()
        status_input.addItems(["available", "occupied", "under maintenance"])
        status_input.setCurrentText(unit[3])
        unit_type_input = QComboBox()
        unit_type_input.addItems(["studio", "one_bedroom", "two_bedroom", "three_bedroom"])
        unit_type_input.setCurrentText(unit[4])

        # Apply styles
        for widget in [unit_number_input, floor_number_input, rent_amount_input, status_input, unit_type_input]:
            widget.setStyleSheet(field_style)

        # Create labels and ensure uniform size
        labels = [
            ("Unit Number:", unit_number_input),
            ("Floor Number:", floor_number_input),
            ("Rent Amount:", rent_amount_input),
            ("Status:", status_input),
            ("Unit Type:", unit_type_input),
        ]

        for text, widget in labels:
            label = QLabel(text)
            label.setFont(label_font)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)  # Aligning text to right
            layout.addRow(label, widget)

        # Styled Update button
        save_button = QPushButton("Update")
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(lambda: self.update_unit(
            unit_id, unit_number_input.text(), floor_number_input.value(),
            rent_amount_input.text(), status_input.currentText(),
            unit_type_input.currentText(), dialog
        ))

        layout.addRow("", save_button)  # Center align the button

        dialog.setLayout(layout)
        dialog.exec()


    def update_unit(self, unit_id, unit_number, floor_number, rent_amount, status, unit_type, dialog):
        """Update an existing unit in the database."""
        if not unit_number or not rent_amount:
            QMessageBox.warning(self, "Input Error", "Unit number and rent amount are required.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE units
                SET unit_number = %s, floor_number = %s, rent_amount = %s, status = %s, unit_type = %s
                WHERE id = %s;
            """, (unit_number, floor_number, rent_amount, status, unit_type, unit_id))
            conn.commit()
            cursor.close()
            conn.close()
            self.load_units()
            dialog.accept()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update unit: {e}")

    def go_back(self):
        from views.property_management import PropertiesPage  # Import inside the function
        self.property_management = PropertiesPage()
        self.property_management.show()
        self.close()

    def toggle_filter_panel(self):
        if self.filter_panel.isVisible():
            self.filter_panel.hide()
        else:
            self.filter_panel.show()


    def apply_filter(self):
        selected_status = []
        selected_unit_types = []

        # **Get Selected Status Filters**
        if self.available_checkbox.isChecked():
            selected_status.append("available")
        if self.occupied_checkbox.isChecked():
            selected_status.append("occupied")
        if self.maintenance_checkbox.isChecked():
            selected_status.append("under maintenance")

        # **Get Selected Unit Type Filters**
        if self.studio_checkbox.isChecked():
            selected_unit_types.append("studio")
        if self.one_bedroom_checkbox.isChecked():
            selected_unit_types.append("one_bedroom")
        if self.two_bedroom_checkbox.isChecked():
            selected_unit_types.append("two_bedroom")

        # **Load Filtered Data into Table**
        self.load_filtered_data(selected_status, selected_unit_types)


    def load_filtered_data(self, selected_status, selected_unit_types):
        """Fetch and display filtered units based on user selections."""
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Build the SQL query dynamically based on selected filters
            query = """
                SELECT id, unit_number, floor_number, rent_amount, status, unit_type
                FROM units
                WHERE apartment_id = %s
            """
            params = [self.apartment_id]

            if selected_status:
                query += " AND status IN %s"
                params.append(tuple(selected_status))

            if selected_unit_types:
                query += " AND unit_type IN %s"
                params.append(tuple(selected_unit_types))

            cursor.execute(query, params)
            filtered_units = cursor.fetchall()

            # Clear the table before displaying new filtered data
            self.units_table.setRowCount(len(filtered_units))

            for row_idx, unit in enumerate(filtered_units):
                unit_id, unit_number, floor_number, rent_amount, status, unit_type = unit
                self.units_table.setItem(row_idx, 0, QTableWidgetItem(unit_number))
                self.units_table.setItem(row_idx, 1, QTableWidgetItem(str(floor_number)))
                self.units_table.setItem(row_idx, 2, QTableWidgetItem(f"{rent_amount:.2f}"))
                self.units_table.setItem(row_idx, 3, QTableWidgetItem(status))
                self.units_table.setItem(row_idx, 4, QTableWidgetItem(unit_type))

                # Actions (Edit/Delete) - Keeping the same behavior as load_units()
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                edit_button = QPushButton("Edit")
                delete_button = QPushButton("Delete")

                edit_button.setStyleSheet("background-color: green; color: black;")
                delete_button.setStyleSheet("background-color: red; color: black;")

                edit_button.setFixedWidth(80)
                delete_button.setFixedWidth(80)

                edit_button.clicked.connect(lambda _, uid=unit_id: self.show_edit_unit_dialog(uid))
                delete_button.clicked.connect(lambda _, uid=unit_id: self.delete_unit(uid))

                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                actions_widget.setLayout(actions_layout)
                self.units_table.setCellWidget(row_idx, 5, actions_widget)

            cursor.close()
            conn.close()

            print(f"Displayed {len(filtered_units)} filtered units.")  # Debugging output

        except psycopg2.Error as e:
            print(f"Database error: {e}")


    def reset_filters(self):
        """Reset all filters and reload all units."""
        self.available_checkbox.setChecked(False)
        self.occupied_checkbox.setChecked(False)
        self.maintenance_checkbox.setChecked(False)

        self.studio_checkbox.setChecked(False)
        self.one_bedroom_checkbox.setChecked(False)
        self.two_bedroom_checkbox.setChecked(False)

        self.load_units()  # Reload all units


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UnitManagementPage()
    window.show()
    sys.exit(app.exec())
  