import os
import sys
from flask import Flask, render_template, request, jsonify, send_file

# Add parent directory to path so we can import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.inference_engine import InferenceEngine
from backend.explanation_engine import ExplanationEngine
from backend.recommendation_engine import RecommendationEngine
from backend.query_processor import QueryProcessor
from backend.rag_engine import RAGEngine, MEDICAL_CORPUS
from backend.report_generator import generate_pdf_report
from utils.constants import ALL_SYMPTOMS

app = Flask(__name__)

# Initialize Engines
try:
    inference_engine = InferenceEngine()
    explanation_engine = ExplanationEngine()
    recommendation_engine = RecommendationEngine()
except Exception as e:
    print(f"[WARN] Prolog engine unavailable: {e}")
    inference_engine = None
    explanation_engine = None
    recommendation_engine = None

query_processor = QueryProcessor()
rag_engine = RAGEngine()
rag_engine.set_query_processor(query_processor)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify(ALL_SYMPTOMS)

@app.route('/api/set_api_key', methods=['POST'])
def set_api_key():
    data = request.json
    api_key = data.get('api_key', '')
    rag_engine.set_api_key(api_key)
    return jsonify({'success': True})

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    symptoms = data.get('symptoms', [])
    
    if not symptoms:
        return jsonify({'success': False, 'message': 'No symptoms provided.'}), 400
        
    # Standardize engines
    global inference_engine, explanation_engine, recommendation_engine
    if not inference_engine:
        inference_engine = InferenceEngine()
    if not explanation_engine:
        explanation_engine = ExplanationEngine()
    if not recommendation_engine:
        recommendation_engine = RecommendationEngine()

    diagnoses = inference_engine.diagnose(symptoms)
    
    # Log to DB
    if diagnoses:
        top = diagnoses[0]
        query_processor.log_query(symptoms, top["disease"], top["confidence"])
        
        # Add rich explanations and recommendations
        for d in diagnoses:
            d['explanation'] = explanation_engine.generate_explanation(d)
            d['details'] = recommendation_engine.get_details(d['disease'], symptoms)
            
    return jsonify({
        'success': True,
        'diagnoses': diagnoses
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    if not message:
        return jsonify({'reply': 'I didn\'t catch that. Could you repeat?'}), 400
    
    reply = rag_engine.chat(message)
    return jsonify({'reply': reply})

@app.route('/api/history', methods=['GET'])
def get_history():
    rows = query_processor.get_history()
    history = []
    for r in rows:
        history.append({
            'id': r[0],
            'timestamp': r[1],
            'symptoms': r[2],
            'diagnosis': r[3].title(),
            'confidence': f"{r[4]:.1f}%" if r[4] else "N/A"
        })
    return jsonify(history)

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    cursor = query_processor.conn.cursor()
    cursor.execute("DELETE FROM queries")
    query_processor.conn.commit()
    return jsonify({'success': True})

@app.route('/api/export_pdf', methods=['GET'])
def export_pdf():
    rows = query_processor.get_history()
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'report.pdf')
    generate_pdf_report(rows, pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name='IntelliExpert_Report.pdf')

@app.route('/api/knowledge_base', methods=['GET'])
def get_knowledge_base():
    return jsonify(MEDICAL_CORPUS)

if __name__ == '__main__':
    print("--------------------------------------------------")
    print(" IntelliExpert AI Server running at:")
    print(" -> http://localhost:5000")
    print("--------------------------------------------------")
    app.run(host='0.0.0.0', port=5000, debug=True)
