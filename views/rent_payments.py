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
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
import subprocess
from functools import partial 
import platform
from datetime import date, datetime

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
                # Search Bar Layout
        search_layout = QHBoxLayout()
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search payments by tenant name, ID, contact, or email...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #1a1a1a;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 12px;
                color: #1a1a1a;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_payments)  # 🔥 Connect search bar to filtering function

        # Add elements to layout
        search_layout.addWidget(left_spacer)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(right_spacer)

        # Add search bar layout to main layout
        self.main_layout.addLayout(search_layout)

        # **Payments Table**
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(9)
        self.payments_table.setHorizontalHeaderLabels([
            "Tenant Name", "Unit", "Amount Paid", "Payment Date", "Method",
            "Receipt No.", "Status","Actions", "Send Receipt"])
        self.payments_table.verticalHeader().setDefaultSectionSize(30)

        # Adjust column widths
        column_widths = [150, 120, 120, 120, 100, 150, 100, 150, 120]
        for i, width in enumerate(column_widths):
            self.payments_table.setColumnWidth(i, width)

        self.payments_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #1a1a1a;
                border-radius: 10px;
                padding: 10px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
                color: black;
            }
            QTableWidget::item:selected {
                background-color: #FFD700;
                color: #1a1a1a;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #FFD700;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
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
        """Load payments from the database into the table with action buttons."""
        conn = connect_db()
        if not conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to the database.")
            return
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT p.id, t.full_name, u.unit_number, p.amount_paid, p.payment_date, 
                    p.payment_method, p.receipt_number, p.status
                FROM payments p
                JOIN tenants t ON p.tenant_id = t.id
                LEFT JOIN units u ON t.unit_id = u.id
                ORDER BY p.payment_date DESC
            """
            cursor.execute(query)
            payments = cursor.fetchall()

            self.payments_table.setRowCount(0)  # Clear table
            for row_num, row_data in enumerate(payments):
                payment_id = row_data[0]  # Extract Payment ID
                self.payments_table.insertRow(row_num)

                # Fill table cells (Skipping payment_id column)
                for col_num, col_data in enumerate(row_data[1:]):
                    self.payments_table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
                
                # Create a QWidget container for the action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)

                # Download Button
                download_button = QPushButton("Download")
                download_button.setStyleSheet("background-color: black; color: gold;")
                download_button.clicked.connect(partial(self.download_receipt, payment_id))

                # Print Button
                print_button = QPushButton("Print")
                print_button.setStyleSheet("background-color: gold; color: black;")
                print_button.clicked.connect(partial(self.print_receipt, payment_id))

                # Add buttons to layout
                action_layout.addWidget(download_button)
                action_layout.addWidget(print_button)

                # Set the widget with buttons in the table
                self.payments_table.setCellWidget(row_num, 7, action_widget)  # Actions column (index 7)

                # **Send Receipt Button (Green)**
                send_receipt_button = QPushButton("Send Receipt")
                send_receipt_button.setStyleSheet("background-color: green; color: white;")
                send_receipt_button.clicked.connect(partial(self.send_receipt, payment_id))

                # Add the "Send Receipt" button in the last column (index 8)
                self.payments_table.setCellWidget(row_num, 8, send_receipt_button)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load payments: {e}")
        
        finally:
            conn.close()

    def show_record_payment_dialog(self):
        """Display a styled dialog to record a new payment."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Record Payment")
        dialog.setFixedSize(550, 300)  # Adjusted size since we removed two fields
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
        self.populate_tenant_dropdown(tenant_dropdown)  # Populate dropdown with active tenants

        # Other Input Fields
        amount_paid_input = QLineEdit()
        payment_date_input = QDateEdit()
        payment_date_input.setCalendarPopup(True)
        payment_date_input.setDate(date.today())  # Set default date
        payment_method_input = QComboBox()
        payment_method_input.addItems(["Cash", "Bank", "Mobile Money"])
        status_input = QComboBox()
        status_input.addItems(["Paid", "Pending", "Overdue"])

        # Apply styling to all input fields
        for widget in [tenant_dropdown, amount_paid_input, payment_date_input, payment_method_input, status_input]:
            widget.setStyleSheet(field_style)

        # Apply styling to calendar popup
        payment_date_input.calendarWidget().setStyleSheet("""
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

        # Form Layout (Without Receipt Number & Late Fee)
        fields = [
            ("Tenant:", tenant_dropdown),
            ("Amount Paid:", amount_paid_input),
            ("Payment Date:", payment_date_input),
            ("Payment Method:", payment_method_input),
            ("Status:", status_input),
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
        save_button.clicked.connect(lambda: self.add_payment(
            tenant_dropdown, amount_paid_input, payment_date_input, 
            payment_method_input, status_input, dialog  # Removed receipt_number_input & late_fee_input
        ))
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
                    payment_method_input, status_input, dialog):
        try:
            conn = connect_db()
            cur = conn.cursor()

            # Get values from the form
            tenant_id = tenant_dropdown.currentData()
            amount_paid = Decimal(amount_paid_input.text())
            payment_date = payment_date_input.date().toString("yyyy-MM-dd")
            payment_method = payment_method_input.currentText().lower()
            status = status_input.currentText().lower()

            if not all([tenant_id, amount_paid, payment_date, payment_method]):
                QMessageBox.warning(self, "Error", "Please fill in all required fields.")
                return

            # Generate receipt number
            cur.execute("SELECT receipt_number FROM payments ORDER BY id DESC LIMIT 1")
            last_receipt = cur.fetchone()
            new_receipt = f"N{(int(last_receipt[0][1:]) + 1) if last_receipt else 1:03}"

            # Record the payment
            cur.execute("""
                INSERT INTO payments (tenant_id, amount_paid, payment_date, 
                                    payment_method, receipt_number, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (tenant_id, amount_paid, payment_date, payment_method, new_receipt, status))
            payment_id = cur.fetchone()[0]

            remaining_payment = amount_paid
            
            # Fetch all unpaid invoices ordered by date
            cur.execute("""
                SELECT id, amount_due, late_fee, remaining_balance, status 
                FROM invoices 
                WHERE tenant_id = %s AND status IN ('unpaid', 'partially_paid', 'overdue')
                ORDER BY invoice_date ASC
            """, (tenant_id,))
            unpaid_invoices = cur.fetchall()

            for invoice in unpaid_invoices:
                if remaining_payment <= 0:
                    break

                invoice_id, amount_due, late_fee, remaining_balance, inv_status = invoice
                total_due = amount_due + (late_fee or 0)
                current_balance = remaining_balance if remaining_balance is not None else total_due

                if remaining_payment >= current_balance:
                    # Full payment for this invoice
                    cur.execute("""
                        UPDATE invoices 
                        SET status = 'paid', remaining_balance = 0 
                        WHERE id = %s
                    """, (invoice_id,))
                    remaining_payment -= current_balance
                else:
                    # Partial payment
                    new_balance = current_balance - remaining_payment
                    cur.execute("""
                        UPDATE invoices 
                        SET status = 'partially_paid', remaining_balance = %s 
                        WHERE id = %s
                    """, (new_balance, invoice_id))
                    remaining_payment = 0

            # Store any remaining amount as credit
            if remaining_payment > 0:
                cur.execute("""
                    UPDATE tenants 
                    SET credit_balance = COALESCE(credit_balance, 0) + %s 
                    WHERE id = %s
                """, (remaining_payment, tenant_id))

            conn.commit()
            self.load_payments()
            dialog.accept()
            QMessageBox.information(self, "Success", "Payment recorded successfully.")
            self.generate_receipt_pdf(payment_id)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save payment: {e}")
            print(f"❌ Database Error: {e}")
        finally:
            if conn:
                conn.close()


   
    def generate_receipt_pdf(self, payment_id, save_path="receipts/"):
        """Generate a PDF receipt for the given payment_id."""
        conn = connect_db()
        cur = conn.cursor()

        # Fetch payment details
        cur.execute("""
            SELECT p.id, t.full_name, u.unit_number, a.id AS apartment_id, a.name AS apartment_name, 
                p.payment_date, p.amount_paid, p.payment_method
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.id
            JOIN units u ON t.unit_id = u.id
            JOIN apartments a ON u.apartment_id = a.id
            WHERE p.id = %s
        """, (payment_id,))
        payment = cur.fetchone()

        if not payment:
            print("Payment not found!")
            return None  

        (payment_id, tenant_name, unit_number, apartment_id, apartment_name, 
        payment_date, amount_paid, payment_method) = payment

        # Fetch payment details for the apartment
        cur.execute("""
            SELECT payment_mode, mpesa_paybill, mpesa_account_no, bank_account_no, bank_name
            FROM apartment_payment_methods 
            WHERE apartment_id = %s
            LIMIT 1
        """, (apartment_id,))
        payment_details = cur.fetchone()
        
        conn.close()

        # Determine payment method details
        if payment_details:
            payment_mode, mpesa_paybill, mpesa_account_no, bank_account_no, bank_name = payment_details
        else:
            payment_mode, mpesa_paybill, mpesa_account_no, bank_account_no, bank_name = None, None, None, None, None

        # PDF Generation
        pdf_filename = f"{save_path}receipt_{payment_id}.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=A4)
        width, height = A4

        # Add logo
        logo_path = "rental_image.png"
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, 40, height - 100, width=100, height=60)
        except Exception as e:
            print(f"Logo not found or error loading logo: {e}")

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, height - 80, "Payment Receipt")

        receipt_number = f"RCPT-{payment_date.strftime('%Y%m')}-{payment_id}"
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, height - 80, f"Receipt No: {receipt_number}")

        # Receipt details
        c.setFont("Helvetica", 12)
        details = [
            ("Apartment:", apartment_name),
            ("Tenant Name:", tenant_name),
            ("Unit:", unit_number),
            ("Payment Date:", str(payment_date)),
            ("Amount Paid:", f"KES {amount_paid}"),
            ("Payment Method:", payment_method)
        ]

        y_position = height - 150
        for label, value in details:
            c.drawString(50, y_position, f"{label} {value}")
            y_position -= 25

        # QR Code for payment confirmation
        qr_text = f"Payment Confirmed: {receipt_number} | Amount: KES {amount_paid}"
        qr = qrcode.make(qr_text)
        qr_path = f"{save_path}receipt_qr_{payment_id}.png"
        qr.save(qr_path)
        c.drawImage(qr_path, 400, y_position - 60, width=80, height=80)

        # Signature Section
        y_position -= 100
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, "Authorized Signature: ____________________________")
        y_position -= 20
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, y_position, "Landlord/Property Manager")

        # Footer
        y_position -= 40
        c.setFont("Helvetica", 10)
        c.drawString(50, y_position, "Managed by XYZ Properties | Phone: +254 700 123456 | Email: info@xyz.com")

        c.save()
        print(f"Receipt saved as {pdf_filename}")
        self.send_receipt(payment_id)
        return pdf_filename  # Return the generated PDF path

    def download_receipt(self, payment_id):
        """Generate and save the payment receipt as a PDF, then open it."""
        save_path = "receipts/"
        os.makedirs(save_path, exist_ok=True)  # Ensure the directory exists
        
        pdf_path = self.generate_receipt_pdf(payment_id, save_path)  # Generate the PDF
        
        if pdf_path:
            if os.name == "nt":  # Windows
                os.startfile(pdf_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", pdf_path])
            else:  # Linux
                subprocess.run(["xdg-open", pdf_path])
    
    def print_receipt(self, payment_id):
        """Print the receipt PDF directly after generating it."""
        save_path = "receipts/"
        os.makedirs(save_path, exist_ok=True)  # Ensure the directory exists
        
        pdf_path = self.generate_receipt_pdf(payment_id, save_path)  # Generate the PDF
        
        if pdf_path:
            system_os = platform.system()

            if system_os == "Windows":
                os.startfile(pdf_path, "print")
            elif system_os == "Darwin":  # macOS
                subprocess.run(["lp", pdf_path])
            elif system_os == "Linux":
                subprocess.run(["lp", pdf_path])
            else:
                print("Unsupported OS for direct printing.")

            print(f"Sent {pdf_path} to printer.")

    def send_receipt(self, payment_id):
        """Trigger the script to send a receipt via email."""
        try:
            subprocess.run(["python", "views/send_receipts.py", str(payment_id)], check=True)
            QMessageBox.information(self, "Success", "Receipt sent successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send receipt: {e}")

    def filter_payments(self):
        """Filters the tenants table based on the search input."""
        search_text = self.search_bar.text().strip().lower()

        for row in range(self.payments_table.rowCount()):
            row_matches = False  # Assume row doesn't match

            for col in range(self.payments_table.columnCount()):  # Include all columns
                item = self.payments_table.item(row, col)
                if item and search_text in item.text().strip().lower():
                    row_matches = True
                    break  # No need to check further if there's a match

            self.payments_table.setRowHidden(row, not row_matches)  # Hide rows that don't match

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