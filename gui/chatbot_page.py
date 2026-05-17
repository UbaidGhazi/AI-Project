"""
chatbot_page.py
Premium AI Chatbot page powered by the local RAG engine.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QLineEdit, QFrame,
                               QSizePolicy)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont


# ── Worker thread so RAG doesn't block the UI ────────────────────────────────
class ChatWorker(QThread):
    response_ready = Signal(str)

    def __init__(self, engine, message):
        super().__init__()
        self.engine = engine
        self.message = message

    def run(self):
        reply = self.engine.chat(self.message)
        self.response_ready.emit(reply)


# ── Individual message bubble ─────────────────────────────────────────────────
class MessageBubble(QFrame):
    def __init__(self, text: str, is_user: bool):
        super().__init__()
        self.setWordWrap = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setFont(QFont("Segoe UI", 13))
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setOpenExternalLinks(False)

        if is_user:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 #2563EB, stop:1 #60A5FA);
                    border-radius: 16px 16px 4px 16px;
                    margin-left: 80px;
                }
            """)
            lbl.setStyleSheet("color: white; background: transparent;")
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #F1F5F9;
                    border: 1px solid #E2E8F0;
                    border-radius: 16px 16px 16px 4px;
                    margin-right: 80px;
                }
            """)
            lbl.setStyleSheet("color: #1E293B; background: transparent;")

        layout.addWidget(lbl)


class ChatbotPage(QWidget):
    def __init__(self, rag_engine=None):
        super().__init__()
        self.rag_engine = rag_engine
        self.worker = None
        self.init_ui()

    def set_engine(self, engine):
        self.rag_engine = engine

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                             "stop:0 #1E40AF, stop:1 #3B82F6); border: none;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)

        bot_icon = QLabel("🤖")
        bot_icon.setFont(QFont("Segoe UI", 24))
        title = QLabel("IntelliBot — AI Medical Assistant")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        status = QLabel("● Online  |  RAG-Powered")
        status.setStyleSheet("color: #93C5FD; font-size: 12px; background: transparent;")

        h_layout.addWidget(bot_icon)
        h_layout.addSpacing(10)
        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(status)
        layout.addWidget(header)

        # ── Chat scroll area ──────────────────────────────────────────────────
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background-color: #F8FAFC;")

        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: #F8FAFC;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_layout.setSpacing(12)
        self.chat_layout.addStretch()

        self.scroll.setWidget(self.chat_container)
        layout.addWidget(self.scroll)

        # ── Typing indicator ──────────────────────────────────────────────────
        self.typing_lbl = QLabel("IntelliBot is thinking…")
        self.typing_lbl.setStyleSheet("color: #94A3B8; font-size: 13px; padding: 4px 24px;")
        self.typing_lbl.hide()
        layout.addWidget(self.typing_lbl)

        # ── Input bar ─────────────────────────────────────────────────────────
        input_frame = QWidget()
        input_frame.setStyleSheet("background: white; border-top: 1px solid #E2E8F0;")
        input_frame.setFixedHeight(70)
        i_layout = QHBoxLayout(input_frame)
        i_layout.setContentsMargins(16, 10, 16, 10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me about symptoms, medicines, precautions…")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E2E8F0;
                border-radius: 24px;
                padding: 10px 20px;
                font-size: 14px;
                background-color: #F8FAFC;
            }
            QLineEdit:focus { border: 1px solid #3B82F6; }
        """)
        self.input_field.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton("Send →")
        self.send_btn.setFixedHeight(42)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #2563EB, stop:1 #60A5FA);
                color: white;
                border: none;
                border-radius: 21px;
                padding: 0 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background: #1D4ED8; }
        """)
        self.send_btn.clicked.connect(self.send_message)

        i_layout.addWidget(self.input_field)
        i_layout.addWidget(self.send_btn)
        layout.addWidget(input_frame)

        # Starter greeting
        QTimer.singleShot(400, self._show_welcome)

    def _show_welcome(self):
        welcome = ("👋 Hello! I'm **IntelliBot**, your AI Medical Assistant powered by the "
                   "IntelliExpert knowledge base.\n\n"
                   "You can ask me:\n"
                   "• *What are the symptoms of flu?*\n"
                   "• *What medicines are used for migraine?*\n"
                   "• *Show my diagnosis history*\n"
                   "• *List all diseases*\n\n"
                   "How can I help you today?")
        self._add_bubble(welcome, is_user=False)

    def send_message(self):
        text = self.input_field.text().strip()
        if not text or self.worker is not None:
            return

        self.input_field.clear()
        self._add_bubble(text, is_user=True)

        if not self.rag_engine:
            self._add_bubble("⚠️ RAG engine not initialized. Please restart the application.", is_user=False)
            return

        self.typing_lbl.show()
        self.send_btn.setEnabled(False)

        self.worker = ChatWorker(self.rag_engine, text)
        self.worker.response_ready.connect(self._on_response)
        self.worker.start()

    def _on_response(self, reply: str):
        self.typing_lbl.hide()
        self.send_btn.setEnabled(True)
        self.worker = None
        self._add_bubble(reply, is_user=False)

    def _add_bubble(self, text: str, is_user: bool):
        bubble = MessageBubble(text, is_user)
        # Insert before the stretch at the end
        count = self.chat_layout.count()
        self.chat_layout.insertWidget(count - 1, bubble)
        # Scroll to bottom
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))
