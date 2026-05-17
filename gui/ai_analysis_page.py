"""
ai_analysis_page.py
Interactive AI analytics dashboard with embedded Matplotlib charts.
"""

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import Counter

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGridLayout, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


BLUE_PALETTE = ["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE",
                "#1D4ED8", "#1E40AF", "#7C3AED", "#A78BFA", "#C4B5FD"]


class ChartCard(QFrame):
    def __init__(self, title: str, fig: Figure):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)

        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl.setStyleSheet("color: #1E293B; background: transparent; border: none;")
        layout.addWidget(lbl)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(canvas)


class AIAnalysisPage(QWidget):
    def __init__(self):
        super().__init__()
        self.query_processor = None
        self.init_ui()

    def set_query_processor(self, qp):
        self.query_processor = qp

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # Header row
        header_row = QHBoxLayout()
        header = QLabel("AI Analysis & Insights")
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header.setStyleSheet("color: #1E293B;")

        self.refresh_btn = QPushButton("↻  Refresh Charts")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #EFF6FF;
                color: #2563EB;
                border: 1px solid #BFDBFE;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #DBEAFE; }
        """)
        self.refresh_btn.clicked.connect(self.load_charts)

        header_row.addWidget(header)
        header_row.addStretch()
        header_row.addWidget(self.refresh_btn)
        self.main_layout.addLayout(header_row)

        # Placeholder text until data loads
        self.placeholder = QLabel("Click 'Refresh Charts' or run a Diagnosis to see analytics.")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color: #94A3B8; font-size: 16px;")
        self.main_layout.addWidget(self.placeholder)
        self.main_layout.addStretch()

    def load_charts(self):
        # Clear existing widgets below header row
        while self.main_layout.count() > 1:
            item = self.main_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        rows = []
        if self.query_processor:
            try:
                rows = self.query_processor.get_history()
            except Exception:
                rows = []

        if not rows:
            lbl = QLabel("No diagnosis data yet.\nRun diagnoses in the Diagnosis tab to see AI analytics here.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #94A3B8; font-size: 15px;")
            self.main_layout.addWidget(lbl)
            self.main_layout.addStretch()
            return

        # ── Prepare data ───────────────────────────────────────────────────
        diseases = [r[3].title() for r in rows if r[3]]
        confidences = [float(r[4]) for r in rows if r[4]]
        symptom_raw = [s.strip() for r in rows for s in r[2].split(",") if r[2]]

        disease_counts = Counter(diseases)
        symptom_counts = Counter(symptom_raw).most_common(8)

        grid = QGridLayout()
        grid.setSpacing(20)

        # 1. Disease distribution bar chart
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        fig1.patch.set_facecolor("white")
        ax1.set_facecolor("#F8FAFC")
        labels = list(disease_counts.keys())
        vals = list(disease_counts.values())
        bars = ax1.bar(labels, vals, color=BLUE_PALETTE[:len(labels)], edgecolor="white",
                       linewidth=0.8, width=0.6)
        ax1.set_title("Diagnoses by Disease", fontsize=11, fontweight="bold", color="#1E293B")
        ax1.set_ylabel("Count", fontsize=9, color="#64748B")
        ax1.tick_params(axis="x", rotation=30, labelsize=8, colors="#475569")
        ax1.tick_params(axis="y", labelsize=8, colors="#475569")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.spines["left"].set_color("#E2E8F0")
        ax1.spines["bottom"].set_color("#E2E8F0")
        for bar, v in zip(bars, vals):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                     str(v), ha="center", va="bottom", fontsize=8, color="#1E293B")
        fig1.tight_layout()
        grid.addWidget(ChartCard("🏥 Disease Distribution", fig1), 0, 0)

        # 2. Confidence distribution
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        fig2.patch.set_facecolor("white")
        ax2.set_facecolor("#F8FAFC")
        if confidences:
            ax2.hist(confidences, bins=10, color="#3B82F6", edgecolor="white",
                     linewidth=0.8, alpha=0.85)
        ax2.set_title("AI Confidence Distribution", fontsize=11, fontweight="bold", color="#1E293B")
        ax2.set_xlabel("Confidence (%)", fontsize=9, color="#64748B")
        ax2.set_ylabel("Frequency", fontsize=9, color="#64748B")
        ax2.tick_params(labelsize=8, colors="#475569")
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.spines["left"].set_color("#E2E8F0")
        ax2.spines["bottom"].set_color("#E2E8F0")
        fig2.tight_layout()
        grid.addWidget(ChartCard("📊 Confidence Distribution", fig2), 0, 1)

        # 3. Pie chart for disease share
        fig3, ax3 = plt.subplots(figsize=(5, 3))
        fig3.patch.set_facecolor("white")
        if disease_counts:
            wedges, texts, autotexts = ax3.pie(
                disease_counts.values(),
                labels=disease_counts.keys(),
                autopct="%1.0f%%",
                colors=BLUE_PALETTE[:len(disease_counts)],
                startangle=140,
                pctdistance=0.8,
                wedgeprops={"edgecolor": "white", "linewidth": 2},
            )
            for t in texts:
                t.set_fontsize(8)
                t.set_color("#475569")
            for at in autotexts:
                at.set_fontsize(7)
                at.set_color("white")
                at.set_fontweight("bold")
        ax3.set_title("Disease Share", fontsize=11, fontweight="bold", color="#1E293B")
        fig3.tight_layout()
        grid.addWidget(ChartCard("🍩 Disease Share", fig3), 1, 0)

        # 4. Top symptoms bar
        fig4, ax4 = plt.subplots(figsize=(5, 3))
        fig4.patch.set_facecolor("white")
        ax4.set_facecolor("#F8FAFC")
        if symptom_counts:
            syms, cnts = zip(*symptom_counts)
            syms_short = [s.replace("_", " ").title()[:12] for s in syms]
            ax4.barh(syms_short, cnts, color=BLUE_PALETTE[:len(syms)],
                     edgecolor="white", linewidth=0.8)
        ax4.set_title("Top Reported Symptoms", fontsize=11, fontweight="bold", color="#1E293B")
        ax4.set_xlabel("Frequency", fontsize=9, color="#64748B")
        ax4.tick_params(axis="y", labelsize=8, colors="#475569")
        ax4.tick_params(axis="x", labelsize=8, colors="#475569")
        ax4.spines["top"].set_visible(False)
        ax4.spines["right"].set_visible(False)
        ax4.spines["left"].set_color("#E2E8F0")
        ax4.spines["bottom"].set_color("#E2E8F0")
        ax4.invert_yaxis()
        fig4.tight_layout()
        grid.addWidget(ChartCard("🤒 Top Symptoms", fig4), 1, 1)

        self.main_layout.addLayout(grid)
