import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTableWidget,
    QTableWidgetItem, QMessageBox, QDialog, QLineEdit,
    QFormLayout, QFrame, QHeaderView, QSplitter, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

API_BASE = "http://127.0.0.1:8000"
API_UPLOAD_URL = f"{API_BASE}/api/upload/"
API_REPORT_URL = f"{API_BASE}/api/report/"
API_HISTORY_URL = f"{API_BASE}/api/history/"

# STYLESHEET (Light Theme matching Web App)
STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', sans-serif;
}
QPushButton {
    background-color: #0ea5e9;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #0284c7;
}
QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
}
QLabel {
    font-size: 14px;
    color: #0f172a;
}
QTableWidget {
    background-color: white;
    border: 1px solid #e2e8f0;
    gridline-color: #e2e8f0;
    color: #0f172a;
    selection-background-color: #e0f2fe;
    selection-color: #0f172a;
}
QHeaderView::section {
    background-color: #f1f5f9;
    color: #64748b;
    padding: 8px;
    border: 1px solid #e2e8f0;
    font-weight: bold;
}
QLineEdit {
    background-color: white;
    border: 1px solid #e2e8f0;
    padding: 8px;
    border-radius: 4px;
    color: #0f172a;
}
QFrame#StatCard, QFrame#ChartCard, QFrame#HistoryCard {
    background-color: white;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}
