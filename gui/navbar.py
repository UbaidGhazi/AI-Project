from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt

class Navbar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(70)
        self.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E2E8F0;")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("AI Medical Diagnostic System")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1E293B; border: none;")
        
        search = QLineEdit()
        search.setPlaceholderText("Search patients or queries...")
        search.setFixedWidth(300)
        search.setStyleSheet("border-radius: 20px; padding: 8px 16px; background-color: #F1F5F9; border: none;")
        
        status = QLabel("● AI Online")
        status.setStyleSheet("color: #10B981; font-weight: 500; border: none;")
        
        layout.addWidget(title)
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(search)
        layout.addSpacing(20)
        layout.addWidget(status)
