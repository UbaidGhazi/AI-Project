"""
settings.py
System settings page — theme, database management, system info.
"""

import os, sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QComboBox, QCheckBox,
                               QGroupBox, QMessageBox, QScrollArea)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SettingsSection(QGroupBox):
    def __init__(self, title: str):
        super().__init__(title)
        self.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #1E293B;
                border: 1px solid #E2E8F0; border-radius: 10px;
                margin-top: 12px; padding: 16px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 12px;
                padding: 0 6px; color: #2563EB;
            }
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(10)

    def add_row(self, label_text: str, widget):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #475569; font-size: 13px; font-weight: normal;")
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(widget)
        self._layout.addLayout(row)


class SettingsPage(QWidget):
    theme_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.query_processor = None
        self.init_ui()

    def set_query_processor(self, qp):
        self.query_processor = qp

    def init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 30, 30, 30)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(20)

        # ── Page header ───────────────────────────────────────────────────────
        header = QLabel("Settings")
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header.setStyleSheet("color: #1E293B;")
        layout.addWidget(header)

        # ── Appearance ────────────────────────────────────────────────────────
        appearance = SettingsSection("🎨  Appearance")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light (Default)", "Dark", "Ocean Blue"])
        self.theme_combo.setFixedWidth(200)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E2E8F0; border-radius: 6px;
                padding: 6px 12px; font-size: 13px; background: white;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { border: 1px solid #E2E8F0; }
        """)
        appearance.add_row("Color Theme", self.theme_combo)

        self.font_combo = QComboBox()
        self.font_combo.addItems(["Segoe UI", "Inter", "Poppins", "Arial"])
        self.font_combo.setFixedWidth(200)
        self.font_combo.setStyleSheet(self.theme_combo.styleSheet())
        appearance.add_row("Font Family", self.font_combo)

        self.animations_cb = QCheckBox("Enable animations")
        self.animations_cb.setChecked(True)
        self.animations_cb.setStyleSheet("font-size: 13px; color: #475569;")
        appearance._layout.addWidget(self.animations_cb)
        layout.addWidget(appearance)

        # ── Database ──────────────────────────────────────────────────────────
        db_section = SettingsSection("🗄️  Database")

        self.db_path_lbl = QLabel("Loading…")
        self.db_path_lbl.setStyleSheet("color: #64748B; font-size: 12px; font-family: monospace;")
        db_section._layout.addWidget(self.db_path_lbl)

        btn_clear = QPushButton("🗑  Clear All Query History")
        btn_clear.clicked.connect(self.clear_history)
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2; color: #EF4444;
                border: 1px solid #FECACA; border-radius: 8px;
                padding: 8px 18px; font-weight: 600; font-size: 13px;
            }
            QPushButton:hover { background-color: #FEE2E2; }
        """)
        db_section._layout.addWidget(btn_clear)
        layout.addWidget(db_section)

        # ── System Info ───────────────────────────────────────────────────────
        info_section = SettingsSection("ℹ️  System Information")
        info_items = [
            ("Application", "IntelliExpert AI v1.0"),
            ("Python Version", f"{sys.version.split()[0]}"),
            ("Platform", sys.platform.title()),
            ("Architecture", "Symbolic AI + RAG Chatbot"),
            ("Knowledge Base", "8 Diseases · 30+ Facts · 20+ Rules"),
            ("Inference Engine", "Prolog (SWI-Prolog + PySWIP)"),
            ("GUI Framework", "PySide6 (Qt6)"),
        ]
        for key, val in info_items:
            row = QHBoxLayout()
            k = QLabel(key)
            k.setStyleSheet("color: #64748B; font-size: 13px;")
            v = QLabel(val)
            v.setStyleSheet("color: #1E293B; font-size: 13px; font-weight: 600;")
            row.addWidget(k)
            row.addStretch()
            row.addWidget(v)
            info_section._layout.addLayout(row)
        layout.addWidget(info_section)

        layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

        # Load DB path
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db = os.path.join(base, "database", "history.db")
        self.db_path_lbl.setText(f"Path: {db}")

    def clear_history(self):
        if not self.query_processor:
            QMessageBox.warning(self, "Unavailable", "Database not connected.")
            return
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Delete ALL diagnosis history permanently?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                cur = self.query_processor.conn.cursor()
                cur.execute("DELETE FROM queries")
                self.query_processor.conn.commit()
                QMessageBox.information(self, "Done", "History cleared successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