QLabel#PageTitle {
    font-size: 24px;
    font-weight: bold;
    color: #0f172a;
}
QLabel#StatTitle {
    color: #64748b;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
}
QLabel#StatValue {
    font-size: 24px;
    font-weight: bold;
    color: #0f172a;
}
QListWidget {
    background-color: white;
    border: none;
    color: #0f172a;
}
QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #e2e8f0;
}
QListWidget::item:hover {
    background-color: #f1f5f9;
}
QListWidget::item:selected {
    background-color: #e0f2fe;
    color: #0f172a;
}
QFrame#Sidebar {
    background-color: #1e293b;
}
QLabel#SidebarTitle {
    color: white;
    font-size: 20px;
    font-weight: bold;
    padding-left: 10px;
}
QLabel#SidebarSection {
    color: #94a3b8; 
    font-weight: bold; 
    font-size: 12px;
    margin-top: 20px;
}
"""

class StatCard(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setObjectName("StatCard")
        layout = QVBoxLayout()
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("StatTitle")
        
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("StatValue")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.setLayout(layout)

    def update_value(self, value):
        self.value_label.setText(str(value))


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - ChemVis")
        self.setFixedSize(400, 250)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Chemical Equipment Visualizer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #0f172a;")
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.accept)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
        layout.addStretch()

        self.setLayout(layout)

    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()


class App(QWidget):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.current_dataset_id = None
        
        self.setWindowTitle("ChemVis Desktop Pro")
        self.resize(1300, 850)
        
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.init_sidebar()
        self.init_content()
        self.setLayout(self.main_layout)
        
        # Load initial history
        self.refresh_history()

    def init_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(280)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(15)
        
        # Logo Area
        logo = QLabel("ChemVis")
        logo.setObjectName("SidebarTitle")
        # Explicit style to ensure visibility
        logo.setStyleSheet("color: #0ea5e9; font-size: 24px; font-weight: bold;")
        layout.addWidget(logo)
        
        # Actions Section
        action_label = QLabel("ACTIONS")
        action_label.setObjectName("SidebarSection")
        layout.addWidget(action_label)
        
        self.upload_btn = QPushButton("  Upload CSV")
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setStyleSheet("text-align: left;")
        self.upload_btn.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_btn)
        
        self.download_btn = QPushButton("  Download Report")
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.setStyleSheet("text-align: left;")
        self.download_btn.clicked.connect(self.download_report)
        self.download_btn.setEnabled(False)
        layout.addWidget(self.download_btn)

        layout.addStretch()
        
        # User Info
        user_info = QLabel("Logged in as User")
        user_info.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(user_info)
        
        sidebar.setLayout(layout)
        self.main_layout.addWidget(sidebar)

    def init_content(self):
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Dashboard Analysis")
        title.setObjectName("PageTitle")
        header.addWidget(title)
        layout.addLayout(header)
        
        # Stats Row
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        self.stat_total = StatCard("Total Equipment", "-")
        self.stat_flow = StatCard("Avg Flowrate (m³/h)", "-")
        self.stat_press = StatCard("Avg Pressure (bar)", "-")
        
        self.stats_layout.addWidget(self.stat_total)
        self.stats_layout.addWidget(self.stat_flow)
        self.stats_layout.addWidget(self.stat_press)
        layout.addLayout(self.stats_layout)
        
        # Middle Section (Chart + History)
        middle_section = QWidget()
        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(0,0,0,0)
        middle_layout.setSpacing(20)
        
        # Chart
        chart_frame = QFrame()
        chart_frame.setObjectName("ChartCard")
        chart_layout = QVBoxLayout()
        self.figure = Figure(facecolor='white')
        self.canvas = FigureCanvasQTAgg(self.figure)
        chart_layout.addWidget(self.canvas)
        chart_frame.setLayout(chart_layout)
        
        # History Panel (Right Side)
        history_frame = QFrame()
        history_frame.setObjectName("HistoryCard")
        history_frame.setFixedWidth(300)
        history_layout = QVBoxLayout()
        history_layout.setContentsMargins(15, 15, 15, 15)
        
        h_label = QLabel("Recent Uploads")
        h_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        history_layout.addWidget(h_label)
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_history_item)
        history_layout.addWidget(self.history_list)
        history_frame.setLayout(history_layout)

        # Add to middle layout with ratios
        middle_layout.addWidget(chart_frame, 2)
        middle_layout.addWidget(history_frame, 1)
        middle_section.setLayout(middle_layout)
        
        # Splitter for Middle Section and Table
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #e2e8f0; }")
        
        splitter.addWidget(middle_section)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Flowrate", "Pressure", "Temperature"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        splitter.addWidget(self.table)
        
        layout.addWidget(splitter)
        content.setLayout(layout)
        
        self.main_layout.addWidget(content)

    def refresh_history(self):
        try:
            response = requests.get(API_HISTORY_URL, auth=self.auth)
            if response.status_code == 200:
                self.history_list.clear()
                history_data = response.json()
                for item in history_data:
                    display_text = f"{item['name']}\n{item['total']} items • {item['uploaded_at'][:10]}"
                    list_item = QListWidgetItem(display_text)
                    list_item.setData(Qt.UserRole, item)
                    self.history_list.addItem(list_item)
        except Exception as e:
            print(f"Failed to fetch history: {e}")

    def load_history_item(self, item):
        data = item.data(Qt.UserRole)
        self.current_dataset_id = data['id']
        self.download_btn.setEnabled(True)
        QMessageBox.information(self, "Dataset Selected", 
            f"Selected dataset: {data['name']}.\nYou can now download its report.")

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if not file_path: return

        try:
            with open(file_path, "rb") as f:
                response = requests.post(API_UPLOAD_URL, files={"file": f}, auth=self.auth)

            if response.status_code == 403:
                QMessageBox.critical(self, "Error", "Authentication Failed")
                return

            data = response.json()
            self.current_dataset_id = data.get("id")
            self.download_btn.setEnabled(True)
            self.update_ui(data)
            self.refresh_history()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_ui(self, data):
        # Update Stats
        self.stat_total.update_value(data['total_equipment'])
        self.stat_flow.update_value(f"{data['avg_flowrate']:.2f}")
        self.stat_press.update_value(f"{data['avg_pressure']:.2f}")
        
        # Update Chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white')
        
        bars = ax.bar(
            data["type_distribution"].keys(),
            data["type_distribution"].values(),
            color=['#0ea5e9', '#6366f1', '#22c55e', '#f43f5e']
        )
        
        # Chart Styling
        ax.spines['bottom'].set_color('#e2e8f0')
        ax.spines['top'].set_visible(False) 
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#e2e8f0')
        ax.tick_params(axis='x', colors='#64748b')
        ax.tick_params(axis='y', colors='#64748b')
        
        self.canvas.draw()
        
        # Update Table
        self.table.setRowCount(0)
        for row in data["table"]:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(row["Equipment Name"])))
            self.table.setItem(r, 1, QTableWidgetItem(str(row["Type"])))
            self.table.setItem(r, 2, QTableWidgetItem(str(row["Flowrate"])))
            self.table.setItem(r, 3, QTableWidgetItem(str(row["Pressure"])))
            self.table.setItem(r, 4, QTableWidgetItem(str(row["Temperature"])))

    def download_report(self):
        if not self.current_dataset_id: return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", f"report_{self.current_dataset_id}.pdf", "PDF Files (*.pdf)"
        )
        if not save_path: return

        try:
            response = requests.get(f"{API_REPORT_URL}{self.current_dataset_id}/", auth=self.auth)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                QMessageBox.information(self, "Success", "Report downloaded successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to download report.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        username, password = login.get_credentials()
        window = App(auth=(username, password))
        window.show()
        sys.exit(app.exec_())
