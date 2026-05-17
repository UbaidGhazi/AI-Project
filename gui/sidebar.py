"""
sidebar.py
Animated left navigation sidebar.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QSpacerItem, QSizePolicy, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

TABS = [
    ("🏠", "Dashboard"),
    ("🩺", "Diagnosis"),
    ("🤖", "AI Chatbot"),
    ("📊", "AI Analysis"),
    ("📋", "Reports"),
    ("📚", "Knowledge Base"),
    ("🕐", "Query History"),
    ("⚙️", "Settings"),
]


class Sidebar(QWidget):
    tab_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(240)
        self.buttons: list[QPushButton] = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Brand header ──────────────────────────────────────────────────────
        brand = QWidget()
        brand.setFixedHeight(70)
        brand.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                            "stop:0 #1E40AF, stop:1 #2563EB);")
        b_layout = QVBoxLayout(brand)
        b_layout.setContentsMargins(20, 0, 20, 0)
        b_layout.setAlignment(Qt.AlignVCenter)

        logo = QLabel("IntelliExpert")
        logo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo.setStyleSheet("color: white; background: transparent; border: none;")
        tagline = QLabel("AI Medical Platform")
        tagline.setFont(QFont("Segoe UI", 9))
        tagline.setStyleSheet("color: #93C5FD; background: transparent; border: none;")
        b_layout.addWidget(logo)
        b_layout.addWidget(tagline)
        layout.addWidget(brand)

        # ── Navigation buttons ────────────────────────────────────────────────
        nav_widget = QWidget()
        nav_widget.setStyleSheet("background-color: #FFFFFF;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(12, 16, 12, 16)
        nav_layout.setSpacing(4)

        for i, (icon, text) in enumerate(TABS):
            btn = QPushButton(f"  {icon}  {text}")
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.setFixedHeight(44)
            btn.setFont(QFont("Segoe UI", 13))
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    border: none;
                    border-radius: 8px;
                    padding-left: 12px;
                    color: #64748B;
                    background-color: transparent;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #F1F5F9;
                    color: #0F172A;
                }
                QPushButton:checked {
                    background-color: #EFF6FF;
                    color: #2563EB;
                    font-weight: 700;
                    border-left: 3px solid #2563EB;
                }
            """)
            btn.clicked.connect(lambda _, idx=i: self.on_tab_clicked(idx))
            self.buttons.append(btn)
            nav_layout.addWidget(btn)

        nav_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ── Footer ────────────────────────────────────────────────────────────
        footer = QLabel("v1.0  ·  Symbolic AI")
        footer.setStyleSheet("color: #CBD5E1; font-size: 11px; margin-left: 16px;")
        nav_layout.addWidget(footer)

        layout.addWidget(nav_widget)

    def on_tab_clicked(self, idx: int):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == idx)
        self.tab_changed.emit(idx)

    def set_active(self, idx: int):
        self.on_tab_clicked(idx)
