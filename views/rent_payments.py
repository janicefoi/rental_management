import sys
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLabel, QWidget, QTableWidget, QTableWidgetItem,
                            QSizePolicy, QDateEdit, QComboBox, QLineEdit, QApplication,
                             QDialog,QFormLayout, QCompleter, QMessageBox )
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import os
from PyQt6.QtWidgets import QMessageBox
import psycopg2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db 
from decimal import Decimal

class RentPaymentsPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Rent Payments")
        self.setGeometry(100, 100, 900, 600)  # Increased window width
        self.initUI()
        self.load_payments()

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

        # **Spacer to push buttons apart**
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

        top_button_layout.addWidget(back_button)
        top_button_layout.addWidget(spacer)
        top_button_layout.addWidget(filter_button)
        self.main_layout.addLayout(top_button_layout)

        # **Title Label**
        title_label = QLabel("Rent Payments Management")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: black;")
        self.main_layout.addWidget(title_label)

        # **Payments Table**
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(8)
        self.payments_table.setHorizontalHeaderLabels([
            "Tenant Name", "Unit", "Amount Paid", "Payment Date", "Method",
            "Receipt No.", "Status", "Late Fee"])
        self.payments_table.verticalHeader().setDefaultSectionSize(30)

        # Adjust column widths
        column_widths = [150, 120, 120, 120, 100, 150, 100, 100]
        for i, width in enumerate(column_widths):
            self.payments_table.setColumnWidth(i, width)

        self.payments_table.setStyleSheet("""
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
        
        self.main_layout.addWidget(self.payments_table)

        # **Record Payment Button**
        record_payment_button = QPushButton("Record Payment")
        record_payment_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        record_payment_button.setFixedSize(180, 40)
        record_payment_button.setStyleSheet("""
            QPushButton {
                background-color: gold;
                color: black;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: black;
                color: gold;
            }
        """)
        record_payment_button.clicked.connect(self.show_record_payment_dialog)
        self.main_layout.addWidget(record_payment_button, alignment=Qt.AlignmentFlag.AlignRight)

        # **Set Main Layout**
        container = QWidget()
        container.setStyleSheet("background-color: white;")
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def load_payments(self):
        """Load payments from the database into the table."""
        conn = connect_db()
        if not conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to the database.")
            return
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT t.full_name, u.unit_number, p.amount_paid, p.payment_date, 
                    p.payment_method, p.receipt_number, p.status, p.late_fee
                FROM payments p
                JOIN tenants t ON p.tenant_id = t.id
                LEFT JOIN units u ON t.unit_id = u.id
                ORDER BY p.payment_date DESC
            """
            cursor.execute(query)
            payments = cursor.fetchall()

            self.payments_table.setRowCount(0)  # Clear table
            for row_num, row_data in enumerate(payments):
                self.payments_table.insertRow(row_num)
                for col_num, col_data in enumerate(row_data):
                    self.payments_table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load payments: {e}")

        finally:
            conn.close()

    def show_record_payment_dialog(self):
        """Display a styled dialog to record a new payment."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Record Payment")
        dialog.setFixedSize(550, 360)
        dialog.setStyleSheet("background-color: white;")

        layout = QFormLayout()
        layout.setHorizontalSpacing(50)
        layout.setVerticalSpacing(10)

        label_font = QFont("Arial", 12, QFont.Weight.Bold)

        # Styling for Labels
        label_style = """
            QLabel {
                background-color: black;
                color: gold;
                padding: 5px;
                border-radius: 5px;
                min-width: 140px;  
                max-width: 140px;
                min-height: 20px;
                max-height: 20px;
                text-align: right;
            }
        """

        # Styling for Input Fields
        field_style = """
            QLineEdit, QDateEdit, QComboBox {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid gray;
                border-radius: 5px;
                padding: 5px;
                font-size: 11pt;
                min-width: 180px;
                max-width: 180px;
                min-height: 20px;
                max-height: 20px;
            }
        """

        # Styling for Button
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

        # **Tenant Dropdown with Searchable Capability**
        tenant_dropdown = QComboBox()
        tenant_dropdown.setEditable(True)  # Allows user to type and search
        
  
        # Populate dropdown with active tenants
        self.populate_tenant_dropdown(tenant_dropdown)

        # Other Input Fields
        amount_paid_input = QLineEdit()
        payment_date_input = QDateEdit()
        payment_date_input.setCalendarPopup(True)
        payment_method_input = QComboBox()
        payment_method_input.addItems(["Cash", "Bank", "Mobile Money"])
        receipt_number_input = QLineEdit()
        status_input = QComboBox()
        status_input.addItems(["Paid", "Pending", "Overdue"])
        late_fee_input = QLineEdit("0.00")

        # Apply styling to all input fields
        for widget in [
            tenant_dropdown, amount_paid_input, payment_date_input,
            payment_method_input, receipt_number_input, status_input, late_fee_input
        ]:
            widget.setStyleSheet(field_style)

        # Form Layout
        fields = [
            ("Tenant:", tenant_dropdown),
            ("Amount Paid:", amount_paid_input),
            ("Payment Date:", payment_date_input),
            ("Payment Method:", payment_method_input),
            ("Receipt Number:", receipt_number_input),
            ("Status:", status_input),
            ("Late Fee:", late_fee_input),
        ]

        for text, widget in fields:
            label = QLabel(text)
            label.setFont(label_font)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            layout.addRow(label, widget)

        # Save Button
        save_button = QPushButton("Save")
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(lambda: self.add_payment(tenant_dropdown, amount_paid_input, 
                                                            payment_date_input, payment_method_input, 
                                                            receipt_number_input, status_input, late_fee_input,dialog))
        layout.addRow("", save_button)


        dialog.setLayout(layout)
        dialog.exec()

    def populate_tenant_dropdown(self, tenant_dropdown):
        """Fetch active tenants from DB and populate the dropdown with search capability, storing tenant_id."""
        conn = connect_db()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            query = """
                SELECT id, full_name FROM tenants 
                WHERE lease_end_date IS NULL OR lease_end_date > CURRENT_DATE
                ORDER BY full_name
            """
            cursor.execute(query)
            tenants = cursor.fetchall()

            tenant_dropdown.clear()
            tenant_names = []  # List to store names for QCompleter

            for tenant_id, full_name in tenants:
                tenant_dropdown.addItem(full_name, tenant_id)  # Store tenant_id as userData
                tenant_names.append(full_name)

            # Enable search with autocompletion
            completer = QCompleter(tenant_names)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            tenant_dropdown.setCompleter(completer)

        except Exception as e:
            print(f"Error populating tenant dropdown: {e}")
        finally:
            cursor.close()
            conn.close()

    def add_payment(self, tenant_dropdown, amount_paid_input, payment_date_input, 
                    payment_method_input, receipt_number_input, status_input, late_fee_input, dialog):
        """Insert a new payment record into the database and update invoice status accordingly."""
        try:
            conn = connect_db()
            cur = conn.cursor()

            # Get values from the form
            tenant_id = tenant_dropdown.currentData()  # Get tenant ID from dropdown
            amount_paid = float(amount_paid_input.text())
            payment_date = payment_date_input.date().toString("yyyy-MM-dd")
            payment_method = payment_method_input.currentText().lower()  # Convert to lowercase
            receipt_number = receipt_number_input.text()
            status = status_input.currentText().lower()  # Convert to lowercase if needed
            late_fee = float(late_fee_input.text())

            # Ensure required fields are not empty
            if not tenant_id or not amount_paid or not payment_date or not payment_method:
                QMessageBox.warning(self, "Error", "Please fill in all required fields.")
                return

            # Insert payment record
            query = """
            INSERT INTO payments (tenant_id, amount_paid, payment_date, 
                                payment_method, receipt_number, status, late_fee)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            cur.execute(query, (tenant_id, amount_paid, payment_date, 
                                payment_method, receipt_number, status, late_fee))

            payment_id = cur.fetchone()[0]

            # Find the most recent unpaid or partially paid invoice for this tenant
            cur.execute("""
                SELECT id, amount_due, late_fee, COALESCE(remaining_balance, amount_due + late_fee) 
                FROM invoices 
                WHERE tenant_id = %s AND status IN ('unpaid', 'partially_paid')
                ORDER BY invoice_date ASC LIMIT 1
            """, (tenant_id,))
            invoice = cur.fetchone()

            if invoice:
                invoice_id, amount_due, late_fee, remaining_balance = invoice
                total_due = remaining_balance  # Remaining amount due on the invoice

                # Calculate the new remaining balance after payment
                

                new_balance = total_due - Decimal(amount_paid)  # Convert amount_paid to Decimal


                if new_balance <= 0:  # Payment fully covers or overpays the invoice
                    cur.execute("""
                        UPDATE invoices 
                        SET status = 'paid', remaining_balance = 0 
                        WHERE id = %s
                    """, (invoice_id,))
                    print(f"✅ Invoice {invoice_id} marked as paid")
                else:  # Payment is partial, update remaining balance and mark as partially paid
                    cur.execute("""
                        UPDATE invoices 
                        SET status = 'partially_paid', remaining_balance = %s 
                        WHERE id = %s
                    """, (new_balance, invoice_id))
                    print(f"⚠️ Invoice {invoice_id} is now partially paid. Remaining balance: {new_balance}")

            conn.commit()
            cur.close()
            conn.close()

            self.load_payments()  # Refresh payments table
            dialog.accept()  # Close the dialog
            QMessageBox.information(self, "Success", "Payment recorded successfully.")

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save payment: {e}")
            print(self, "Database Error", f"Failed to save payment: {e}")

    def toggle_filter_panel(self):
        print("Toggle filter panel")  # Placeholder for filter functionality

    def go_back(self):
        from views.payment_management import PaymentManagementPage  # Import inside the function
        self.payment_management = PaymentManagementPage()
        self.payment_management.show()
        self.close()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RentPaymentsPage()
    window.show()
    sys.exit(app.exec())