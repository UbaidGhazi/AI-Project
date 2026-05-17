# IntelliExpert AI

A futuristic, enterprise-grade AI Medical Diagnosis Expert System that uses symbolic reasoning (Prolog) integrated with a modern Python (PySide6) GUI.

## Features
- **Prolog-based Reasoning Engine**: Employs an intelligent inference system using a knowledge base of facts and rules.
- **Explainable AI**: The system provides clear explanations detailing *why* a particular diagnosis was made and which rules were triggered.
- **Enterprise UI/UX**: Designed using modern principles—clean typography, smooth animations, and a rich dashboard.
- **Real-Time Database**: A SQLite backend automatically logs queries, confidence rates, and symptoms.
- **Multi-page Dashboard**: Fully built out dashboard, including diagnosis execution, AI results analysis, and animated system monitoring elements.

## Prerequisites
- Python 3.12+
- SWI-Prolog installed on your system.

## Setup Instructions

1. Install SWI-Prolog
Make sure you install SWI-Prolog and add its `bin` directory to your System PATH environment variable so that PySWIP can find the `libswipl.dll`.

2. Install Requirements
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python main.py
```

## Structure
- `main.py`: Entry point for the application.
- `prolog/`: Contains knowledge base, symptoms, recommendations, and logical inference rules.
- `backend/`: Provides Python-Prolog connectivity, query processing, explainability, and database logic.
- `gui/`: Houses modern PySide6 pages, including the dashboard, diagnosis page, splash screen, and navbar.
- `utils/`: Theme constants, UI constants, and QPropertyAnimation configurations.
