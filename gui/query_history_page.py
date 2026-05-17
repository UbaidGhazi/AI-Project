"""
query_history_page.py
View all past AI diagnoses with search and delete functionality.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QAbstractItemView, QLineEdit,
                               QMessageBox, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class QueryHistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.query_processor = None
        self._all_rows = []
        self.init_ui()

    def set_query_processor(self, qp):
        self.query_processor = qp

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # ── Header ────────────────────────────────────────────────────────────
        header_row = QHBoxLayout()
        header = QLabel("Query History")
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header.setStyleSheet("color: #1E293B;")

        self.refresh_btn = QPushButton("↻  Refresh")
        self.refresh_btn.clicked.connect(self.load_data)
        self.refresh_btn.setStyleSheet(self._small_btn("#EFF6FF", "#2563EB"))

        self.clear_btn = QPushButton("🗑  Clear All")
        self.clear_btn.clicked.connect(self.clear_history)
        self.clear_btn.setStyleSheet(self._small_btn("#FEF2F2", "#EF4444"))

        header_row.addWidget(header)
        header_row.addStretch()
        header_row.addWidget(self.refresh_btn)
        header_row.addWidget(self.clear_btn)
        layout.addLayout(header_row)

        # ── Search ────────────────────────────────────────────────────────────
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("🔍  Filter by symptom, diagnosis or date…")
        self.search_field.setFixedHeight(40)
        self.search_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E2E8F0; border-radius: 20px;
                padding: 0 18px; font-size: 13px; background: white;
            }
            QLineEdit:focus { border: 1px solid #3B82F6; }
        """)
        self.search_field.textChanged.connect(self._filter)
        layout.addWidget(self.search_field)

        # ── Stats strip ───────────────────────────────────────────────────────
        self.stats_lbl = QLabel("")
        self.stats_lbl.setStyleSheet("color: #64748B; font-size: 13px;")
        layout.addWidget(self.stats_lbl)

        # ── Table ─────────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["#", "Timestamp", "Symptoms", "Diagnosis", "Confidence"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E2E8F0; border-radius: 10px;
                gridline-color: #F1F5F9; font-size: 13px; background: white;
            }
            QTableWidget::item { padding: 10px 12px; color: #1E293B; }
            QTableWidget::item:selected { background-color: #EFF6FF; color: #2563EB; }
            QTableWidget::item:alternate { background-color: #F8FAFC; }
            QHeaderView::section {
                background-color: #1E40AF; color: white;
                padding: 10px 12px; border: none;
                font-weight: bold; font-size: 13px;
            }
        """)
        layout.addWidget(self.table)

    def _small_btn(self, bg, text_color):
        return f"""
            QPushButton {{
                background-color: {bg}; color: {text_color};
                border: 1px solid {text_color}33; border-radius: 8px;
                padding: 7px 16px; font-weight: 600; font-size: 12px;
            }}
            QPushButton:hover {{ opacity: 0.85; }}
        """

    def load_data(self):
        if not self.query_processor:
            return
        try:
            self._all_rows = self.query_processor.get_history()
        except Exception:
            self._all_rows = []
        self._populate(self._all_rows)

    def _filter(self, text: str):
        q = text.lower()
        filtered = [r for r in self._all_rows
                    if q in str(r[1]).lower()
                    or q in str(r[2]).lower()
                    or q in str(r[3]).lower()]
        self._populate(filtered)

    def _populate(self, rows):
        self.table.setRowCount(len(rows))
        avg_conf = 0.0
        for i, row in enumerate(rows):
            conf = float(row[4]) if row[4] else 0.0
            avg_conf += conf
            items = [
                QTableWidgetItem(str(row[0])),
                QTableWidgetItem(str(row[1])),
                QTableWidgetItem(str(row[2])),
                QTableWidgetItem(str(row[3]).title()),
                QTableWidgetItem(f"{conf:.1f}%"),
            ]
            items[0].setTextAlignment(Qt.AlignCenter)
            items[4].setTextAlignment(Qt.AlignCenter)
            # Confidence color
            color = ("#10B981" if conf >= 75 else "#F59E0B" if conf >= 40 else "#EF4444")
            items[4].setForeground(QColor(color))
            for j, item in enumerate(items):
                self.table.setItem(i, j, item)

        n = len(rows)
        avg = avg_conf / n if n > 0 else 0.0
        self.stats_lbl.setText(
            f"Showing {n} record{'s' if n != 1 else ''}  ·  "
            f"Avg. Confidence: {avg:.1f}%"
        )

    def clear_history(self):
        if not self.query_processor:
            return
        confirm = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to delete all diagnosis history?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            try:
                cursor = self.query_processor.conn.cursor()
                cursor.execute("DELETE FROM queries")
                self.query_processor.conn.commit()
                self._all_rows = []
                self._populate([])
                QMessageBox.information(self, "Cleared", "All history has been deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
