"""
knowledge_base_page.py
Searchable, interactive viewer for the entire Prolog + Python knowledge base.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QFrame, QLineEdit,
                               QGridLayout, QTabWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from backend.rag_engine import MEDICAL_CORPUS


class DiseaseCard(QFrame):
    def __init__(self, disease: str, info: dict):
        super().__init__()
        self.setObjectName("DiseaseCard")
        self.setStyleSheet("""
            #DiseaseCard {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
            #DiseaseCard:hover {
                border: 1px solid #3B82F6;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        # Title
        title = QLabel(info["full_name"])
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2563EB; background: transparent; border: none;")
        layout.addWidget(title)

        # Description
        desc = QLabel(info["description"])
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #475569; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(desc)

        layout.addSpacing(4)
        self._add_section(layout, "🩺 Symptoms", info["symptoms"], "#1E293B")
        self._add_section(layout, "💊 Medicines", info["medicines"], "#7C3AED")
        self._add_section(layout, "✅ Recommendations", info["recommendations"], "#059669")
        self._add_section(layout, "🛡️ Precautions", info["precautions"], "#D97706")

        # Footer pills
        footer = QHBoxLayout()
        sev = QLabel(f"⚠ {info['severity']}")
        sev.setStyleSheet("font-size: 11px; color: #EF4444; background: #FEF2F2; "
                          "border-radius: 6px; padding: 2px 8px; border: none;")
        cont = QLabel("🦠 Contagious" if info["contagious"] else "🔒 Not Contagious")
        cont.setStyleSheet(f"font-size: 11px; color: {'#DC2626' if info['contagious'] else '#059669'}; "
                           f"background: {'#FEF2F2' if info['contagious'] else '#ECFDF5'}; "
                           "border-radius: 6px; padding: 2px 8px; border: none;")
        footer.addWidget(sev)
        footer.addWidget(cont)
        footer.addStretch()
        layout.addLayout(footer)

    def _add_section(self, layout, heading, items, color):
        lbl = QLabel(f"<b>{heading}:</b> {', '.join(items)}")
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color: {color}; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(lbl)


class KnowledgeBasePage(QWidget):
    def __init__(self):
        super().__init__()
        self.all_cards = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        header = QLabel("Knowledge Base")
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header.setStyleSheet("color: #1E293B;")
        header_row.addWidget(header)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Stats bar
        stats = QLabel(
            f"📚 {len(MEDICAL_CORPUS)} Diseases  ·  "
            f"🩺 {sum(len(v['symptoms']) for v in MEDICAL_CORPUS.values())} Symptoms  ·  "
            f"💊 {sum(len(v['medicines']) for v in MEDICAL_CORPUS.values())} Medicines  ·  "
            f"✅ {sum(len(v['recommendations']) for v in MEDICAL_CORPUS.values())} Recommendations"
        )
        stats.setStyleSheet("color: #2563EB; font-size: 13px; font-weight: 600;")
        layout.addWidget(stats)

        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search diseases, symptoms, medicines…")
        self.search.setFixedHeight(44)
        self.search.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E2E8F0;
                border-radius: 22px;
                padding: 0 20px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus { border: 1px solid #3B82F6; }
        """)
        self.search.textChanged.connect(self.filter_cards)
        layout.addWidget(self.search)

        # Scroll area with card grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(16)

        row, col = 0, 0
        for disease, info in MEDICAL_CORPUS.items():
            card = DiseaseCard(disease, info)
            card.setProperty("disease_key", disease)
            card.setProperty("search_text",
                             f"{disease} {info['full_name']} {' '.join(info['symptoms'])} {' '.join(info['medicines'])}".lower())
            self.all_cards.append(card)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)

    def filter_cards(self, text: str):
        query = text.lower().strip()
        row, col = 0, 0
        for card in self.all_cards:
            visible = not query or query in card.property("search_text")
            card.setVisible(visible)
            if visible:
                self.grid_layout.addWidget(card, row, col)
                col += 1
                if col > 1:
                    col = 0
                    row += 1
