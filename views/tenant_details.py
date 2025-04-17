from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QFrame, QScrollArea
)
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db
from functools import partial 
import subprocess
import platform


class TenantDetailsPage(QWidget):
    def __init__(self, tenant_id, go_back_callback=None):
        super().__init__()
        self.tenant_id = tenant_id
        self.go_back_callback = go_back_callback
        self.setWindowTitle("Tenant Details")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: white;")
        
        # Define styles as instance variables
        self.table_style = """
            QTableWidget {
                background-color: white;
                color: #1a1a1a;
                border: 2px solid #1a1a1a;
                border-radius: 12px;
                gridline-color: #e0e0e0;
                padding: 10px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #FFD700;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: rgba(255, 215, 0, 0.2);
                color: #1a1a1a;
            }
        """

        self.section_header_style = """
            QLabel {
                color: #1a1a1a;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 0px;
                border-bottom: 2px solid #FFD700;
                margin-bottom: 10px;
            }
        """

        self.profile_style = """
            QLabel#profile_pic {
                background-color: #f5f5f5;
                border: 3px solid #1a1a1a;
                border-radius: 75px;
            }
            QLabel#name {
                color: #1a1a1a;
                font-size: 18px;
                font-weight: bold;
                margin-top: 10px;
            }
            QLabel#apartment {
                color: #666666;
                font-size: 14px;
            }
        """

        self.button_style = """
            QPushButton {
                background-color: #FFD700;
                color: #1a1a1a;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 120px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
                color: #FFD700;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """

        self.status_style = """
            QLabel#active {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
            }
            QLabel#expired {
                background-color: #f44336;
                color: white;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
            }
        """
        
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Add back the top bar layout
        top_bar_layout = QHBoxLayout()
        
        back_button = QPushButton("← Back")
        back_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        back_button.setFixedSize(130, 45)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #FFD700;
                border-radius: 12px;
                padding: 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #1a1a1a;
            }
        """)
        back_button.clicked.connect(self.go_back)

        self.title_label = QLabel("Tenant Details")
        self.title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            color: #1a1a1a;
            padding: 10px;
            font-size: 18px;
        """)

        top_bar_layout.addWidget(back_button)
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(self.title_label)
        top_bar_layout.addStretch(1)

        self.main_layout.addLayout(top_bar_layout)

        # Modern container styling
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
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

        # Create main container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(25)
        container_layout.setContentsMargins(30, 30, 30, 30)

        # Add your existing widgets to container_layout
        self.tenant_details_widget = QWidget()
        self.tenant_details_layout = QVBoxLayout(self.tenant_details_widget)
        self.tenant_details_widget.setStyleSheet("background-color: transparent; border: none;")
        container_layout.addWidget(self.tenant_details_widget)

        self.invoice_widget = QWidget()
        self.invoice_layout = QVBoxLayout(self.invoice_widget)
        self.invoice_widget.setStyleSheet("background-color: transparent; border: none;")
        container_layout.addWidget(self.invoice_widget)

        self.payments_widget = QWidget()
        self.payments_layout = QVBoxLayout(self.payments_widget)
        self.payments_widget.setStyleSheet("background-color: transparent; border: none;")
        container_layout.addWidget(self.payments_widget)

        # Set the container as the scroll area widget
        scroll.setWidget(container)

        # Add scroll area to main layout
        self.main_layout.addWidget(scroll)
        self.setLayout(self.main_layout)

        # Load the data
        self.load_tenant_details()
        self.load_invoices()
        self.load_payments()
  
    def go_back(self):
        from views.tenant_management import TenantManagementPage  
        self.tenant_management = TenantManagementPage()
        self.tenant_management.show()
        self.close()

    def load_tenant_details(self):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.full_name, t.phone, t.email, t.id_number, t.credit_balance,t.deposit, t.lease_start_date, 
                t.lease_end_date, t.lease_agreement, u.unit_number, a.name
            FROM tenants t
            JOIN units u ON t.unit_id = u.id
            JOIN apartments a ON u.apartment_id = a.id
            WHERE t.id = %s
        """, (self.tenant_id,))
        result = cursor.fetchone()

        if result:
            (full_name, phone, email, id_number, credit_balance, deposit,
            lease_start, lease_end, lease_doc, unit_number, apt_name) = result

            self.title_label.setText(f"{full_name}'s Details")

            # Create section header
            header = QLabel("Personal Information")
            header.setStyleSheet(self.section_header_style)
            self.tenant_details_layout.addWidget(header)

            # Main info container
            tenant_info_layout = QHBoxLayout()

            # Left Column (Profile)
            left_column = QVBoxLayout()
            
            profile_pic = QLabel()
            profile_pic.setFixedSize(150, 150)
            profile_pic.setObjectName("profile_pic")
            profile_pic.setStyleSheet(self.profile_style)
            profile_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            profile_pic.setText("👤")

            name_label = QLabel(full_name)
            name_label.setObjectName("name")
            name_label.setStyleSheet(self.profile_style)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            apartment_label = QLabel(f"{apt_name} - Unit {unit_number}")
            apartment_label.setObjectName("apartment")
            apartment_label.setStyleSheet(self.profile_style)
            apartment_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            left_column.addWidget(profile_pic, alignment=Qt.AlignmentFlag.AlignHCenter)
            left_column.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignHCenter)
            left_column.addWidget(apartment_label, alignment=Qt.AlignmentFlag.AlignHCenter)
            left_column.addStretch()

            # Middle Column (Contact Info)
            middle_column = QVBoxLayout()
            
            info_container = QWidget()
            info_container.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    border-radius: 15px;
                    padding: 20px;
                }
            """)
            info_layout = QVBoxLayout(info_container)

            for label_text, value_text in [
                ("Email", email),
                ("Phone", phone),
                ("ID Number", id_number),
                ("Credit Balance", f"Ksh {credit_balance:,.2f}"),
                ("Deposit", f"Ksh {deposit:,.2f}")
            ]:
                row = QHBoxLayout()
                label = QLabel(f"{label_text}:")
                label.setStyleSheet("""
                    QLabel {
                        color: #1a1a1a;
                        font-weight: bold;
                        font-size: 14px;
                        min-width: 120px;
                    }
                """)
                value = QLabel(value_text)
                value.setStyleSheet("""
                    QLabel {
                        color: #1a1a1a;
                        font-size: 14px;
                    }
                """)
                row.addWidget(label)
                row.addWidget(value)
                info_layout.addLayout(row)

            middle_column.addWidget(info_container)
            middle_column.addStretch()

            # Right Column (Lease Info)
            right_column = QVBoxLayout()
            
            lease_container = QWidget()
            lease_container.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    border-radius: 15px;
                    padding: 20px;
                }
            """)
            lease_layout = QVBoxLayout(lease_container)

            # Lease Status
            status_label = QLabel()
            status_label.setObjectName("active" if lease_end is None or lease_end >= date.today() else "expired")
            status_label.setText("Active Lease" if lease_end is None or lease_end >= date.today() else "Expired Lease")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_label.setStyleSheet(self.status_style)
            lease_layout.addWidget(status_label)

            # Lease Dates
            lease_dates = QLabel(f"Start: {lease_start.strftime('%B %d, %Y')}\n" +
                               (f"End: {lease_end.strftime('%B %d, %Y')}" if lease_end else "End: Ongoing"))
            lease_dates.setStyleSheet("""
                QLabel {
                    color: #1a1a1a;
                    font-size: 14px;
                    margin-top: 10px;
                    text-align: center;
                }
            """)
            lease_dates.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lease_layout.addWidget(lease_dates)

            # Lease Document
            if lease_doc:
                view_button = QPushButton("View Lease Agreement")
                view_button.setStyleSheet(self.button_style)
                view_button.clicked.connect(lambda: self.view_lease_agreement(lease_doc))
                lease_layout.addWidget(view_button)

                download_button = QPushButton("Download Lease")
                download_button.setStyleSheet(self.button_style)
                download_button.clicked.connect(lambda: self.download_lease_file(lease_doc))
                lease_layout.addWidget(download_button)
            else:
                no_lease_label = QLabel("No Lease Document")
                no_lease_label.setStyleSheet("color: #666666; text-align: center;")
                no_lease_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lease_layout.addWidget(no_lease_label)

            right_column.addWidget(lease_container)
            right_column.addStretch()

            # Add all columns to main layout
            tenant_info_layout.addLayout(left_column)
            tenant_info_layout.addLayout(middle_column)
            tenant_info_layout.addLayout(right_column)

            self.tenant_details_layout.addLayout(tenant_info_layout)

        cursor.close()


    def download_lease_file(self, filename):
        file_path = os.path.join("leases", filename) 
        if os.path.exists(file_path):
            system_os = platform.system()
            try:
                if system_os == "Windows":
                    os.startfile(file_path)
                elif system_os == "Darwin":  # macOS
                    subprocess.run(['open', file_path])
                elif system_os == "Linux":
                    subprocess.run(['xdg-open', file_path])
                else:
                    QMessageBox.warning(self, "Unsupported OS", "Your operating system is not supported.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open file: {str(e)}")
        else:
            QMessageBox.warning(self, "File Not Found", "The lease agreement file could not be found.")

    def view_lease_agreement(self, filename):
        file_path = os.path.join("leases", filename)
        if os.path.exists(file_path):
            system_os = platform.system()
            try:
                if system_os == "Windows":
                    os.startfile(file_path)
                elif system_os == "Darwin":  # macOS
                    subprocess.run(['open', file_path])
                elif system_os == "Linux":
                    subprocess.run(['xdg-open', file_path])
                else:
                    QMessageBox.warning(self, "Unsupported OS", "Your operating system is not supported.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open file: {str(e)}")
        else:
            QMessageBox.warning(self, "File Not Found", "The lease agreement file could not be found.")


    def load_invoices(self):
        invoice_header = QLabel("📊 Invoice History")
        invoice_header.setStyleSheet(self.section_header_style)
        self.invoice_layout.addWidget(invoice_header)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Invoice Date", "Due Date", "Amount Due", "Remaining Balance", 
            "Status",
        ])
        
        # Apply table styling
        table.verticalHeader().setVisible(False)
        table.setShowGrid(True)
        table.setStyleSheet(self.table_style)
        table.horizontalHeader().setStretchLastSection(True)
        table.setMinimumHeight(300)

        # Set column widths
        column_widths = [200, 200, 200, 200, 200]
        for i, width in enumerate(column_widths):
            table.setColumnWidth(i, width)

        self.invoice_layout.addWidget(table)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT invoice_date, due_date, amount_due, remaining_balance,
                       status, id
                FROM invoices 
                WHERE tenant_id = %s
                ORDER BY invoice_date DESC
            """, (self.tenant_id,))
            rows = cursor.fetchall()

            table.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                invoice_id = row_data[5]  # Get invoice ID from the last column
                for col_idx, value in enumerate(row_data[:-1]):  # Exclude ID from display
                    if col_idx == 4:  # Status column
                        status_label = QLabel(str(value).capitalize())
                        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        
                        status_styles = {
                            "paid": "background-color: #90EE90; color: black;",
                            "unpaid": "background-color: #FFB6C1; color: black;",
                            "overdue": "background-color: #FF8C00; color: white;",
                            "partially_paid": "background-color: #FFFF66; color: black;"
                        }
                        
                        status_label.setStyleSheet(f"""
                            {status_styles.get(value.lower(), "background-color: gray; color: white;")}
                                border-radius: 10px;
                                padding: 2px 8px;
                                font-weight: bold;
                                border: none;
                                margin: 2px;
                                min-height: 20px;
                                max-height: 25px;
                        """)
                        table.setCellWidget(row_idx, col_idx, status_label)
                    
                    elif col_idx in [2, 3]:  # Amount columns
                        formatted_value = f"Ksh {float(value):,.2f}" if value else "None"
                        item = QTableWidgetItem(formatted_value)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        table.setItem(row_idx, col_idx, item)
                    
                    elif col_idx in [0, 1]:  # Date columns
                        formatted_value = value.strftime('%Y-%m-%d') if value else ""
                        item = QTableWidgetItem(formatted_value)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        table.setItem(row_idx, col_idx, item)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Failed to load tenant invoices: {e}")

    def load_payments(self):
        payment_header = QLabel("💳 Payment History")
        payment_header.setStyleSheet(self.section_header_style)
        self.payments_layout.addWidget(payment_header)

        table = QTableWidget()
        table.setColumnCount(5)  # Updated column count
        table.setHorizontalHeaderLabels([
            "Amount Paid", "Payment Date", "Payment Method", 
            "Receipt No.", "Status"
        ])
        
        # Apply table styling
        table.verticalHeader().setVisible(False)
        table.setShowGrid(True)
        table.setStyleSheet(self.table_style)
        table.horizontalHeader().setStretchLastSection(True)
        table.setMinimumHeight(300)

        # Set column widths
        column_widths = [200, 200, 200, 200, 200]
        for i, width in enumerate(column_widths):
            table.setColumnWidth(i, width)

        self.payments_layout.addWidget(table)

        conn = connect_db()
        if not conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to the database.")
            return
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.amount_paid, p.payment_date, p.payment_method, 
                    p.receipt_number, p.status
                FROM payments p
                WHERE p.tenant_id = %s
                ORDER BY p.payment_date DESC
            """
            cursor.execute(query, (self.tenant_id,))
            payments = cursor.fetchall()

            table.setRowCount(0)  # Clear table
            for row_num, row_data in enumerate(payments):
                payment_id = row_data[0]  # Extract Payment ID
                table.insertRow(row_num)

                # Fill table cells (Skipping payment_id column)
                for col_num, col_data in enumerate(row_data[1:]):
                    if col_num == 0:  # Amount Paid column
                        formatted_value = f"Ksh {float(col_data):,.2f}" if col_data else "None"
                    elif col_num == 1:  # Payment Date column
                        formatted_value = col_data.strftime('%Y-%m-%d') if col_data else ""
                    else:
                        formatted_value = str(col_data) if col_data else ""
                    
                    item = QTableWidgetItem(formatted_value)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(row_num, col_num, item)
    

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load payments: {e}")
        
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    app = TenantDetailsPage(sys.argv)
    window = TenantDetailsPage()
    window.show()
    sys.exit(app.exec())