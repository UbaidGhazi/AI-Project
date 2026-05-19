import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

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
        layout.setContentsMargins(30, 24, 30, 24)
        
        # Banner Image
        banner = QLabel()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_path = os.path.join(base_dir, "assets", "images", "medical_banner.png")
        
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            banner.setPixmap(pixmap.scaled(900, 240, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            banner.setFixedHeight(220)
            banner.setStyleSheet("border-radius: 16px; border: 1px solid #E2E8F0; background-color: #F1F5F9;")
            banner.setScaledContents(True)
            layout.addWidget(banner)
            layout.addSpacing(20)
        
        header = QLabel("System Performance & Statistics")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        layout.addWidget(header)
        layout.addSpacing(15)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        grid.addWidget(DashboardCard("Symbolic Clinical Facts", "35 Facts Active", "#3B82F6"), 0, 0)
        grid.addWidget(DashboardCard("Logical Inference Rules", "18 Rules Active", "#10B981"), 0, 1)
        grid.addWidget(DashboardCard("Total Clinical Queries", "1,204 Queries", "#8B5CF6"), 0, 2)
        grid.addWidget(DashboardCard("Symbolic Inference Accuracy", "98.5% Accuracy", "#EF4444"), 1, 0)
        grid.addWidget(DashboardCard("AI Clinical Confidence Avg", "94.2% Average", "#F59E0B"), 1, 1)
        
        layout.addLayout(grid)
        layout.addStretch()

