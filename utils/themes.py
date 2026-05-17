MAIN_THEME = """
QWidget {
    background-color: #F8FAFC;
    font-family: "Segoe UI", "Inter", "Poppins", sans-serif;
    color: #1E293B;
}

/* Sidebar */
#Sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

#Sidebar QPushButton {
    text-align: left;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    margin: 4px 12px;
    font-size: 14px;
    font-weight: 500;
    color: #64748B;
    background-color: transparent;
}

#Sidebar QPushButton:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

#Sidebar QPushButton:checked {
    background-color: #EFF6FF;
    color: #2563EB;
    font-weight: 600;
}

/* Cards */
.Card {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
}

.Card:hover {
    border: 1px solid #CBD5E1;
}

/* Inputs and Buttons */
QLineEdit {
    padding: 12px;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    background-color: #FFFFFF;
    font-size: 14px;
}

QLineEdit:focus {
    border: 1px solid #3B82F6;
}

QPushButton.Primary {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton.Primary:hover {
    background-color: #1D4ED8;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #F1F5F9;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}

/* Progress Bars */
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #E2E8F0;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #60A5FA);
    border-radius: 4px;
}
"""
