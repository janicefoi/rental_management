import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QSizePolicy, QApplication,
    QFrame, QComboBox, QTabWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class ReportsManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_apartment_id = None
        self.setWindowTitle("Financial Reports")
        self.setGeometry(100, 100, 900, 600)  
        self.initUI()
        self.load_reports_data()

    def initUI(self):
        self.main_layout = QVBoxLayout()

        # Top Button Section
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

        title_label = QLabel("Financial Reports & Analytics")
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

        top_button_layout.addWidget(back_button)
        top_button_layout.addStretch(1)
        top_button_layout.addWidget(title_label)
        top_button_layout.addStretch(1)
        top_button_layout.addWidget(filter_button)
        top_button_layout.addWidget(reset_button)

        self.main_layout.addLayout(top_button_layout)

        # Graph Tabs
        graph_tabs = QTabWidget()
        graph_tabs.setStyleSheet("""
            QTabWidget {
                background-color: white;
                border: 2px solid #1a1a1a;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: #1a1a1a;
                color: #FFD700;
                padding: 8px 20px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #FFD700;
                color: #1a1a1a;
            }
        """)

        self.income_expense_canvas = self.create_income_expense_graph()
        self.net_income_canvas = self.create_net_income_graph()
        
        graph_tabs.addTab(self.income_expense_canvas, "Income vs Expenses")
        graph_tabs.addTab(self.net_income_canvas, "Net Income Trend")
        
        self.main_layout.addWidget(graph_tabs)

        # Report Cards Container
        container = QWidget()
        container_layout = QVBoxLayout()

        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(15)

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

        # Filter Panel
        self.filter_panel = QWidget()
        self.filter_panel.setFixedWidth(300)
        self.filter_panel.setStyleSheet("background-color: black; border-left: 2px solid gold;")

        filter_layout = QVBoxLayout()
        filter_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        filter_title = QLabel("Filter Reports")
        filter_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        filter_title.setStyleSheet("color: gold;")
        filter_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        filter_layout.addWidget(filter_title)

        apartment_label = QLabel("Filter by Apartment")
        apartment_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        apartment_label.setStyleSheet("color: white;")
        filter_layout.addWidget(apartment_label)

        self.apartment_dropdown = QComboBox()
        self.apartment_dropdown.setStyleSheet("color: gold; background-color: black;")
        self.apartment_dropdown.addItem("All Apartments")
        filter_layout.addWidget(self.apartment_dropdown)

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
        self.filter_panel.hide()

        content_layout = QHBoxLayout()
        content_layout.addWidget(container)
        content_layout.addWidget(self.filter_panel)

        self.main_layout.addLayout(content_layout)
        self.setLayout(self.main_layout)
        self.setStyleSheet("background-color: white;")
        
        self.load_apartments()

    def load_reports_data(self):
        conn = connect_db()
        cur = conn.cursor()

        base_query = """
            WITH monthly_payments AS (
                SELECT 
                    DATE_TRUNC('month', p.payment_date) AS month_start,
                    TO_CHAR(p.payment_date, 'Month YYYY') AS month,
                    SUM(CASE WHEN p.status = 'paid' THEN p.amount_paid ELSE 0 END) as total_income
                FROM payments p
                JOIN tenants t ON p.tenant_id = t.id
                JOIN units u ON t.unit_id = u.id
                WHERE (CASE WHEN %s != -1 THEN u.apartment_id = %s ELSE TRUE END)
                GROUP BY month_start, month
            ),
            monthly_expenses AS (
                SELECT 
                    DATE_TRUNC('month', e.expense_date) AS month_start,
                    SUM(e.amount) as total_expenses
                FROM expenses e
                WHERE (CASE WHEN %s != -1 THEN e.apartment_id = %s ELSE TRUE END)
                GROUP BY month_start
            )
            SELECT 
                mp.month,
                COALESCE(mp.total_income, 0) as total_income,
                COALESCE(me.total_expenses, 0) as total_expenses,
                COALESCE(mp.total_income, 0) - COALESCE(me.total_expenses, 0) as net_income
            FROM monthly_payments mp
            LEFT JOIN monthly_expenses me ON mp.month_start = me.month_start
            ORDER BY mp.month_start DESC;
        """

        try:
            if self.selected_apartment_id is not None:
                cur.execute(base_query, (self.selected_apartment_id, self.selected_apartment_id, 
                                       self.selected_apartment_id, self.selected_apartment_id))
            else:
                cur.execute(base_query, (-1, -1, -1, -1))
                
            monthly_data = cur.fetchall()
            self.create_monthly_cards(monthly_data)
            self.update_graphs(monthly_data)
        except Exception as e:
            print(f"Error loading report data: {e}")
        finally:
            conn.close()

    def create_monthly_cards(self, monthly_data):
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        row, col = 0, 0
        for month_data in monthly_data:
            month, total_income, total_expenses, net_income = month_data
            
            card = QFrame()
            card.setStyleSheet("background-color: #111; border-radius: 6px;")
            card.setFixedSize(250, 270)

            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(5, 5, 5, 5)
            card_layout.setSpacing(5)
            
            metrics = [
                ("📆 Month", month.strip()),
                ("💰 Total Income", f"Ksh {total_income:,.2f}"),
                ("💳 Total Expenses", f"Ksh {total_expenses:,.2f}"),
                ("📊 Net Income", f"Ksh {net_income:,.2f}")
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

            card.setLayout(card_layout)
            self.cards_layout.addWidget(card, row, col)
            
            col += 1
            if col == 3:
                col = 0
                row += 1

        # Force UI Refresh
        self.cards_layout.invalidate()
        self.repaint()
        self.update()

    def create_income_expense_graph(self):
        fig = Figure(figsize=(8, 4), facecolor='white')
        canvas = FigureCanvas(fig)
        self.income_expense_ax = fig.add_subplot(111)
        self.income_expense_ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        return canvas

    def create_net_income_graph(self):
        fig = Figure(figsize=(8, 4), facecolor='white')
        canvas = FigureCanvas(fig)
        self.net_income_ax = fig.add_subplot(111)
        self.net_income_ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        return canvas

    def update_graphs(self, monthly_data):
        self.income_expense_ax.clear()
        self.net_income_ax.clear()

        months = [row[0].strip() for row in monthly_data]
        income = [float(row[1]) for row in monthly_data]
        expenses = [float(row[2]) for row in monthly_data]
        net_income = [float(row[3]) for row in monthly_data]

        # Income vs Expenses Graph
        x = np.arange(len(months))
        bar_width = 0.25  # Reduced bar width
        
        # Create modern bars with alpha and edge color
        self.income_expense_ax.bar(x - bar_width/2, income, bar_width, 
                                 label='Income', 
                                 color='#2ecc71', 
                                 alpha=0.8,
                                 edgecolor='#27ae60',
                                 linewidth=1,
                                 capstyle='round')
        self.income_expense_ax.bar(x + bar_width/2, expenses, bar_width, 
                                 label='Expenses', 
                                 color='#e74c3c',
                                 alpha=0.8,
                                 edgecolor='#c0392b',
                                 linewidth=1,
                                 capstyle='round')

        # Style the income vs expenses graph
        self.income_expense_ax.set_title('Income vs Expenses by Month', 
                                       color='#1a1a1a', 
                                       pad=20, 
                                       fontsize=14,
                                       fontweight='bold')
        self.income_expense_ax.set_xlabel('Month', color='#1a1a1a', labelpad=10, fontsize=10)
        self.income_expense_ax.set_ylabel('Amount (KSH)', color='#1a1a1a', labelpad=10, fontsize=10)
        
        # Style the grid
        self.income_expense_ax.grid(True, linestyle='--', alpha=0.2, color='#666666')
        self.income_expense_ax.set_axisbelow(True)
        
        # Style the spines
        for spine in self.income_expense_ax.spines.values():
            spine.set_color('#666666')
            spine.set_linewidth(0.5)

        # Style ticks
        self.income_expense_ax.tick_params(colors='#1a1a1a', which='both', labelsize=8)
        self.income_expense_ax.set_xticks(x)
        self.income_expense_ax.set_xticklabels(months, rotation=45, ha='right')

        # Modern legend
        legend = self.income_expense_ax.legend(facecolor='white', 
                                             edgecolor='#666666',
                                             fontsize=10)
        for text in legend.get_texts():
            text.set_color('#1a1a1a')

        # Net Income Trend Graph
        # Create gradient fill under the line
        self.net_income_ax.fill_between(x, net_income, 0,
                                      alpha=0.2,
                                      color='#3498db')
        
        # Plot line with gradient color
        self.net_income_ax.plot(x, net_income, 
                              color='#3498db', 
                              linewidth=2.5,
                              marker='o',
                              markersize=8,
                              markerfacecolor='white',
                              markeredgecolor='#3498db',
                              markeredgewidth=2)

        # Style the net income graph
        self.net_income_ax.set_title('Net Income Trend', 
                                   color='#1a1a1a', 
                                   pad=20, 
                                   fontsize=14,
                                   fontweight='bold')
        self.net_income_ax.set_xlabel('Month', color='#1a1a1a', labelpad=10, fontsize=10)
        self.net_income_ax.set_ylabel('Net Income (KSH)', color='#1a1a1a', labelpad=10, fontsize=10)
        
        # Style the grid
        self.net_income_ax.grid(True, linestyle='--', alpha=0.2, color='#666666')
        self.net_income_ax.set_axisbelow(True)
        
        # Style the spines
        for spine in self.net_income_ax.spines.values():
            spine.set_color('#666666')
            spine.set_linewidth(0.5)

        # Style ticks
        self.net_income_ax.tick_params(colors='#1a1a1a', which='both', labelsize=8)
        self.net_income_ax.set_xticks(x)
        self.net_income_ax.set_xticklabels(months, rotation=45, ha='right')

        # Update layout with more padding
        self.income_expense_ax.figure.tight_layout(pad=2.0)
        self.net_income_ax.figure.tight_layout(pad=2.0)

        # Render the graphs
        self.income_expense_canvas.draw()
        self.net_income_canvas.draw()

    def load_apartments(self):
        self.apartment_dropdown.clear()
        self.apartment_dropdown.addItem("All Apartments", -1)
        
        conn = connect_db()
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT id, name FROM apartments ORDER BY name")
            apartments = cur.fetchall()
            
            for apt_id, apt_name in apartments:
                self.apartment_dropdown.addItem(apt_name, apt_id)
        except Exception as e:
            print(f"Error loading apartments: {e}")
        finally:
            conn.close()

    def go_back(self):
        from views.admin_dashboard import MainWindow
        self.admin_dashboard = MainWindow()
        self.admin_dashboard.show()
        self.close()

    def toggle_filter_panel(self):
        if self.filter_panel.isVisible():
            self.filter_panel.hide()
        else:
            self.filter_panel.show()

    def apply_filter(self):
        self.selected_apartment_id = self.apartment_dropdown.currentData()
        self.filter_panel.hide()
        self.load_reports_data()

    def reset_filters(self):
        self.selected_apartment_id = None
        self.apartment_dropdown.setCurrentIndex(0)
        self.load_reports_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportsManagementPage()
    window.show()
    sys.exit(app.exec())