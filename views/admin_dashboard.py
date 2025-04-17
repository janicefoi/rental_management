import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGridLayout, QFrame
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QTimer
from views.property_management import PropertiesPage
from views.tenant_management import TenantManagementPage
from views.payment_management import PaymentManagementPage
from views.maintenance_management import MaintenancePage
from views.reports_management import ReportsManagementPage
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QToolButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db 

class HoverButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.default_size = (220, 50)
        self.hover_size = (230, 55)
        self.setFixedSize(*self.default_size)
        self.setFont(QFont("Inter", 12))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #FFD700;
                border-radius: 12px;
                border: none;
            }
        """)

    def enterEvent(self, event):
        self.setFixedSize(*self.hover_size)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #1a1a1a;
                border-radius: 12px;
                border: none;
            }
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setFixedSize(*self.default_size)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #FFD700;
                border-radius: 12px;
                border: none;
            }
        """)
        super().leaveEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_sidebar_expanded = True
        self.initUI()
        # Update stats periodically
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_dashboard_stats)
        self.stats_timer.start(30000)  # Update every 30 seconds

    def get_dashboard_stats(self):
        conn = connect_db()
        cur = conn.cursor()
        stats = {}
        
        try:
            # Get unit statistics
            cur.execute("""
                SELECT status, COUNT(*) as count
                FROM units 
                GROUP BY status
                ORDER BY status
            """)
            stats['units'] = cur.fetchall()
            
            # Get invoice statistics
            cur.execute("""
                SELECT status, COUNT(*) as count
                FROM invoices
                GROUP BY status
                ORDER BY status
            """)
            stats['invoices'] = cur.fetchall()
            
        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
        finally:
            conn.close()
        
        return stats

    def update_dashboard_stats(self):
        stats = self.get_dashboard_stats()
        
        # Clear existing grid layout
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().deleteLater()

        # Create container for charts
        charts_container = QWidget()
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Units Chart
        units_card = self.create_pie_chart(
            "Unit Status Overview",
            stats['units'],
            {
                'occupied': '#FFD700',       # Gold
                'available': '#2ecc71',      # Emerald Green
                'under maintenance': '#e74c3c' # Coral Red
            }
        )
        
        # Invoices Chart
        invoices_card = self.create_pie_chart(
            "Invoice Status Overview",
            stats['invoices'],
            {
                'paid': '#2ecc71',           # Emerald Green
                'unpaid': '#e67e22',         # Carrot Orange
                'overdue': '#e74c3c',        # Coral Red
                'partially_paid': '#3498db'   # Blue
            }
        )
        
        charts_layout.addWidget(units_card)
        charts_layout.addWidget(invoices_card)
        charts_container.setLayout(charts_layout)
        
        self.grid_layout.addWidget(charts_container, 0, 0)

    def create_pie_chart(self, title, data, colors):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                min-width: 400px;
                max-width: 500px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title styling
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: black;
            font-size: 10px;
            font-weight: bold;
            font-family: 'Montserrat';
            text-align: center;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)  # Add title to layout first
        
        # Update pie chart colors and style
        fig = Figure(figsize=(6, 6), facecolor='white')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Prepare data
        labels = []
        sizes = []
        chart_colors = []
        
        for status, count in data:
            labels.append(f"{status.title()}\n({count})")
            sizes.append(count)
            chart_colors.append(colors.get(status.lower(), '#95a5a6'))
        
        # Create pie chart with modern styling
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=chart_colors,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(width=0.7, edgecolor='#1a1a1a'),  # Donut style
            pctdistance=0.75,
            textprops={'color': 'white'}
        )
        
        # Style the percentage labels
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)
        
        # Style the labels
        for text in texts:
            text.set_color('black')
            text.set_fontsize(8)
        
        ax.axis('equal')
        ax.set_facecolor('white')
        
        layout.addWidget(canvas)
        card.setLayout(layout)
        return card

    def initUI(self):
        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(100, 100, 1200, 700)

        main_layout = QHBoxLayout()

        # Sidebar layout
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(10, 15, 10, 15)
        sidebar.setSpacing(15)

        # Create navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", "dashboard"),
            ("🏢 Properties", "properties"),
            ("👤 Tenants", "tenants"),
            ("💰 Payments", "payments"),
            ("🛠 Maintenance", "maintenance"),
            ("📊 Reports", "reports")
        ]

        # Add buttons to sidebar
        self.buttons = {}
        for text, name in nav_buttons:
            btn = HoverButton(text)
            btn.setObjectName(name)
            if name == "properties":
                btn.clicked.connect(self.open_property_management)
            elif name == "tenants":
                btn.clicked.connect(self.open_tenant_management)
            elif name == "payments":
                btn.clicked.connect(self.open_payment_management)
            elif name == "maintenance":
                btn.clicked.connect(self.open_maintenance_management)
            elif name == "reports":
                btn.clicked.connect(self.open_reports_management)
            
            sidebar.addWidget(btn)
            self.buttons[name] = btn

        sidebar.addStretch()

        # Create sidebar container
        sidebar_container = QWidget()
        sidebar_container.setLayout(sidebar)
        sidebar_container.setFixedWidth(250)
        sidebar_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
        """)

        # Main content area
        main_content = QWidget()
        main_content.setObjectName("main_content")

        # Slideshow setup
        self.slideshow_label = QLabel()
        self.slideshow_label.setFixedSize(1100, 400)
        self.slideshow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slideshow_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border-radius: 15px;
                padding: 10px;
            }
        """)

        # Title setup
        self.title_label = QLabel("🏠 Admin Dashboard")
        self.title_label.setFont(QFont("Montserrat", 24, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: black;
            }
        """)

        # Layout setup
        title_layout = QVBoxLayout()
        title_layout.addWidget(self.slideshow_label)
        title_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        title_container = QWidget()
        title_container.setLayout(title_layout)

        # Stats setup
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)

        stats_container = QWidget()
        stats_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 20px;
                padding: 20px;
                margin-top: 20px;
            }
        """)

        stats_layout = QVBoxLayout()
        stats_layout.addLayout(self.grid_layout)
        stats_container.setLayout(stats_layout)

        # Main content layout
        content_layout = QVBoxLayout()
        content_layout.addWidget(title_container)
        content_layout.addWidget(stats_container)
        content_layout.setSpacing(20)
        main_content.setLayout(content_layout)

        # Add to main layout
        main_layout.addWidget(sidebar_container)
        main_layout.addWidget(main_content)

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initial stats update
        self.update_dashboard_stats()

        # Setup slideshow
        self.images = ["admin_dashboard.jpg", "admin_dashboard2.jpg", "admin_dashboard3.jpg", "admin_dashboard5.jpg", "admin_dashboard6.jpg"]
        self.current_image_index = 0
        self.update_slideshow()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.start(5000)
        self.setStyleSheet("background-color: white;")

    def update_slideshow(self):
        """Update the slideshow with the current image."""
        pixmap = QPixmap(self.images[self.current_image_index])
        if not pixmap.isNull():
            self.slideshow_label.setPixmap(pixmap.scaled(self.slideshow_label.width(), self.slideshow_label.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.slideshow_label.setText("Image not found")

    def next_image(self):
        """Switch to the next image in the slideshow."""
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.update_slideshow()

    # Navigation Functions
    def open_property_management(self):
        self.hide()  # Hide Admin Dashboard instead of closing it
        self.property_window = PropertiesPage()
        self.property_window.show()

    def open_tenant_management(self):
        self.hide()  # Hide Admin Dashboard instead of closing it
        self.property_window = TenantManagementPage()
        self.property_window.show()

    
    def open_payment_management(self):
        self.hide()  # Hide Admin Dashboard instead of closing it
        self.property_window = PaymentManagementPage()
        self.property_window.show()

    def open_maintenance_management(self):
        self.hide()  # Hide Admin Dashboard instead of closing it
        self.property_window = MaintenancePage()
        self.property_window.show()

    def open_reports_management(self):
        self.hide()  # Hide Admin Dashboard instead of closing it
        self.reports_window = ReportsManagementPage()
        self.reports_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
