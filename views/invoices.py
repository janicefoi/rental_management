from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QSizePolicy, 
                             QWidget, QMessageBox, QTableWidgetItem, QPushButton, QApplication, QComboBox,QDateEdit,
                             QCheckBox,QLineEdit )
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt,  QDate
import os
import sys
from functools import partial 
import subprocess
import psycopg2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db 
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import psycopg2
import qrcode
import platform
from datetime import date, datetime
from decimal import Decimal

class InvoicesPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rent Invoices")
        self.setGeometry(100, 100, 900, 600)
        self.initUI()
        self.load_invoices()

    def initUI(self):
        self.main_layout = QVBoxLayout()

        # **Top Button Section (Back & Filter)**
        top_button_layout = QHBoxLayout()

        back_button = QPushButton("\u2190 Back")
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

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

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
                background-color: white;
                border: 2px solid #1a1a1a;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 12px;
                color: #1a1a1a;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_invoices)  # 🔥 Connect search bar to filtering function

        # Add elements to layout
        search_layout.addWidget(left_spacer)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(right_spacer)

        # Add search bar layout to main layout
        self.main_layout.addLayout(search_layout)

        # **Main Content Layout (Invoices Table + Filter Panel on Right)**
        self.content_layout = QHBoxLayout()

        # **Invoices Table**
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(9)
        self.invoices_table.setHorizontalHeaderLabels([
            "Tenant Name", "Unit", "Amount Due", "Remaining Balance", "Invoice Date", 
            "Due Date", "Status", "Late Fee", "Actions"
        ])
        self.invoices_table.verticalHeader().setDefaultSectionSize(30)

        # Set column widths
        column_widths = [150, 120, 120, 130, 120, 120, 100, 100, 150]
        for i, width in enumerate(column_widths):
            self.invoices_table.setColumnWidth(i, width)

        # Updated table styling
        self.invoices_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #1a1a1a;
                border-radius: 10px;
                padding: 5px;
                color: black;  /* Set default text color */
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
                color: black;  /* Ensure item text is black */
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
                color: black;  /* Keep text black on hover */
            }
        """)

        # **Filter Panel**
        self.filter_panel = QWidget()
        self.filter_panel.setFixedWidth(300)  # Panel Width (300px)
        self.filter_panel.setStyleSheet("background-color: black; border-left: 2px solid gold;")
        self.filter_panel.setVisible(False)  # Start hidden

        filter_layout = QVBoxLayout()
        filter_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        filter_title = QLabel("Filter Invoices")
        filter_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        filter_title.setStyleSheet("color: gold;")
        filter_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        filter_layout.addWidget(filter_title)

        date_label = QLabel("Filter by Date")
        date_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        date_label.setStyleSheet("color: white;")
        filter_layout.addWidget(date_label)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("color: gold; background-color: black;")
        self.start_date.setDate(QDate.currentDate().addMonths(-1))  # Start date = 1 month ago
        filter_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("color: gold; background-color: black;")
        self.end_date.setDate(date.today())
        filter_layout.addWidget(self.end_date)

        tenant_label = QLabel("Filter by Tenant")
        tenant_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        tenant_label.setStyleSheet("color: white;")
        filter_layout.addWidget(tenant_label)

        self.tenant_dropdown = QComboBox()
        self.tenant_dropdown.setStyleSheet("color: gold; background-color: black;")
        filter_layout.addWidget(self.tenant_dropdown)

        status_label = QLabel("Invoice Status")
        status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_label.setStyleSheet("color: white;")
        filter_layout.addWidget(status_label)

        self.unpaid_checkbox = QCheckBox("Unpaid")
        self.paid_checkbox = QCheckBox("Paid")
        self.partially_paid_checkbox = QCheckBox("Partially Paid")
        self.overdue_checkbox = QCheckBox("Overdue")
    
        for checkbox in [self.unpaid_checkbox, self.paid_checkbox,self.partially_paid_checkbox, self.overdue_checkbox]:
            checkbox.setStyleSheet("color: gold;")
            filter_layout.addWidget(checkbox)

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
        apply_button.clicked.connect(self.apply_filter_invoices)
        filter_layout.addWidget(apply_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.filter_panel.setLayout(filter_layout)

        # **Add Table First, then Filter Panel**
        self.content_layout.addWidget(self.invoices_table)
        self.content_layout.addWidget(self.filter_panel)

        self.main_layout.addLayout(self.content_layout)
                # **Generate Invoice Button**
        generate_invoice_button = QPushButton("Generate Invoice")
        generate_invoice_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        generate_invoice_button.setFixedSize(200, 40)
        generate_invoice_button.setStyleSheet("""
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
        generate_invoice_button.clicked.connect(self.generate_invoices)

        # **Send Invoices Button**
        send_invoices_button = QPushButton("Send Invoices")
        send_invoices_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        send_invoices_button.setFixedSize(200, 40)
        send_invoices_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: gold;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: gold;
                color: black;
            }
        """)
        send_invoices_button.clicked.connect(self.send_invoices)

        # **Buttons Layout**
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(generate_invoice_button)
        buttons_layout.addWidget(send_invoices_button)

        self.main_layout.addLayout(buttons_layout)
        # **Set Main Layout**
        container = QWidget()
        container.setStyleSheet("background-color: white;")
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def load_invoices(self):
            """Fetch invoices from the database and populate the table with status badges."""
            conn = None
            try:
                conn = connect_db()
                cur = conn.cursor()
                
                # Query to fetch invoices with tenant name and unit number
                query = """
                SELECT i.id, t.full_name, u.unit_number, i.amount_due, i.remaining_balance, 
                    i.invoice_date, i.due_date, i.status, i.late_fee
                FROM invoices i
                JOIN tenants t ON i.tenant_id = t.id
                JOIN units u ON t.unit_id = u.id
                ORDER BY i.due_date DESC;
                """
                cur.execute(query)
                invoices = cur.fetchall()

                # Clear existing table rows
                self.invoices_table.setRowCount(0)

                # Populate the table with fetched data
                for row_idx, row_data in enumerate(invoices):
                    invoice_id = row_data[0]  # Extract Invoice ID
                    self.invoices_table.insertRow(row_idx)

                    # Fill table cells (Skipping invoice_id column)
                    for col_idx, value in enumerate(row_data[1:]):  # Exclude invoice_id
                        if col_idx == 6:  # "Status" column (7th in query, 6th in table)
                            status_button = QPushButton(str(value).capitalize())  # Create a QPushButton
                            status_button.setEnabled(False)  # Make it non-clickable
                            
                            # Apply styling based on status
                            status_styles = {
                                "paid": "background-color: #90EE90; color: black;",  # Light Green
                                "unpaid": "background-color: #FFB6C1; color: black;",  # Light Pink/Red
                                "overdue": "background-color: #FF8C00; color: white;",  # Dark Orange
                                "partially_paid": "background-color: #FFFF66; color: black;",  # Yellow
                            }
                            status_button.setStyleSheet(f"""
                                {status_styles.get(value.lower(), "background-color: gray; color: white;")}
                                border-radius: 10px;
                                padding: 2px 8px;
                                font-weight: bold;
                                border: none;
                                margin: 2px;
                                min-height: 20px;
                                max-height: 25px;
                            """)

                            self.invoices_table.setCellWidget(row_idx, col_idx, status_button)  # Add button to table
                        else:
                            item = QTableWidgetItem(str(value))
                            self.invoices_table.setItem(row_idx, col_idx, item)

                    # Create a QWidget container for both buttons
                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(0, 0, 0, 0)

                    # Download Button
                    download_button = QPushButton("Download")
                    download_button.setStyleSheet("background-color: black; color: gold;")
                    download_button.clicked.connect(partial(self.download_invoice, invoice_id))

                    # Print Button
                    print_button = QPushButton("Print")
                    print_button.setStyleSheet("background-color: gold; color: black;")
                    print_button.clicked.connect(partial(self.print_invoice, invoice_id))

                    # Add buttons to layout
                    action_layout.addWidget(download_button)
                    action_layout.addWidget(print_button)

                    # Set the widget with buttons in the table
                    self.invoices_table.setCellWidget(row_idx, 8, action_widget)  # Actions column (index 8)


                cur.close()
                conn.close()
            except Exception as e:
                print(f"Error loading invoices: {e}")
                if conn:
                    conn.close()

    def generate_invoices(self):
        """Generate invoices for all active tenants and apply any available credit."""
        conn = connect_db()
        if not conn:
            return

        try:
            cur = conn.cursor()
            today = QDate.currentDate()
            current_month = today.toString("yyyy-MM")

            cur.execute("""
                SELECT t.id AS tenant_id, t.full_name, u.rent_amount, t.credit_balance
                FROM tenants t
                JOIN units u ON t.unit_id = u.id
                WHERE t.lease_end_date IS NULL OR t.lease_end_date > CURRENT_DATE
            """)
            tenants = cur.fetchall()

            invoices_generated = 0
            save_path = "invoices/"
            os.makedirs(save_path, exist_ok=True)

            for tenant_id, tenant_name, rent_amount, credit_balance in tenants:
                cur.execute("""
                    SELECT id FROM invoices 
                    WHERE tenant_id = %s AND to_char(invoice_date, 'YYYY-MM') = %s
                """, (tenant_id, current_month))
                existing_invoice = cur.fetchone()

                if existing_invoice:
                    continue  # Skip if an invoice already exists

                due_date = today.addDays(7).toString("yyyy-MM-dd")

                # Deduct available credit from new invoice
                amount_due = max(0, rent_amount - credit_balance)

                # Insert invoice
                cur.execute("""
                    INSERT INTO invoices (tenant_id, invoice_date, due_date, amount_due, status)
                    VALUES (%s, CURRENT_DATE, %s, %s, %s) RETURNING id
                """, (tenant_id, due_date, amount_due, 'paid' if amount_due == 0 else 'unpaid'))

                invoice_id = cur.fetchone()[0]
                invoices_generated += 1

                # If credit was used, reduce credit balance
                new_credit_balance = max(0, credit_balance - rent_amount)
                cur.execute("""
                    UPDATE tenants SET credit_balance = %s WHERE id = %s
                """, (new_credit_balance, tenant_id))

                conn.commit()
                pdf_path=self.generate_invoice_pdf(invoice_id, save_path)

                if pdf_path:
                    print(f"📄 Invoice PDF generated: {pdf_path}")
                else:
                    print(f"⚠️ Failed to generate PDF for Invoice {invoice_id}")

            cur.close()
            conn.close()
            self.load_invoices()
            QMessageBox.information(self, "Invoices Generated", f"Generated {invoices_generated} new invoices.")

        except psycopg2.Error as e:
            print(f"❌ Database Error: {e}")
        
    def download_invoice(self, invoice_id):
        """Generate and save the invoice as a PDF, then open it."""
        save_path = "invoices/"
        os.makedirs(save_path, exist_ok=True)  # Ensure the directory exists
        
        pdf_path = self.generate_invoice_pdf(invoice_id, save_path)  # Generate the PDF
        
        if pdf_path:
            if os.name == "nt":  # Windows
                os.startfile(pdf_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", pdf_path])
            else:  # Linux
                subprocess.run(["xdg-open", pdf_path])

    def print_invoice(self, invoice_id):
        """Print the invoice PDF directly after generating it."""
        save_path = "invoices/"
        os.makedirs(save_path, exist_ok=True)  # Ensure the directory exists
        
        pdf_path = self.generate_invoice_pdf(invoice_id, save_path)  # Generate the PDF
        
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

    def generate_invoice_pdf(self, invoice_id, save_path="invoices/"):
        """Generate a PDF invoice for the given invoice_id with dynamic payment details."""
        conn = connect_db()
        cur = conn.cursor()

        # Fetch invoice details
        cur.execute("""
            SELECT i.id, t.full_name, u.unit_number, a.id AS apartment_id, a.name AS apartment_name, 
                i.invoice_date, i.due_date, i.amount_due, i.late_fee, i.status
            FROM invoices i
            JOIN tenants t ON i.tenant_id = t.id
            JOIN units u ON t.unit_id = u.id
            JOIN apartments a ON u.apartment_id = a.id
            WHERE i.id = %s
        """, (invoice_id,))
        invoice = cur.fetchone()

        if not invoice:
            print("Invoice not found!")
            return None  

        (invoice_id, tenant_name, unit_number, apartment_id, apartment_name, 
        invoice_date, due_date, amount_due, late_fee, status) = invoice

        # Fetch payment details for the apartment
        cur.execute("""
            SELECT payment_mode, mpesa_paybill, mpesa_account_no, bank_account_no, bank_name
            FROM apartment_payment_methods 
            WHERE apartment_id = %s
            LIMIT 1
        """, (apartment_id,))
        payment_details = cur.fetchone()
        
        conn.close()

        # Determine payment method
        if payment_details:
            payment_mode, mpesa_paybill, mpesa_account_no, bank_account_no, bank_name = payment_details
        else:
            payment_mode, mpesa_paybill, mpesa_account_no, bank_account_no, bank_name = None, None, None, None, None

        # PDF Generation
        pdf_filename = f"{save_path}invoice_{invoice_id}.pdf"
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
        c.drawString(200, height - 80, "Rental Invoice")

        invoice_number = f"INV-{invoice_date.strftime('%Y%m')}-{invoice_id}"
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, height - 80, f"Invoice No: {invoice_number}")

        # Invoice details
        c.setFont("Helvetica", 12)
        details = [
            ("Apartment:", apartment_name),
            ("Tenant Name:", tenant_name),
            ("Unit:", unit_number),
            ("Invoice Date:", str(invoice_date)),
            ("Due Date:", str(due_date)),
            ("Amount Due:", f"KES {amount_due}"),
            ("Late Fee:", f"KES {late_fee}"),
            ("Status:", status)
        ]

        y_position = height - 150
        for label, value in details:
            c.drawString(50, y_position, f"{label} {value}")
            y_position -= 25

        # Payment Instructions
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Payment Instructions:")
        c.setFont("Helvetica", 10)
        y_position -= 20

        if payment_mode == "Mpesa":
            c.drawString(50, y_position, "M-Pesa Payment:")
            y_position -= 15
            c.drawString(50, y_position, f"PayBill: {mpesa_paybill}")
            y_position -= 15
            c.drawString(50, y_position, f"Account No: {mpesa_account_no}")

            # Generate QR Code for M-Pesa payment
            qr_text = f"M-Pesa PayBill: {mpesa_paybill} | Acc: {mpesa_account_no}"
        
        elif payment_mode == "Bank":
            c.drawString(50, y_position, "Bank Payment:")
            y_position -= 15
            c.drawString(50, y_position, f"Bank Name: {bank_name}")
            y_position -= 15
            c.drawString(50, y_position, f"Account No: {bank_account_no}")

            # Generate QR Code for bank payment (optional)
            qr_text = f"Bank: {bank_name} | Acc: {bank_account_no}"
        
        else:
            c.drawString(50, y_position, "No payment details available.")
            qr_text = ""

        # Generate and add QR Code
        if qr_text:
            qr = qrcode.make(qr_text)
            qr_path = f"{save_path}invoice_qr_{invoice_id}.png"
            qr.save(qr_path)
            c.drawImage(qr_path, 400, y_position - 60, width=80, height=80)
        
        # Terms & Conditions
        y_position -= 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Terms & Conditions:")
        c.setFont("Helvetica", 10)
        terms = [
            "- Payments must be made by the due date to avoid penalties.",
            "- Late payments will incur a 5% penalty per month.",
            "- If payment is not received within 30 days, further action may be taken.",
            "- For disputes, please contact management within 7 days of invoice receipt."
        ]

        y_position -= 20
        for term in terms:
            c.drawString(50, y_position, term)
            y_position -= 15

        # Signature Section
        y_position -= 40
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
        print(f"Invoice saved as {pdf_filename}")
        return pdf_filename  # Return the generated PDF path

    def send_invoices(self):
        """Trigger the script to send invoices via email."""
        try:
            subprocess.run(["python", "views/send_invoices.py"], check=True)
            QMessageBox.information(self, "Success", "Invoices sent successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send invoices: {e}")

    def apply_filter_invoices(self):
        """Trigger invoice filtering based on selected criteria."""
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        tenant_id = self.tenant_dropdown.currentData()
        status_filter = []
        if self.unpaid_checkbox.isChecked():
            status_filter.append("unpaid")
        if self.paid_checkbox.isChecked():
            status_filter.append("paid")
        if self.partially_paid_checkbox.isChecked():
            status_filter.append("partially_paid")
        if self.overdue_checkbox.isChecked():
            status_filter.append("overdue")
        
        self.load_filtered_invoices(start_date, end_date, tenant_id, status_filter)

    def load_filtered_invoices(self, start_date, end_date, tenant_id, status_filter):
        """Fetch and display invoices based on selected filters with the same appearance as load_invoices."""
        conn = None
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Base query
            query = """
                SELECT invoices.id, tenants.full_name, units.unit_number, invoices.amount_due, invoices.remaining_balance,
                    invoices.invoice_date, invoices.due_date, invoices.status, invoices.late_fee
                FROM invoices
                JOIN tenants ON invoices.tenant_id = tenants.id
                JOIN units ON tenants.unit_id = units.id
                WHERE 1=1
            """
            params = []

            # **Filter by Date Range**
            if start_date and end_date:
                query += " AND invoices.invoice_date BETWEEN %s AND %s"
                params.extend([start_date, end_date])

            # **Filter by Tenant**
            if tenant_id:
                query += " AND tenants.id = %s"
                params.append(tenant_id)

            # **Filter by Invoice Status**
            if status_filter:
                query += " AND invoices.status IN ({})".format(",".join(["%s"] * len(status_filter)))
                params.extend(status_filter)

            # Order results
            query += " ORDER BY invoices.due_date DESC"

            # Execute query
            cursor.execute(query, params)
            filtered_invoices = cursor.fetchall()

            # Close DB connection
            conn.close()

            # **Update Table**
            self.invoices_table.setRowCount(0)  # Clear previous entries

            for row_idx, row_data in enumerate(filtered_invoices):
                invoice_id = row_data[0]  # Extract Invoice ID
                self.invoices_table.insertRow(row_idx)

                # Fill table cells (Skipping invoice_id column)
                for col_idx, value in enumerate(row_data[1:]):  # Exclude invoice_id
                    if col_idx == 6:  # "Status" column (7th in query, 6th in table)
                        status_button = QPushButton(str(value).capitalize())  # Create a QPushButton
                        status_button.setEnabled(False)  # Make it non-clickable

                        # Apply styling based on status
                        status_styles = {
                            "paid": "background-color: #90EE90; color: black;",  # Light Green
                            "unpaid": "background-color: #FFB6C1; color: black;",  # Light Pink/Red
                            "overdue": "background-color: #FF8C00; color: white;",  # Dark Orange
                            "partially_paid": "background-color: #FFFF66; color: black;",  # Yellow
                        }
                        status_button.setStyleSheet(f"""
                            {status_styles.get(value.lower(), "background-color: gray; color: white;")}
                            border-radius: 10px;
                            padding: 2px 8px;
                            font-weight: bold;
                            border: none;
                            margin: 2px;
                            min-height: 20px;
                            max-height: 25px;
                        """)

                        self.invoices_table.setCellWidget(row_idx, col_idx, status_button)  # Add button to table
                    else:
                        item = QTableWidgetItem(str(value))
                        self.invoices_table.setItem(row_idx, col_idx, item)

                # Create a QWidget container for action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)

                # Download Button
                download_button = QPushButton("Download")
                download_button.setStyleSheet("background-color: black; color: gold; border-radius: 5px;")
                download_button.clicked.connect(partial(self.download_invoice, invoice_id))

                # Print Button
                print_button = QPushButton("Print")
                print_button.setStyleSheet("background-color: gold; color: black; border-radius: 5px;")
                print_button.clicked.connect(partial(self.print_invoice, invoice_id))

                # Add buttons to layout
                action_layout.addWidget(download_button)
                action_layout.addWidget(print_button)

                # Set the widget with buttons in the table
                self.invoices_table.setCellWidget(row_idx, 8, action_widget)  # Actions column (index 8)

        except Exception as e:
            print(f"Error loading filtered invoices: {e}")
            if conn:
                conn.close()
    
    def apply_late_fees():
        """Check for overdue invoices and apply a fixed late fee."""
        conn = connect_db()
        if not conn:
            print("❌ Database connection failed.")
            return

        try:
            cur = conn.cursor()

            # Fetch the fixed late fee from settings (default: 1500 Ksh)
            cur.execute("SELECT value FROM settings WHERE key = 'late_fee_fixed'")
            late_fee_fixed = Decimal(cur.fetchone()[0]) if cur.rowcount else Decimal("1500.0")  

            # Get overdue invoices (unpaid and past due date) that have not had a late fee applied
            cur.execute("""
                SELECT id, tenant_id, amount_due, COALESCE(late_fee, 0) 
                FROM invoices 
                WHERE status = 'overdue' AND due_date < CURRENT_DATE
            """)
            overdue_invoices = cur.fetchall()

            for invoice_id, tenant_id, amount_due, existing_late_fee in overdue_invoices:
                # Only apply a new late fee if it hasn't been applied before
                if existing_late_fee == 0:
                    new_amount_due = amount_due + late_fee_fixed
                    new_late_fee = late_fee_fixed

                    # Update invoice amount, late_fee, and mark as overdue
                    cur.execute("""
                        UPDATE invoices 
                        SET amount_due = %s, late_fee = %s
                        WHERE id = %s
                    """, (new_amount_due, new_late_fee, invoice_id))

                    # Fetch tenant contact details
                    cur.execute("SELECT full_name, email FROM tenants WHERE id = %s", (tenant_id,))
                    tenant = cur.fetchone()
                    tenant_name, tenant_email = tenant if tenant else ("Unknown", None)

                    # Log application of late fee
                    print(f"[{datetime.now()}] 🏠 Late fee of {late_fee_fixed} applied to Invoice {invoice_id} for {tenant_name}.")

            conn.commit()
            cur.close()
            conn.close()
            print("✅ Late fee process completed.")

        except psycopg2.Error as e:
            print(f"⚠️ Database Error: {e}")

    def go_back(self):
        from views.payment_management import PaymentManagementPage  # Import inside the function
        self.payment_management = PaymentManagementPage()
        self.payment_management.show()
        self.close()

    def toggle_filter_panel(self):
        """Show/hide filter panel."""
        if self.filter_panel.isVisible():
            self.filter_panel.hide()
        else:
            self.filter_panel.show()

    def reset_filters(self):
        """Reset all filters and reload all invoices."""
        self.start_date.setDate(QDate.currentDate().addMonths(-1))  # Default to one month back
        self.end_date.setDate(QDate.currentDate())  # Default to today
        self.tenant_dropdown.setCurrentIndex(0)  # Reset tenant selection
        self.unpaid_checkbox.setChecked(False)
        self.paid_checkbox.setChecked(False)
        self.overdue_checkbox.setChecked(False)
        
        self.load_filtered_invoices(None, None, None, [])  # Reload all invoices

    def filter_invoices(self):
        """Filters the tenants table based on the search input."""
        search_text = self.search_bar.text().strip().lower()

        for row in range(self.invoices_table.rowCount()):
            row_matches = False  # Assume row doesn't match

            for col in range(self.invoices_table.columnCount()):  # Include all columns
                item = self.invoices_table.item(row, col)
                if item and search_text in item.text().strip().lower():
                    row_matches = True
                    break  # No need to check further if there's a match

            self.invoices_table.setRowHidden(row, not row_matches)  # Hide rows that don't match
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InvoicesPage()
    window.show()
    sys.exit(app.exec())