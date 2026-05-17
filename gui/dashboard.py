from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
from PySide6.QtCore import Qt

class DashboardCard(QFrame):
    def __init__(self, title, value, color):
        super().__init__()
        self.setProperty("class", "Card")
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #64748B; font-size: 14px; font-weight: 500;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("System Overview")
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        layout.addSpacing(20)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        grid.addWidget(DashboardCard("Total Facts", "34", "#3B82F6"), 0, 0)
        grid.addWidget(DashboardCard("Total Rules", "24", "#10B981"), 0, 1)
        grid.addWidget(DashboardCard("Diagnoses Processed", "1,204", "#8B5CF6"), 0, 2)
        grid.addWidget(DashboardCard("AI Confidence Avg", "94.2%", "#F59E0B"), 1, 0)
        grid.addWidget(DashboardCard("System Accuracy", "98.5%", "#EF4444"), 1, 1)
        
        layout.addLayout(grid)
        layout.addStretch()
