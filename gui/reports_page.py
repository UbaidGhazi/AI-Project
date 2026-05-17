"""
reports_page.py
View, manage and export PDF reports of all past diagnoses.
"""

import os
from datetime import datetime

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QFrame, QFileDialog,
                               QMessageBox, QTableWidget, QTableWidgetItem,
                               QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.query_processor = None
        self.report_generator = None
        self.init_ui()

    def set_dependencies(self, query_processor, report_generator_fn):
        self.query_processor = query_processor
        self.report_generator = report_generator_fn

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        header = QLabel("Diagnosis Reports")
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header.setStyleSheet("color: #1E293B;")

        self.refresh_btn = QPushButton("↻  Refresh")
        self.refresh_btn.clicked.connect(self.load_data)
        self.refresh_btn.setStyleSheet(self._btn_style("#EFF6FF", "#2563EB", "#BFDBFE"))

        self.export_btn = QPushButton("⬇  Export PDF")
        self.export_btn.clicked.connect(self.export_pdf)
        self.export_btn.setStyleSheet(self._btn_style("#2563EB", "white", "#2563EB", text_hover="white"))

        header_row.addWidget(header)
        header_row.addStretch()
        header_row.addWidget(self.refresh_btn)
        header_row.addWidget(self.export_btn)
        layout.addLayout(header_row)

        # Stats bar
        self.stats_label = QLabel("0 diagnoses recorded")
        self.stats_label.setStyleSheet("color: #64748B; font-size: 14px;")
        layout.addWidget(self.stats_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Timestamp", "Symptoms", "Diagnosis", "Confidence"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                gridline-color: #F1F5F9;
                font-size: 13px;
                background-color: white;
            }
            QTableWidget::item { padding: 10px 12px; color: #1E293B; }
            QTableWidget::item:selected { background-color: #EFF6FF; color: #2563EB; }
            QTableWidget::item:alternate { background-color: #F8FAFC; }
            QHeaderView::section {
                background-color: #2563EB;
                color: white;
                padding: 10px 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.table)

    def _btn_style(self, bg, text, border, text_hover=None):
        hover_text = text_hover or text
        return f"""
            QPushButton {{
                background-color: {bg}; color: {text};
                border: 1px solid {border}; border-radius: 8px;
                padding: 8px 18px; font-weight: 600; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #1D4ED8; color: {hover_text}; }}
        """

    def load_data(self):
        if not self.query_processor:
            return
        try:
            rows = self.query_processor.get_history()
        except Exception:
            rows = []

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            conf_str = f"{float(row[4]):.1f}%" if row[4] else "N/A"
            conf_val = float(row[4]) if row[4] else 0.0

            items = [
                QTableWidgetItem(str(row[0])),
                QTableWidgetItem(str(row[1])),
                QTableWidgetItem(str(row[2])),
                QTableWidgetItem(str(row[3]).title()),
                QTableWidgetItem(conf_str),
            ]

            items[0].setTextAlignment(Qt.AlignCenter)
            items[4].setTextAlignment(Qt.AlignCenter)

            # Color confidence cell
            conf_item = items[4]
            if conf_val >= 75:
                conf_item.setForeground(QColor("#10B981"))
            elif conf_val >= 40:
                conf_item.setForeground(QColor("#F59E0B"))
            else:
                conf_item.setForeground(QColor("#EF4444"))

            for j, item in enumerate(items):
                self.table.setItem(i, j, item)

        self.stats_label.setText(f"{len(rows)} diagnos{'is' if len(rows)==1 else 'es'} recorded")

    def export_pdf(self):
        if not self.report_generator:
            QMessageBox.warning(self, "Unavailable", "Report generator not initialized.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", f"IntelliExpert_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        if not path:
            return
        try:
            rows = self.query_processor.get_history() if self.query_processor else []
            self.report_generator(rows, path)
            QMessageBox.information(self, "Export Successful",
                                    f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
