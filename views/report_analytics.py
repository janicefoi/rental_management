import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QSizePolicy, QApplication,
    QFrame, QComboBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db

class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_apartment_id = None
        self.setWindowTitle("Reports & Analytics")
        self.setGeometry(100, 100, 900, 600)  
        self.initUI()
        self.load_reports_data()

    def initUI(self):
        self.main_layout = QVBoxLayout()

        # **Top Button Section**
        top_button_layout = QHBoxLayout()

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

        title_label = QLabel("Rent Payments Reports Analytics")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: black;")

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
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: gold;
                color: black;
            }
        """)
        reset_button.clicked.connect(self.reset_filters)

        # **Top Layout: Back button, title centered, filter & reset on the right**
        top_button_layout.addWidget(back_button)
        top_button_layout.addStretch(1)  # Adds space before the title
        top_button_layout.addWidget(title_label)
        top_button_layout.addStretch(1)  # Adds space after the title
        top_button_layout.addWidget(filter_button)
        top_button_layout.addWidget(reset_button)

        self.main_layout.addLayout(top_button_layout)

        # **Report Cards Container**
        container = QWidget()
        container_layout = QVBoxLayout()

        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(15)  # Space between cards

        container_layout.addLayout(self.cards_layout)
        container.setLayout(container_layout)
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid black;
                border-radius: 10px;
                padding: 10px;
            }
        """)

         # **Sliding Filter Panel (Initially Hidden)**
        self.filter_panel = QWidget()
        self.filter_panel.setFixedWidth(300)  # Panel Width (300px)
        self.filter_panel.setStyleSheet("background-color: black; border-left: 2px solid gold;")

        filter_layout = QVBoxLayout()
        filter_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # **Filter Panel Title**
        filter_title = QLabel("Filter Reports")
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
        self.apartment_dropdown.addItem("All Apartments")
        filter_layout.addWidget(self.apartment_dropdown)
        self.load_apartments()  # Call this after defining self.apartment_dropdown

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

        
        # Horizontal layout to hold the container + filter panel
        content_layout = QHBoxLayout()
        content_layout.addWidget(container)
        content_layout.addWidget(self.filter_panel)

        # Add this horizontal layout to the main vertical layout
        self.main_layout.addLayout(content_layout)

        # **Set Main Layout**
        self.setLayout(self.main_layout)
        self.setStyleSheet("background-color: white;")  
    
    def load_reports_data(self):
        """Fetch and display financial insights per month, optionally filtered by apartment."""
        conn = connect_db()
        cur = conn.cursor()

        base_query = """
            WITH monthly_data AS (
                SELECT 
                    DATE_TRUNC('month', i.invoice_date) AS month_start,
                    TO_CHAR(i.invoice_date, 'Month YYYY') AS month,
                    COUNT(i.id) AS total_invoices,
                    COUNT(CASE WHEN i.status = 'overdue' THEN 1 END) AS overdue_invoices,
                    COUNT(CASE WHEN i.status = 'partially_paid' THEN 1 END) AS partially_paid,
                    COUNT(CASE WHEN i.status = 'unpaid' THEN 1 END) AS unpaid_invoices,
                    SUM(
                        CASE 
                            WHEN i.status = 'overdue' THEN i.amount_due + i.late_fee
                            WHEN i.status = 'partially_paid' THEN i.remaining_balance
                            WHEN i.status = 'unpaid' THEN i.amount_due
                            ELSE 0
                        END
                    ) AS total_remaining
                FROM invoices i
                JOIN tenants t ON i.tenant_id = t.id
                JOIN units u ON t.unit_id = u.id
                {where_clause}
                GROUP BY month_start, month
            ),
            payments_data AS (
                SELECT 
                    DATE_TRUNC('month', p.payment_date) AS month_start,
                    SUM(p.amount_paid) AS total_collected
                FROM payments p
                JOIN tenants t ON p.tenant_id = t.id
                JOIN units u ON t.unit_id = u.id
                {where_clause}
                GROUP BY month_start
            )
            SELECT 
                m.month, 
                COALESCE(p.total_collected, 0) AS total_collected,
                m.total_invoices,
                m.overdue_invoices,
                m.partially_paid,
                m.unpaid_invoices,
                m.total_remaining
            FROM monthly_data m
            LEFT JOIN payments_data p ON m.month_start = p.month_start
            ORDER BY m.month_start;
        """

        where_clause = ""
        params = ()

        if self.selected_apartment_id:
            where_clause = "WHERE u.apartment_id = %s"
            params = (self.selected_apartment_id, self.selected_apartment_id)

        query = base_query.format(where_clause=where_clause)

        data = []
        try:
            cur.execute(query, params)
            data = cur.fetchall()

            for i, row in enumerate(data):
                print(f"  Row {i}: {row} (Length: {len(row)})")

        except Exception as e:
            print(f"Error executing query: {e}")
        finally:
            conn.close()

        print(f"Fetched {len(data)} months of reports.")
        if not data:
            print("No report data found!")
            return

        self.create_monthly_cards(data)


    def create_monthly_cards(self, data):
        """Generate a summary card for each month dynamically."""

        # Clear previous cards
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        row, col = 0, 0  # Positioning in grid (3 cards per row)

        # Iterate over the data
        for i, row_data in enumerate(data):
            # Print each row to see the structure (debugging step)
            print(f"🧪 Row {i}: {row_data} (Length: {len(row_data)})")

            # Check if the row has exactly 7 elements
            if len(row_data) != 7:
                print(f"⚠️ Warning: Expected 7 elements but got {len(row_data)}. Skipping this row.")
                continue  # Skip this row if it's malformed

            # Unpack the 7 values from the row
            month, total_collected, total_invoices, overdue_invoices, partially_paid, unpaid_invoices, total_remaining = row_data
            print(f"🛠️ Creating card for {month.strip()} - Total Rent: {total_collected}")  

            card = QFrame()
            card.setStyleSheet("background-color: #111; border-radius: 6px;")
            card.setFixedSize(250, 270)

            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(5, 5, 5, 5)
            card_layout.setSpacing(5)

            metrics = [
                ("📆 Month", month.strip()),
                ("💰 Total Rent Collected", f"Ksh {total_collected or 0:,.2f}"),
                ("📄 Total Invoices Issued", total_invoices or 0),
                ("❗ Overdue Invoices", overdue_invoices or 0),
                ("🟠 Partially Paid", partially_paid or 0),
                ("🟥 Unpaid Invoices", unpaid_invoices or 0),
                ("🔻 Remaining Balance", f"Ksh {total_remaining or 0:,.2f}"),
            ]

            for label, value in metrics:
                metric_label = QLabel(f"{label}: {value}")
                metric_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                metric_label.setFixedHeight(40)
                metric_label.setStyleSheet("""
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 5px;
                """)
                card_layout.addWidget(metric_label)
                print(f"✅ Added label: {label}: {value}")  

            card.setLayout(card_layout)  
            self.cards_layout.addWidget(card, row, col)

            col += 1
            if col == 3:
                col = 0
                row += 1

        # 🔄 Force UI Refresh
        self.cards_layout.invalidate()
        self.repaint()
        self.update()

        print("🎉 Debugging complete.")


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


    def apply_filter(self):
        """Handles filter application."""
        selected_apartment = self.apartment_dropdown.currentText()

        if selected_apartment == "All Apartments":
            self.selected_apartment_id = None
        else:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT id FROM apartments WHERE name = %s", (selected_apartment,))
            result = cur.fetchone()
            conn.close()

            if result:
                self.selected_apartment_id = result[0]
            else:
                self.selected_apartment_id = None

        self.filter_panel.setVisible(False)  # Hide the panel after applying
        self.load_reports_data()  # Reload data with the applied filter

    def reset_filters(self):
        """Reset apartment filter and reload all reports."""
        print("🔄 Resetting filters...")

        # Clear the selected apartment
        self.selected_apartment_id = None

        # Reset any filter widgets (example: dropdown to default index)
        if hasattr(self, 'apartment_filter_dropdown'):
            self.apartment_filter_dropdown.setCurrentIndex(0)

        # Reload all report data
        self.load_reports_data()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportsPage()
    window.show()
    sys.exit(app.exec())
