from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QGridLayout, QCheckBox,
                               QProgressBar)
from PySide6.QtCore import Qt, Signal, QTimer
from utils.constants import ALL_SYMPTOMS

class DiagnosisPage(QWidget):
    diagnosis_requested = Signal(list)

    def __init__(self):
        super().__init__()
        self.selected_symptoms = set()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("AI Symptom Analysis")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        layout.addWidget(header)
        
        desc = QLabel("Select the symptoms you are experiencing. Our AI will analyze them using the Prolog Knowledge Base.")
        desc.setStyleSheet("color: #64748B; font-size: 14px;")
        layout.addWidget(desc)
        layout.addSpacing(20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(15)
        
        row, col = 0, 0
        for symptom in ALL_SYMPTOMS:
            cb = QCheckBox(symptom.replace('_', ' ').title())
            cb.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    padding: 8px;
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 6px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox:hover {
                    border: 1px solid #3B82F6;
                }
            """)
            cb.stateChanged.connect(lambda state, s=symptom: self.toggle_symptom(state, s))
            grid.addWidget(cb, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.hide()
        layout.addWidget(self.progress)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_submit = QPushButton("Run AI Diagnosis")
        self.btn_submit.setProperty("class", "Primary")
        self.btn_submit.clicked.connect(self.on_submit)
        btn_layout.addWidget(self.btn_submit)
        
        layout.addLayout(btn_layout)

    def toggle_symptom(self, state, symptom):
        if state == Qt.Checked.value:
            self.selected_symptoms.add(symptom)
        else:
            self.selected_symptoms.discard(symptom)

    def on_submit(self):
        if not self.selected_symptoms:
            return
            
        self.btn_submit.setEnabled(False)
        self.progress.show()
        self.progress.setRange(0, 0) # Indeterminate mode for loading effect
        
        # Simulate AI processing time for UX
        QTimer.singleShot(1500, self.finish_processing)
        
    def finish_processing(self):
        self.progress.hide()
        self.btn_submit.setEnabled(True)
        self.diagnosis_requested.emit(list(self.selected_symptoms))
