import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog,
    QFormLayout, QLineEdit, QComboBox, QMessageBox, QApplication,
    QSizePolicy, QCheckBox, QDateEdit,  QFileDialog,QPushButton,  QLineEdit, 
    QAbstractItemView
)
from PyQt6.QtCore import Qt,QDate
from PyQt6.QtGui import QFont
import psycopg2
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db
from datetime import date, datetime

class TenantManagementPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tenant Management")
        self.setGeometry(100, 100, 900, 600)
        self.initUI()
        self.load_tenants()
        self.unit_dropdown = QComboBox()

    def initUI(self):
        self.main_layout = QVBoxLayout()

        # **Top Button Section**
        top_button_layout = QHBoxLayout()

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

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        filter_button = QPushButton("Filter")
        filter_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        filter_button.setFixedSize(120, 40)
        filter_button.setStyleSheet("""
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
        filter_button.clicked.connect(self.toggle_filter_panel)

        reset_button = QPushButton("⟳")
        reset_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        reset_button.setFixedSize(40, 40)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: gold;
                border-radius: 20px;  /* Makes the button round */
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: gold;
                color: black;
            }
        """)
        reset_button.clicked.connect(self.reset_filters)

        top_button_layout.addWidget(back_button)
        top_button_layout.addWidget(spacer)
        top_button_layout.addWidget(filter_button)
        top_button_layout.addWidget(reset_button)

        self.main_layout.addLayout(top_button_layout)

        # **Title Label**
        title_label = QLabel("Tenant Management")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: black;")
        self.main_layout.addWidget(title_label)

        # Search Bar Layout
        search_layout = QHBoxLayout()
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search tenant by name, ID, contact, or email...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 2px solid #1a1a1a;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                color: #1a1a1a;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_tenants)  # 🔥 Connect search bar to filtering function

        # Add elements to layout
        search_layout.addWidget(left_spacer)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(right_spacer)

        # Add search bar layout to main layout
        self.main_layout.addLayout(search_layout)

        # **Tenants Table**
        self.tenants_table = QTableWidget()
        self.tenants_table.setColumnCount(11)  
        self.tenants_table.setHorizontalHeaderLabels(["Name", "ID Number", "Contact", "Email", "Unit", "Apartment", "Lease Start Date", "Lease End Date", "Credit Balance","Deposit", "Actions"])

        # Update table styling
        self.tenants_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #1a1a1a;
                border-radius: 15px;
            }
            QTableWidget::item {
                padding: 5px;  /* Reduced padding */
                border-bottom: 1px solid #e0e0e0;
                color: #1a1a1a;
            }
            QTableWidget::item:selected {
                background-color: #FFD700;
                color: #1a1a1a;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #FFD700;
                padding: 12px;
                border: none;
                font-weight: bold;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #1a1a1a;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #FFD700;
            }
        """)

        # Adjust column widths
        self.tenants_table.setColumnWidth(0, 150)
        self.tenants_table.setColumnWidth(1, 120)
        self.tenants_table.setColumnWidth(2, 120)
        self.tenants_table.setColumnWidth(3, 150)
        self.tenants_table.setColumnWidth(4, 70)
        self.tenants_table.setColumnWidth(5, 150)
        self.tenants_table.setColumnWidth(6, 150)
        self.tenants_table.setColumnWidth(7, 150)
        self.tenants_table.setColumnWidth(8, 120)  # Adjust for Credit Balance
        self.tenants_table.setColumnWidth(9, 120)  # Adjust for Credit Balance
        self.tenants_table.setColumnWidth(10, 200)  # Actions Column



         # **Sliding Filter Panel (Initially Hidden)**
        self.filter_panel = QWidget()
        self.filter_panel.setFixedWidth(300)  # Panel Width (300px)
        self.filter_panel.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-left: 2px solid #FFD700;
            }
            QLabel {
                color: #FFD700;
                font-weight: bold;
                font-size: 14px;
            }
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #FFD700;
                border-radius: 10px;
                padding: 5px;
                color: #1a1a1a;
            }
            QComboBox:hover {
                border: 2px solid #ffffff;
            }
            QCheckBox {
                color: #FFD700;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #FFD700;
                border-radius: 5px;
            }
            QCheckBox::indicator:checked {
                background-color: #FFD700;
            }
        """)

        filter_layout = QVBoxLayout()
        filter_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # **Filter Panel Title**
        filter_title = QLabel("Filter Tenants")
        filter_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        filter_title.setStyleSheet("color: gold;")
        filter_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        filter_layout.addWidget(filter_title)

        # **Apartment Filter**
        apartment_label = QLabel("Filter by Apartment")
        apartment_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        apartment_label.setStyleSheet("color: white;")
        filter_layout.addWidget(apartment_label)

        self.apartment_dropdown = QComboBox()
        self.apartment_dropdown.setStyleSheet("color: gold; background-color: black;")
        filter_layout.addWidget(self.apartment_dropdown)
        self.load_apartments()  # Call this after defining self.apartment_dropdown


        # **Lease Status Group**
        lease_status_label = QLabel("Lease Status")
        lease_status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lease_status_label.setStyleSheet("color: white;")
        filter_layout.addWidget(lease_status_label)

        self.active_lease_checkbox = QCheckBox("Active Leases")
        self.expired_lease_checkbox = QCheckBox("Expired Leases")

        for checkbox in [self.active_lease_checkbox, self.expired_lease_checkbox]:
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
        self.filter_panel.hide()  # Initially hidden

   
        # **Main Content Layout (Table & Filter Panel Side-by-Side)**
        self.content_layout = QHBoxLayout()
        self.content_layout.addWidget(self.tenants_table)
        self.content_layout.addWidget(self.filter_panel)

        self.main_layout.addLayout(self.content_layout)

        # **Add Tenant Button**
        add_tenant_button = QPushButton("Add Tenant")
        add_tenant_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        add_tenant_button.setStyleSheet("""
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
        add_tenant_button.clicked.connect(self.show_add_tenant_dialog)
        self.main_layout.addWidget(add_tenant_button, alignment=Qt.AlignmentFlag.AlignRight)

        # **Set Main Layout**
        container = QWidget()
        container.setLayout(self.main_layout)
        container.setStyleSheet("background-color: white;")  # Ensures a white background
        self.setCentralWidget(container)
        
    def load_tenants(self):
        """Load tenants into the table with Edit and Delete buttons."""
        self.tenants_table.setRowCount(0)  # Clear existing rows  
        self.tenants_table.verticalHeader().setDefaultSectionSize(35)     
        self.tenants_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tenants_table.cellDoubleClicked.connect(self.open_tenant_details)
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tenants.id, tenants.full_name, tenants.id_number, tenants.phone, tenants.email, 
                units.unit_number, apartments.name, tenants.lease_start_date, tenants.lease_end_date, tenants.credit_balance, tenants.deposit
            FROM tenants
            JOIN units ON tenants.unit_id = units.id
            JOIN apartments ON units.apartment_id = apartments.id
        """)

        tenants = cursor.fetchall()
        conn.close()
        
        
        for row_idx, tenant in enumerate(tenants):
            tenant_id, name, id_number, phone, email, unit_number, apartment_name, lease_start_date, lease_end_date, credit_balance,deposit = tenant

            
            self.tenants_table.insertRow(row_idx)
            self.tenants_table.setItem(row_idx, 0, QTableWidgetItem(name))
            self.tenants_table.setItem(row_idx, 1, QTableWidgetItem(id_number))
            self.tenants_table.setItem(row_idx, 2, QTableWidgetItem(phone))
            self.tenants_table.setItem(row_idx, 3, QTableWidgetItem(email))
            self.tenants_table.setItem(row_idx, 4, QTableWidgetItem(unit_number))  # Now showing unit_number
            self.tenants_table.setItem(row_idx, 5, QTableWidgetItem(apartment_name))
            self.tenants_table.setItem(row_idx, 6, QTableWidgetItem(str(lease_start_date)))
            self.tenants_table.setItem(row_idx, 7, QTableWidgetItem(str(lease_end_date) if lease_end_date else "Active"))
            self.tenants_table.setItem(row_idx, 8, QTableWidgetItem(f"Ksh {credit_balance:,.2f}"))  # Format as currency
            self.tenants_table.setItem(row_idx, 9, QTableWidgetItem(f"Ksh {deposit:,.2f}"))  # Format as currency
            # Actions Column (Edit/Delete Buttons)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")

            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #1a1a1a;
                    color: #FFD700;
                    border-radius: 8px;
                    font-weight: bold;
                    min-width: 55px;
                    max-width: 55px;
                    min-height: 20px;
                    max-height: 20px;
                    font-size: 10px;
                    margin: 0px;
                }
                QPushButton:hover {
                    background-color: #FFD700;
                    color: #1a1a1a;
                }
            """)
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #8B0000;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                    min-width: 55px;
                    max-width: 55px;
                    min-height: 20px;
                    max-height: 20px;
                    font-size: 10px;
                    margin: 0px;
                }
                QPushButton:hover {
                    background-color: #FF0000;
                    color: white;
                }
            """)

            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            actions_layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
            actions_layout.setSpacing(2)  # Minimal spacing
            actions_widget.setLayout(actions_layout)

            self.tenants_table.setCellWidget(row_idx, 10, actions_widget)

            # Connect buttons to their respective functions
            edit_button.clicked.connect(lambda _, idx=row_idx: self.show_edit_tenant_dialog(tenant_id))
            delete_button.clicked.connect(lambda _, idx=row_idx: self.delete_tenant(tenant_id)) 
            
    def go_back(self):
        from views.admin_dashboard import MainWindow
        self.admin_dashboard = MainWindow()
        self.admin_dashboard.show()
        self.close()
        
    def load_units(self, apartment_dropdown, unit_dropdown):
        """Loads only available units based on selected apartment."""
        unit_dropdown.clear()
        apartment_id = apartment_dropdown.currentData()

        if apartment_id is None or apartment_id == -1:
            return

        conn = connect_db()
        cursor = conn.cursor()
        
        # Fetch only units that are marked as "available"
        cursor.execute("""
            SELECT id, unit_number FROM units 
            WHERE apartment_id = %s AND status = 'available'
        """, (apartment_id,)) 

        available_units = cursor.fetchall()
        cursor.close()
        conn.close()

        if available_units:
            unit_dropdown.addItem("Select Unit", -1)  # Default option
            for unit in available_units:
                unit_dropdown.addItem(str(unit[1]), unit[0])  # Convert unit_number to string
        else:
            unit_dropdown.addItem("No available units", -1)  # Show if no units are available

    def add_tenant(self, full_name, phone, email, id_number,deposit, apartment_id, unit_id, lease_start_date, lease_end_date, lease_file_path, dialog):
        """Saves the new tenant to the database, updates the unit status, and refreshes the tables."""

        if not all([full_name, phone, email, id_number,deposit, apartment_id != -1, unit_id, lease_start_date]):
            QMessageBox.warning(None, "Missing Data", "Please fill in all required fields (Lease End Date is optional).")
            return

        lease_filename = os.path.basename(lease_file_path) if lease_file_path else ""

        if lease_file_path:
            lease_storage_path = os.path.join("leases", lease_filename)
            os.makedirs("leases", exist_ok=True)
            os.replace(lease_file_path, lease_storage_path)

        # Fix: Allow lease_end_date to be blank or None
        lease_end_date = lease_end_date if lease_end_date and lease_end_date != "2000-01-01" else None

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Insert tenant record (allows NULL for lease_end_date)
            cursor.execute("""
                INSERT INTO tenants (full_name, phone, email, id_number,deposit, unit_id, lease_start_date, lease_end_date, lease_agreement)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (full_name, phone, email, id_number,deposit, unit_id, lease_start_date, lease_end_date, lease_filename))

            # 🔥 Fix: Correct unit status logic
            today = datetime.today().date()
            
            if lease_end_date:  # If lease_end_date is provided
                lease_end_date = datetime.strptime(lease_end_date, "%Y-%m-%d").date()
                unit_status = "occupied" if lease_end_date > today else "available"
            else:
                unit_status = "occupied"  # If no lease_end_date, assume tenant is staying indefinitely
            
            # Debugging
            print(f"DEBUG: Updating unit {unit_id} to '{unit_status}'")

            # Update the unit's status
            cursor.execute("UPDATE units SET status = %s WHERE id = %s;", (unit_status, unit_id))

            conn.commit()  # ✅ Make sure this exists
            cursor.close()
            conn.close()

            QMessageBox.information(None, "Success", "Tenant added successfully!")
            dialog.accept()

            # Refresh UI
            self.load_tenants()
            self.load_units(self.apartment_dropdown, self.unit_dropdown)

        except psycopg2.Error as e:
            QMessageBox.critical(None, "Database Error", f"An error occurred: {e}")

    def show_add_tenant_dialog(self):
        """Display a styled dialog to add a new tenant."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Tenant")
        dialog.setFixedSize(600, 450)
        dialog.setStyleSheet("background-color: white;")

        layout = QFormLayout()
        layout.setHorizontalSpacing(50)
        layout.setVerticalSpacing(10)
        # Define styles
        label_font = QFont("Arial", 12, QFont.Weight.Bold)
        label_style = """
            QLabel {
                background-color: black;
                color: gold;
                padding: 5px;
                border-radius: 5px;
                min-width: 150px;
                max-width: 150px;
                text-align: right;
            }
        """
        field_style = """
            QLineEdit, QComboBox, QDateEdit {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid gray;
                border-radius: 5px;
                padding: 2px;
                font-size: 11pt;
                min-width: 200px;
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

        # Input fields
        full_name_input = QLineEdit()
        phone_input = QLineEdit()
        email_input = QLineEdit()
        id_number_input = QLineEdit()
        deposit_input = QLineEdit()

        lease_start_input = QDateEdit()
        lease_start_input.setCalendarPopup(True)
        lease_start_input.setStyleSheet(field_style)
        lease_start_input.setDate(date.today())  # Set default date

        lease_end_input = QDateEdit()
        lease_end_input.setCalendarPopup(True)
        lease_end_input.setStyleSheet(field_style)
        lease_end_input.setSpecialValueText("No End Date")  # Shows placeholder text
        lease_end_input.clear()  # Clears the default date
    
        apartment_dropdown = QComboBox()
        unit_dropdown = QComboBox()

        lease_file_path = QLineEdit()
        lease_file_path.setReadOnly(True)

        # Load apartments into dropdown
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM apartments")
        apartments = cursor.fetchall()
        cursor.close()
        conn.close()

        apartment_dropdown.addItem("Select Apartment", -1)
        for apt in apartments:
            apartment_dropdown.addItem(apt[1], apt[0])

        apartment_dropdown.currentIndexChanged.connect(lambda: self.load_units(apartment_dropdown, unit_dropdown))

        def browse_file():
            file_path, _ = QFileDialog.getOpenFileName(dialog, "Select Lease Agreement", "", "PDF Files (*.pdf)")
            if file_path:
                lease_file_path.setText(file_path)

        # Apply styles individually to prevent issues
        for widget in [
            full_name_input, phone_input, email_input, id_number_input,deposit_input,
            apartment_dropdown, unit_dropdown, lease_start_input, lease_end_input, lease_file_path
        ]:
            widget.setStyleSheet(field_style)

        # Apply styles to both calendar popups
        for calendar_widget in [lease_start_input.calendarWidget(), lease_end_input.calendarWidget()]:
            calendar_widget.setStyleSheet("""
                QCalendarWidget {
                    background-color: #1a1a1a;
                    color: white;
                    border: 2px solid #FFD700;
                    border-radius: 10px;
                }
                QCalendarWidget QWidget#qt_calendar_navigationbar {
                    background-color: #1a1a1a;
                    border-bottom: 2px solid #FFD700;
                }
                QCalendarWidget QComboBox {
                    background-color: #1a1a1a;
                    color: #FFD700;
                    border: 1px solid #FFD700;
                    border-radius: 5px;
                    padding: 5px;
                }
                QCalendarWidget QComboBox QAbstractItemView {
                    background-color: #1a1a1a;
                    color: #FFD700;
                    selection-background-color: #FFD700;
                    selection-color: #1a1a1a;
                }
                QCalendarWidget QToolButton {
                    background-color: #FFD700;
                    color: #1a1a1a;
                    border-radius: 5px;
                    padding: 5px;
                    min-width: 30px;
                    min-height: 30px;
                }
                QCalendarWidget QToolButton:hover {
                    background-color: white;
                    color: #1a1a1a;
                }
                QCalendarWidget QMenu {
                    background-color: #1a1a1a;
                    color: #FFD700;
                    border: 1px solid #FFD700;
                }
                QCalendarWidget QSpinBox {
                    background-color: #1a1a1a;
                    color: #FFD700;
                    border: 1px solid #FFD700;
                    border-radius: 5px;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    color: white;
                    background-color: #1a1a1a;
                    selection-background-color: #FFD700;
                    selection-color: #1a1a1a;
                }
                QCalendarWidget QTableView {
                    background-color: #1a1a1a;
                    color: white;
                    selection-background-color: #FFD700;
                    selection-color: #1a1a1a;
                    outline: none;
                }
                QCalendarWidget QTableView::item:hover {
                    background-color: rgba(255, 215, 0, 0.2);
                }
            """)

        # Create form layout
        labels = [
            ("Full Name:", full_name_input),
            ("Phone:", phone_input),
            ("Email:", email_input),
            ("ID Number:", id_number_input),
            ("Deposit:", deposit_input),
            ("Apartment:", apartment_dropdown),
            ("Unit:", unit_dropdown),
            ("Lease Start Date:", lease_start_input),
            ("Lease End Date:", lease_end_input),  # New lease end field
            ("Lease Agreement:", lease_file_path),
        ]
    
        for text, widget in labels:
            label = QLabel(text)
            label.setFont(label_font)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addRow(label, widget)
    
        # Browse button for lease file
        browse_button = QPushButton("Browse")
        browse_button.setStyleSheet(button_style)
        browse_button.clicked.connect(browse_file)
        layout.addRow("", browse_button)
        
        # Save button
        save_button = QPushButton("Save")
        save_button.setStyleSheet(button_style)  
        save_button.clicked.connect(lambda: self.add_tenant(
            full_name_input.text(),
            phone_input.text(),
            email_input.text(),
            id_number_input.text(),
            deposit_input.text(),
            int(apartment_dropdown.currentData()),
            int(unit_dropdown.currentData()),
            lease_start_input.date().toString("yyyy-MM-dd"),
            lease_end_input.date().toString("yyyy-MM-dd") if lease_end_input.date().isValid() else None,
            lease_file_path.text(),
            dialog,
        ))

        layout.addRow("", save_button)
        dialog.setLayout(layout)
        dialog.exec()

    def show_edit_tenant_dialog(self, tenant_id):
        """Display a dialog to edit tenant details, keeping the name uneditable."""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, phone, email, lease_start_date, lease_end_date FROM tenants WHERE id=%s", (tenant_id,))
        tenant = cursor.fetchone()
        conn.close()

        if not tenant:
            QMessageBox.warning(self, "Error", "Tenant not found.")
            return

        name, phone, email, lease_start, lease_end = tenant

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Tenant")
        dialog.setFixedSize(600, 350)
        dialog.setStyleSheet("background-color: white;")

        layout = QFormLayout()
        layout.setHorizontalSpacing(50)
        layout.setVerticalSpacing(10)

        # Define font and styles
        label_font = QFont("Arial", 12, QFont.Weight.Bold)

        label_style = """
            QLabel {
                background-color: black;
                color: gold;
                padding: 5px;
                border-radius: 5px;
                min-width: 150px;
                max-width: 150px;
                text-align: right;
            }
        """
        field_style = """
            QLineEdit, QComboBox, QDateEdit {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid gray;
                border-radius: 5px;
                padding: 2px;
                font-size: 11pt;
                min-width: 200px;
                max-width: 200px;
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

        # Input fields
        name_input = QLineEdit(name)
        name_input.setReadOnly(True)
        phone_input = QLineEdit(phone)
        email_input = QLineEdit(email)

        lease_start_input = QDateEdit()
        lease_start_input.setDate(QDate(lease_start.year, lease_start.month, lease_start.day))
        lease_start_input.setCalendarPopup(True)
        lease_start_input.setEnabled(False)  # Start date should not be edited

        lease_end_input = QDateEdit()
        if lease_end:
            lease_end_input.setDate(QDate(lease_end.year, lease_end.month, lease_end.day))
        lease_end_input.setCalendarPopup(True)

        # Apply styling
        for widget in [name_input, phone_input, email_input, lease_start_input, lease_end_input]:
            widget.setStyleSheet(field_style)

        # Apply styles to lease start and end date input
        lease_start_input.setStyleSheet("""
            QDateEdit {
                background-color: black;
                color: gold;
                border: 2px solid gold;
                border-radius: 5px;
                padding: 5px;
                font-size: 12pt;
            }
            QDateEdit::drop-down {
                width: 20px;
                border-left: 1px solid gold;
            }
        """)

        lease_end_input.setStyleSheet(lease_start_input.styleSheet())

    
        # Apply styles to both calendar popups
        for calendar_widget in [lease_start_input.calendarWidget(), lease_end_input.calendarWidget()]:
            calendar_widget.setStyleSheet("""
                QCalendarWidget {
                    background-color: #1a1a1a;
                    color: white;
                    border: 2px solid #FFD700;
                    border-radius: 10px;
                }
                QCalendarWidget QWidget#qt_calendar_navigationbar {
                    background-color: #1a1a1a;
                    border-bottom: 2px solid #FFD700;
                }
                QCalendarWidget QComboBox {
                    background-color: #1a1a1a;
                    color: #FFD700;
                    border: 1px solid #FFD700;
                    border-radius: 5px;
                    padding: 5px;
                }
                QCalendarWidget QComboBox QAbstractItemView {
                    background-color: #1a1a1a;
                    color: #FFD700;
                    selection-background-color: #FFD700;
                    selection-color: #1a1a1a;
                }
                QCalendarWidget QToolButton {
                    background-color: #FFD700;
                    color: #1a1a1a;
                    border-radius: 5px;
                    padding: 5px;
                    min-width: 30px;
                    min-height: 30px;
                }
                QCalendarWidget QToolButton:hover {
                    background-color: white;
                    color: #1a1a1a;
                }
                QCalendarWidget QMenu {
                    background-color: #1a1a1a;
                    color: #FFD700;
                    border: 1px solid #FFD700;
                }
                QCalendarWidget QSpinBox {
                    background-color: #1a1a1a;
                    color: #FFD700;
                    border: 1px solid #FFD700;
                    border-radius: 5px;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    color: white;
                    background-color: #1a1a1a;
                    selection-background-color: #FFD700;
                    selection-color: #1a1a1a;
                }
                QCalendarWidget QTableView {
                    background-color: #1a1a1a;
                    color: white;
                    selection-background-color: #FFD700;
                    selection-color: #1a1a1a;
                    outline: none;
                }
                QCalendarWidget QTableView::item:hover {
                    background-color: rgba(255, 215, 0, 0.2);
                }
            """)


        # Create labels
        labels = [
            ("Full Name:", name_input),
            ("Phone:", phone_input),
            ("Email:", email_input),
            ("Lease Start:", lease_start_input),
            ("Lease End:", lease_end_input),
        ]

        for text, widget in labels:
            label = QLabel(text)
            label.setFont(label_font)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addRow(label, widget)

        # Save button
        save_button = QPushButton("Save")
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(lambda: self.update_tenant(
            tenant_id,
            phone_input.text(),
            email_input.text(),
            lease_end_input.date().toString("yyyy-MM-dd"),
            dialog
        ))

        layout.addRow("", save_button)
        dialog.setLayout(layout)
        dialog.exec()

    def update_tenant(self, tenant_id, phone, email, lease_end, dialog):
        """Update tenant details in the database and adjust unit status if lease expired."""
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch current tenant's unit ID
        cursor.execute("SELECT unit_id FROM tenants WHERE id = %s", (tenant_id,))
        tenant = cursor.fetchone()
        
        if not tenant:
            QMessageBox.warning(self, "Error", "Tenant not found.")
            return
        
        unit_id = tenant[0]

        # Update tenant details
        cursor.execute("""
            UPDATE tenants 
            SET phone=%s, email=%s, lease_end_date=%s
            WHERE id=%s;
        """, (phone, email, lease_end, tenant_id))

        # 🔥 Fix: Handle lease_end_date properly
        today = datetime.today().date()
        if lease_end:  # If a lease_end_date is provided
            lease_end_date = datetime.strptime(lease_end, "%Y-%m-%d").date()
            
            if lease_end_date < today:  # Lease has expired
                cursor.execute("UPDATE units SET status = 'available' WHERE id = %s", (unit_id,))
            else:  # Lease is still active
                cursor.execute("UPDATE units SET status = 'occupied' WHERE id = %s", (unit_id,))
        else:
            # If lease_end_date is NULL, keep the unit as 'occupied'
            cursor.execute("UPDATE units SET status = 'occupied' WHERE id = %s", (unit_id,))

        conn.commit()
        conn.close()

        self.load_tenants()  # Refresh table
        self.load_units(self.apartment_dropdown, self.unit_dropdown)  # 🔄 Refresh available units
        dialog.accept()
        QMessageBox.information(self, "Success", "Tenant details updated successfully!")

    def toggle_filter_panel(self):
        """Show/hide filter panel."""
        if self.filter_panel.isVisible():
            self.filter_panel.hide()
        else:
            self.filter_panel.show()

    def load_apartments(self):
        """Load apartment names and IDs from the database into the dropdown."""
        self.apartment_dropdown.clear()  # Clear existing items

        # **Example Query (Adjust as needed for your DB)**
        query = "SELECT id, name FROM apartments"  # Modify based on your table structure
        connection = connect_db()  
        cursor = connection.cursor()

        cursor.execute(query)
        apartments = cursor.fetchall()

        # **Populate Dropdown**
        for apartment in apartments:
            apartment_id, apartment_name = apartment
            self.apartment_dropdown.addItem(apartment_name, apartment_id)  # Show name, store ID

        cursor.close()
        connection.close()

    def apply_filter(self):
        """Apply tenant filters based on selected apartment and lease status."""
        selected_apartment_id = self.apartment_dropdown.currentData()
        lease_status_filter = []

        # **Get Selected Lease Filters**
        if self.active_lease_checkbox.isChecked():
            lease_status_filter.append("active")
        if self.expired_lease_checkbox.isChecked():
            lease_status_filter.append("expired")

        self.load_filtered_tenants(selected_apartment_id, lease_status_filter)

    def load_filtered_tenants(self, selected_apartment_id, lease_status_filter):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            params = []
            today = date.today()

            query = """
                SELECT tenants.id, tenants.full_name, tenants.id_number, tenants.phone, tenants.email, 
                    units.unit_number, apartments.name, tenants.lease_start_date, tenants.lease_end_date, tenants.credit_balance, tenants.deposit
                FROM tenants
                JOIN units ON tenants.unit_id = units.id
                JOIN apartments ON units.apartment_id = apartments.id
                WHERE 1=1
            """

            # Add apartment filter if selected
            if selected_apartment_id:
                query += " AND apartments.id = %s"
                params.append(selected_apartment_id)

            # Add lease status filters
            if lease_status_filter:
                if "active" in lease_status_filter and "expired" in lease_status_filter:
                    # Both active and expired leases selected - no additional filter needed
                    pass
                elif "active" in lease_status_filter:
                    query += " AND (lease_end_date IS NULL OR lease_end_date > %s)"
                    params.append(today)
                elif "expired" in lease_status_filter:
                    query += " AND lease_end_date <= %s"
                    params.append(today)

            cursor.execute(query, params)
            filtered_tenants = cursor.fetchall()
            conn.close()

            self.tenants_table.setRowCount(0)  # Clear previous entries
            self.tenants_table.verticalHeader().setDefaultSectionSize(35)  # Match row height

            for row_idx, tenant in enumerate(filtered_tenants):
                tenant_id, name, id_number, phone, email, unit_number, apartment_name, lease_start_date, lease_end_date, credit_balance, deposit = tenant
                
                self.tenants_table.insertRow(row_idx)
                self.tenants_table.setItem(row_idx, 0, QTableWidgetItem(name))
                self.tenants_table.setItem(row_idx, 1, QTableWidgetItem(id_number))
                self.tenants_table.setItem(row_idx, 2, QTableWidgetItem(phone))
                self.tenants_table.setItem(row_idx, 3, QTableWidgetItem(email))
                self.tenants_table.setItem(row_idx, 4, QTableWidgetItem(unit_number))
                self.tenants_table.setItem(row_idx, 5, QTableWidgetItem(apartment_name))
                self.tenants_table.setItem(row_idx, 6, QTableWidgetItem(str(lease_start_date)))
                self.tenants_table.setItem(row_idx, 7, QTableWidgetItem(str(lease_end_date) if lease_end_date else "Active"))
                self.tenants_table.setItem(row_idx, 8, QTableWidgetItem(f"Ksh {credit_balance:,.2f}"))  # Add credit balance
                self.tenants_table.setItem(row_idx, 9, QTableWidgetItem(f"Ksh {deposit:,.2f}"))  # Add credit balance

                # Actions Column (Edit/Delete Buttons) with matching style
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                edit_button = QPushButton("Edit")
                delete_button = QPushButton("Delete")

                edit_button.setStyleSheet("""
                    QPushButton {
                        background-color: #1a1a1a;
                        color: #FFD700;
                        border-radius: 8px;
                        font-weight: bold;
                        min-width: 55px;
                        max-width: 55px;
                        min-height: 20px;
                        max-height: 20px;
                        font-size: 10px;
                        margin: 0px;
                    }
                    QPushButton:hover {
                        background-color: #FFD700;
                        color: #1a1a1a;
                    }
                """)
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #8B0000;
                        color: white;
                        border-radius: 8px;
                        font-weight: bold;
                        min-width: 55px;
                        max-width: 55px;
                        min-height: 20px;
                        max-height: 20px;
                        font-size: 10px;
                        margin: 0px;
                    }
                    QPushButton:hover {
                        background-color: #FF0000;
                        color: white;
                    }
                """)

                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                actions_layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
                actions_layout.setSpacing(2)  # Minimal spacing
                actions_widget.setLayout(actions_layout)

                self.tenants_table.setCellWidget(row_idx, 10, actions_widget)

                edit_button.clicked.connect(lambda _, tid=tenant_id: self.show_edit_tenant_dialog(tid))
                delete_button.clicked.connect(lambda _, tid=tenant_id: self.delete_tenant(tid))

        except psycopg2.Error as e:
            print(f"Database error: {e}")
    
    def filter_tenants(self):
        """Filters the tenants table based on the search input."""
        search_text = self.search_bar.text().strip().lower()

        for row in range(self.tenants_table.rowCount()):
            row_matches = False  # Assume row doesn't match

            for col in range(self.tenants_table.columnCount()):  # Include all columns
                item = self.tenants_table.item(row, col)
                if item and search_text in item.text().strip().lower():
                    row_matches = True
                    break  # No need to check further if there's a match

            self.tenants_table.setRowHidden(row, not row_matches)  # Hide rows that don't match

    def reset_filters(self):
        """Reset all filters and reload all tenants."""
        self.apartment_dropdown.setCurrentIndex(0)
        self.active_lease_checkbox.setChecked(False)
        self.expired_lease_checkbox.setChecked(False)
        self.load_tenants()

    def open_tenant_details(self, row, column):
        tenant_id_item = self.tenants_table.item(row, 0)
        if tenant_id_item is None:
            return
        
        # Retrieve tenant_id based on row from previously loaded data
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tenants.id
            FROM tenants
            JOIN units ON tenants.unit_id = units.id
            JOIN apartments ON units.apartment_id = apartments.id
            LIMIT 1 OFFSET %s
        """, (row,))
        tenant_data = cursor.fetchone()
        conn.close()

        if tenant_data:
            tenant_id = tenant_data[0]
            from views.tenant_details import TenantDetailsPage
            self.details_window = TenantDetailsPage(tenant_id)
            self.details_window.show()
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TenantManagementPage()
    window.show()
    sys.exit(app.exec())
