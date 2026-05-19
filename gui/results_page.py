from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal

class ResultsPage(QWidget):
    go_back = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        
        header_layout = QHBoxLayout()
        btn_back = QPushButton("← Back to Diagnosis")
        btn_back.setStyleSheet("color: #3B82F6; font-weight: bold; border: none; background: transparent; font-size: 14px;")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.go_back.emit)
        header_layout.addWidget(btn_back)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)
        
        self.title = QLabel("AI Diagnosis Results")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        self.layout.addWidget(self.title)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background-color: transparent;")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.scroll.setWidget(self.container)
        
        self.layout.addWidget(self.scroll)

    def display_results(self, diagnoses, explanation_engine, recommendation_engine):
        # Clear previous results
        for i in reversed(range(self.container_layout.count())): 
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        if not diagnoses:
            lbl = QLabel("No matching diseases found based on provided symptoms.")
            lbl.setStyleSheet("font-size: 16px; color: #EF4444;")
            self.container_layout.addWidget(lbl)
            self.container_layout.addStretch()
            return
            
        for diag in diagnoses:
            disease = diag['disease']
            confidence = diag['confidence']
            
            card = QFrame()
            card.setProperty("class", "Card")
            card_layout = QVBoxLayout(card)
            
            header = QLabel(f"{disease.replace('_', ' ').title()} ({confidence:.1f}% Confidence)")
            header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2563EB;")
            card_layout.addWidget(header)
            
            # Explanation
            explanation = explanation_engine.generate_explanation(diag)
            lbl_exp = QLabel(explanation)
            lbl_exp.setWordWrap(True)
            lbl_exp.setStyleSheet("color: #475569; font-size: 14px; font-family: monospace; background-color: #F8FAFC; padding: 10px; border-radius: 6px;")
            card_layout.addWidget(lbl_exp)
            
            # Recommendations and Precautions
            details = recommendation_engine.get_details(disease, diag.get('matched_symptoms'))
            if details['recommendations']:
                lbl_rec = QLabel("📋 Care Guidelines: " + ", ".join(details['recommendations']))
                lbl_rec.setWordWrap(True)
                lbl_rec.setStyleSheet("color: #10B981; font-weight: 600; font-size: 14px; margin-top: 10px;")
                card_layout.addWidget(lbl_rec)
                
            if details['precautions']:
                lbl_prec = QLabel("🛡️ Precautions: " + ", ".join(details['precautions']))
                lbl_prec.setWordWrap(True)
                lbl_prec.setStyleSheet("color: #E2E8F0; font-weight: 600; font-size: 14px; color: #D97706; margin-top: 4px;")
                card_layout.addWidget(lbl_prec)
                
            if details['medicines']:
                lbl_med = QLabel("💊 Recommended Safe Medicines: " + ", ".join(details['medicines']))
                lbl_med.setWordWrap(True)
                lbl_med.setStyleSheet("color: #8B5CF6; font-weight: 600; font-size: 14px; margin-top: 4px;")
                card_layout.addWidget(lbl_med)

                
            self.container_layout.addWidget(card)
            self.container_layout.addSpacing(15)
            
        self.container_layout.addStretch()
