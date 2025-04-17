import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog,
    QFormLayout, QLineEdit, QSpinBox, QComboBox, QMessageBox, QApplication,
    QSizePolicy, QCheckBox, QDoubleSpinBox, QDateEdit
)
from PyQt6.QtCore import Qt,  QDate
from PyQt6.QtGui import QFont, QColor
import psycopg2
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db  # Ensure this imports your database connection function


class PropertyMaintenanceManagement(QMainWindow):
    def __init__(self, apartment_id, apartment_name):
        super().__init__()
        self.apartment_id = apartment_id
        self.apartment_name = apartment_name
        self.setWindowTitle(f"{self.apartment_name} Maintenance Management")
        self.setGeometry(100, 100, 900, 600)  # Increased window width
        self.initUI()
        self.load_expenses()
        self.load_expense_categories()

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
        title_label = QLabel(f"{self.apartment_name} Maintenance Management")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: black;")
        self.main_layout.addWidget(title_label)

        # **Expenses Table**
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(6)
        self.expenses_table.verticalHeader().setDefaultSectionSize(30)
        self.expenses_table.setHorizontalHeaderLabels([
            "Category", "Subcategory", "Amount", "Date", "Description", "Actions"
        ])
        self.expenses_table.setColumnWidth(0, 150)  # Category
        self.expenses_table.setColumnWidth(1, 150)  # Subcategory
        self.expenses_table.setColumnWidth(2, 100)  # Amount
        self.expenses_table.setColumnWidth(3, 120)  # Date
        self.expenses_table.setColumnWidth(4, 250)  # Description
        self.expenses_table.setColumnWidth(5, 160)  # Actions


        self.expenses_table.setStyleSheet("""
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

  
        # ==== Expense Filter Panel ====
        self.expense_filter_panel = QWidget()
        self.expense_filter_panel.setFixedWidth(300)
        self.expense_filter_panel.setStyleSheet("background-color: black; border-left: 2px solid gold;")
        self.expense_filter_panel.setVisible(False)

        expense_filter_layout = QVBoxLayout()
        expense_filter_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        filter_title = QLabel("Filter Expenses")
        filter_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        filter_title.setStyleSheet("color: gold;")
        filter_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        expense_filter_layout.addWidget(filter_title)

        # -- Date Range
        date_label = QLabel("Filter by Date")
        date_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        date_label.setStyleSheet("color: white;")
        expense_filter_layout.addWidget(date_label)

        self.expense_start_date = QDateEdit()
        self.expense_start_date.setCalendarPopup(True)
        self.expense_start_date.setDate(QDate.currentDate().addMonths(-1))  # Start date = 1 month ago
        self.expense_start_date.setStyleSheet("color: gold; background-color: black;")
        expense_filter_layout.addWidget(self.expense_start_date)

        self.expense_end_date = QDateEdit()
        self.expense_end_date.setCalendarPopup(True)
        self.expense_end_date.setDate(QDate.currentDate())
        self.expense_end_date.setStyleSheet("color: gold; background-color: black;")
        expense_filter_layout.addWidget(self.expense_end_date)

        # -- Category Dropdown
        category_label = QLabel("Filter by Category")
        category_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        category_label.setStyleSheet("color: white;")
        expense_filter_layout.addWidget(category_label)

        self.expense_category_dropdown = QComboBox()
        self.expense_category_dropdown.setStyleSheet("color: gold; background-color: black;")
        self.expense_category_dropdown.addItem("All Categories")  # Default option
        # Populate categories from DB below in load_expense_categories()
        expense_filter_layout.addWidget(self.expense_category_dropdown)

        # -- Filter Button
        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.setStyleSheet("""
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
        apply_filter_btn.clicked.connect(self.filter_expenses)
        expense_filter_layout.addWidget(apply_filter_btn)

        self.expense_filter_panel.setLayout(expense_filter_layout)
       
        # **Main Content Layout (Table & Filter Panel Side-by-Side)**
        self.content_layout = QHBoxLayout()
        self.content_layout.addWidget(self.expenses_table)
        self.content_layout.addWidget(self.expense_filter_panel)

        self.main_layout.addLayout(self.content_layout)

        # **Add Expense Button**
        add_expense_button = QPushButton("Add Expense")
        add_expense_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        add_expense_button.setStyleSheet("""
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
        add_expense_button.clicked.connect(self.show_add_expense_dialog)
        self.main_layout.addWidget(add_expense_button, alignment=Qt.AlignmentFlag.AlignRight)

        # **Set Main Layout**
        container = QWidget()
        container.setStyleSheet("background-color: white;")
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def load_expenses(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Fetch expenses along with category and subcategory names
            cursor.execute("""
                SELECT 
                    e.id,
                    ec.name AS category_name,
                    esc.name AS subcategory_name,
                    e.amount,
                    e.expense_date,
                    e.description
                FROM expenses e
                LEFT JOIN expense_categories ec ON e.category_id = ec.id
                LEFT JOIN expense_subcategories esc ON e.subcategory_id = esc.id
                WHERE e.apartment_id = %s
                ORDER BY e.expense_date DESC;
            """, (self.apartment_id,))
            expenses = cursor.fetchall()

            self.expenses_table.setRowCount(len(expenses))

            for row_idx, expense in enumerate(expenses):
                expense_id, category_name, subcategory_name, amount, date, description = expense

                self.expenses_table.setItem(row_idx, 0, QTableWidgetItem(category_name or ""))
                self.expenses_table.setItem(row_idx, 1, QTableWidgetItem(subcategory_name or ""))
                self.expenses_table.setItem(row_idx, 2, QTableWidgetItem(f"{amount:.2f}"))
                self.expenses_table.setItem(row_idx, 3, QTableWidgetItem(str(date)))
                self.expenses_table.setItem(row_idx, 4, QTableWidgetItem(description))

                # Actions (Edit/Delete)
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                edit_button = QPushButton("Edit")
                delete_button = QPushButton("Delete")

                edit_button.setStyleSheet("background-color: green; color: black;")
                delete_button.setStyleSheet("background-color: red; color: black;")
                edit_button.setFixedWidth(80)
                delete_button.setFixedWidth(80)

                edit_button.clicked.connect(lambda _, uid=expense_id: self.show_edit_expense_dialog(uid))
                delete_button.clicked.connect(lambda _, uid=expense_id: self.delete_expense(uid))

                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_widget.setLayout(actions_layout)

                self.expenses_table.setCellWidget(row_idx, 5, actions_widget)

            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            print(f"Database error while loading expenses: {e}")

    def load_expense_categories(self):
        """Loads all expense categories into the dropdown."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM expense_categories;")
            categories = cursor.fetchall()

            self.expense_category_dropdown.clear()
            self.expense_category_dropdown.addItem("All Categories", None)

            for cat_id, name in categories:
                self.expense_category_dropdown.addItem(name, cat_id)

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error loading categories: {e}")


    def show_add_expense_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Expense")
        dialog.setFixedSize(550, 300)
        dialog.setStyleSheet("background-color: white;")

        layout = QFormLayout()
        layout.setHorizontalSpacing(50)
        layout.setVerticalSpacing(10)

        label_font = QFont("Arial", 12, QFont.Weight.Bold)
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
        field_style = """
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {
                background-color: #f0f0f0;
                color: black;
                border: 2px solid gray;
                border-radius: 5px;
                padding: 2px;
                font-size: 11pt;
                min-width: 180px;
                max-width: 180px;
                min-height: 20px;
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

        # Inputs
        category_dropdown = QComboBox()
        subcategory_dropdown = QComboBox()
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 1000000)
        amount_input.setDecimals(2)
        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        date_input.setDate(QDate.currentDate())
        description_input = QLineEdit()

        # Apply calendar styling
        date_input.calendarWidget().setStyleSheet("""
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

        # Apply styles
        for widget in [category_dropdown, subcategory_dropdown, amount_input, date_input, description_input]:
            widget.setStyleSheet(field_style)

        # Fetch categories
        category_map = {}  # {name: id}
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM expense_categories ORDER BY name;")
            categories = cursor.fetchall()
            for cat_id, cat_name in categories:
                category_map[cat_name] = cat_id
                category_dropdown.addItem(cat_name)
        except Exception as e:
            print("Error loading categories:", e)

        def load_subcategories(category_name):
            subcategory_dropdown.clear()
            selected_id = category_map.get(category_name)
            if selected_id:
                try:
                    cursor.execute("""
                        SELECT id, name FROM expense_subcategories 
                        WHERE category_id = %s ORDER BY name;
                    """, (selected_id,))
                    subcategories = cursor.fetchall()
                    for sub_id, sub_name in subcategories:
                        subcategory_dropdown.addItem(sub_name, sub_id)
                except Exception as e:
                    print("Error loading subcategories:", e)

        # Load subcategories for the first category initially
        if categories:
            load_subcategories(categories[0][1])

        # Reload subcategories when category changes
        category_dropdown.currentTextChanged.connect(load_subcategories)

        # Labels
        labels = [
            ("Category:", category_dropdown),
            ("Subcategory:", subcategory_dropdown),
            ("Amount (Ksh):", amount_input),
            ("Date:", date_input),
            ("Description:", description_input),
        ]

        for text, widget in labels:
            label = QLabel(text)
            label.setFont(label_font)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            layout.addRow(label, widget)

        # Save button
        save_button = QPushButton("Save")
        save_button.setStyleSheet(button_style)

        def save_expense():
            category_name = category_dropdown.currentText()
            subcategory_id = subcategory_dropdown.currentData()
            category_id = category_map.get(category_name)
            amount = amount_input.value()
            expense_date = date_input.date().toString("yyyy-MM-dd")
            description = description_input.text().strip()

            if not description:
                QMessageBox.warning(self, "Input Error", "Please enter a description.")
                return

            try:
                cursor.execute("""
                    INSERT INTO expenses (apartment_id, category_id, subcategory_id, amount, expense_date, description)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (
                    self.apartment_id,
                    category_id,
                    subcategory_id,
                    amount,
                    expense_date,
                    description
                ))
                conn.commit()
                cursor.close()
                conn.close()
                dialog.accept()
                self.load_expenses()
            except Exception as e:
                print("Database insert error:", e)
                QMessageBox.critical(self, "Error", "Failed to save expense.")

        save_button.clicked.connect(save_expense)
        layout.addRow("", save_button)

        dialog.setLayout(layout)
        dialog.exec()


    def show_edit_expense_dialog(self):
        """Handles edit expense dialog (to be implemented)."""
        pass
    
    def filter_expenses(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Get filter values
            start_date = self.expense_start_date.date().toPyDate()
            end_date = self.expense_end_date.date().toPyDate()
            selected_category = self.expense_category_dropdown.currentText()

            # Base query
            query = """
                SELECT 
                    e.id,
                    ec.name AS category_name,
                    esc.name AS subcategory_name,
                    e.amount,
                    e.expense_date,
                    e.description
                FROM expenses e
                LEFT JOIN expense_categories ec ON e.category_id = ec.id
                LEFT JOIN expense_subcategories esc ON e.subcategory_id = esc.id
                WHERE e.apartment_id = %s
                AND e.expense_date BETWEEN %s AND %s
            """
            params = [self.apartment_id, start_date, end_date]

            # Optional filter by category
            if selected_category != "All":
                query += " AND ec.name = %s"
                params.append(selected_category)

            query += " ORDER BY e.expense_date DESC"

            cursor.execute(query, params)
            filtered_expenses = cursor.fetchall()

            self.expenses_table.setRowCount(len(filtered_expenses))

            for row_idx, expense in enumerate(filtered_expenses):
                expense_id, category_name, subcategory_name, amount, date, description = expense

                self.expenses_table.setItem(row_idx, 0, QTableWidgetItem(category_name or ""))
                self.expenses_table.setItem(row_idx, 1, QTableWidgetItem(subcategory_name or ""))
                self.expenses_table.setItem(row_idx, 2, QTableWidgetItem(f"{amount:.2f}"))
                self.expenses_table.setItem(row_idx, 3, QTableWidgetItem(str(date)))
                self.expenses_table.setItem(row_idx, 4, QTableWidgetItem(description))

                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                edit_button = QPushButton("Edit")
                delete_button = QPushButton("Delete")

                edit_button.setStyleSheet("background-color: green; color: black;")
                delete_button.setStyleSheet("background-color: red; color: black;")
                edit_button.setFixedWidth(80)
                delete_button.setFixedWidth(80)

                edit_button.clicked.connect(lambda _, uid=expense_id: self.show_edit_expense_dialog(uid))
                delete_button.clicked.connect(lambda _, uid=expense_id: self.delete_expense(uid))

                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_widget.setLayout(actions_layout)

                self.expenses_table.setCellWidget(row_idx, 5, actions_widget)

            cursor.close()
            conn.close()

        except psycopg2.Error as e:
            print(f"Database error while filtering expenses: {e}")

     
    def toggle_filter_panel(self):
        if self.expense_filter_panel.isVisible():
            self.expense_filter_panel.hide()
        else:
            self.expense_filter_panel.show()

    def reset_filters(self):
        """Handles resetting filters (to be implemented)."""
        pass

    
    def go_back(self):
        from views.maintenance_management import MaintenancePage
        self.maintenance_page = MaintenancePage()
        self.maintenance_page.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PropertyMaintenanceManagement(property_id=1)
    window.show()
    sys.exit(app.exec())
