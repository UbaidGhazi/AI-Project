"""
gui_main.py
IntelliExpert AI — PySide6 Desktop GUI entry point.
"""

import sys
import os

from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget,
                               QHBoxLayout, QVBoxLayout, QWidget, QMessageBox)
from PySide6.QtCore import Qt

# ── Backend ──────────────────────────────────────────────────────────────────
from backend.inference_engine import InferenceEngine
from backend.explanation_engine import ExplanationEngine
from backend.recommendation_engine import RecommendationEngine
from backend.query_processor import QueryProcessor
from backend.rag_engine import RAGEngine
from backend.report_generator import generate_pdf_report

# ── GUI ───────────────────────────────────────────────────────────────────────
from gui.splash_screen import SplashScreen
from gui.sidebar import Sidebar
from gui.navbar import Navbar
from gui.dashboard import Dashboard
from gui.diagnosis_page import DiagnosisPage
from gui.results_page import ResultsPage
from gui.chatbot_page import ChatbotPage
from gui.ai_analysis_page import AIAnalysisPage
from gui.reports_page import ReportsPage
from gui.knowledge_base_page import KnowledgeBasePage
from gui.query_history_page import QueryHistoryPage
from gui.settings import SettingsPage

from utils.themes import MAIN_THEME

# Stack page indices (must match sidebar TABS order)
IDX_DASHBOARD     = 0
IDX_DIAGNOSIS     = 1
IDX_CHATBOT       = 2
IDX_AI_ANALYSIS   = 3
IDX_REPORTS       = 4
IDX_KNOWLEDGE     = 5
IDX_HISTORY       = 6
IDX_SETTINGS      = 7
IDX_RESULTS       = 8   # Not in sidebar; navigated to programmatically


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IntelliExpert AI — Symbolic Intelligence Platform")
        self.resize(1380, 860)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(MAIN_THEME)

        # Engines initialised after splash
        self.inference_engine      = None
        self.explanation_engine    = None
        self.recommendation_engine = None
        self.query_processor       = None
        self.rag_engine            = None

        self.splash = SplashScreen(self)
        self.splash.show()

    # ── Initialisation ────────────────────────────────────────────────────────

    def _init_engines(self):
        # Prolog (optional — degrades gracefully if SWI-Prolog absent)
        try:
            self.inference_engine      = InferenceEngine()
            self.explanation_engine    = ExplanationEngine()
            self.recommendation_engine = RecommendationEngine()
        except Exception as e:
            print(f"[WARN] Prolog engine unavailable: {e}")

        # Always-available engines
        self.query_processor = QueryProcessor()
        self.rag_engine      = RAGEngine()
        self.rag_engine.set_query_processor(self.query_processor)

    # ── Build main window ─────────────────────────────────────────────────────

    def show_main(self):
        self._init_engines()

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.tab_changed.connect(self.switch_tab)
        root.addWidget(self.sidebar)

        # Right panel
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.navbar = Navbar()
        right_layout.addWidget(self.navbar)

        # ── Pages ─────────────────────────────────────────────────────────────
        self.stack = QStackedWidget()

        # 0 Dashboard
        self.dashboard = Dashboard()
        self.stack.addWidget(self.dashboard)

        # 1 Diagnosis
        self.diagnosis = DiagnosisPage()
        self.diagnosis.diagnosis_requested.connect(self.process_diagnosis)
        self.stack.addWidget(self.diagnosis)

        # 2 Chatbot
        self.chatbot = ChatbotPage(self.rag_engine)
        self.stack.addWidget(self.chatbot)

        # 3 AI Analysis
        self.ai_analysis = AIAnalysisPage()
        self.ai_analysis.set_query_processor(self.query_processor)
        self.stack.addWidget(self.ai_analysis)

        # 4 Reports
        self.reports = ReportsPage()
        self.reports.set_dependencies(self.query_processor, generate_pdf_report)
        self.stack.addWidget(self.reports)

        # 5 Knowledge Base
        self.knowledge_base = KnowledgeBasePage()
        self.stack.addWidget(self.knowledge_base)

        # 6 Query History
        self.query_history = QueryHistoryPage()
        self.query_history.set_query_processor(self.query_processor)
        self.stack.addWidget(self.query_history)

        # 7 Settings
        self.settings_page = SettingsPage()
        self.settings_page.set_query_processor(self.query_processor)
        self.stack.addWidget(self.settings_page)

        # 8 Results (reached programmatically after diagnosis)
        self.results = ResultsPage()
        self.results.go_back.connect(lambda: self.switch_tab(IDX_DIAGNOSIS))
        self.stack.addWidget(self.results)

        right_layout.addWidget(self.stack)
        root.addWidget(right)

        self.show()

    # ── Navigation ────────────────────────────────────────────────────────────

    def switch_tab(self, index: int):
        self.stack.setCurrentIndex(index)
        # Sync sidebar (results page has no sidebar button)
        if index < len(self.sidebar.buttons):
            self.sidebar.set_active(index)

        # Lazy-load data for pages that need it
        if index == IDX_HISTORY:
            self.query_history.load_data()
        elif index == IDX_REPORTS:
            self.reports.load_data()

    # ── Diagnosis flow ────────────────────────────────────────────────────────

    def process_diagnosis(self, symptoms: list[str]):
        if self.inference_engine is None:
            self._init_engines()
            if self.inference_engine is None:
                QMessageBox.critical(
                    self, "System Error",
                    "Could not initialize the logical inference diagnostic engine."
                )
                return


        diagnoses = self.inference_engine.diagnose(symptoms)

        # Log to DB
        if diagnoses:
            top = diagnoses[0]
            try:
                self.query_processor.log_query(symptoms, top["disease"], top["confidence"])
            except Exception as e:
                print(f"[WARN] DB log failed: {e}")

        self.results.display_results(
            diagnoses, self.explanation_engine, self.recommendation_engine
        )
        self.stack.setCurrentIndex(IDX_RESULTS)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("IntelliExpert AI")
    window = MainWindow()
    sys.exit(app.exec())
