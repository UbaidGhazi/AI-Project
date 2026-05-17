from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from utils.animations import fade_in

class SplashScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("IntelliExpert AI")
        title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        title.setStyleSheet("color: #2563EB;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Hybrid Symbolic Intelligence System")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #64748B;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setFixedSize(400, 8)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #E2E8F0;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 4px;
            }
        """)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(40)
        layout.addWidget(self.progress, alignment=Qt.AlignCenter)
        
        # Central widget for background
        bg_widget = QWidget()
        bg_widget.setObjectName("SplashBg")
        bg_widget.setStyleSheet("""
            #SplashBg {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 20px;
                border: 1px solid #E2E8F0;
            }
        """)
        bg_widget.setLayout(layout)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(bg_widget)
        
        fade_in(self, 800)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)
        self.counter = 0

    def update_progress(self):
        self.counter += 1
        self.progress.setValue(self.counter)
        if self.counter >= 100:
            self.timer.stop()
            self.main_window.show_main()
            self.close()
