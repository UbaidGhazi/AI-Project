import React, { useState, useEffect, useRef } from 'react';
import medicalBanner from './assets/medical_banner.png';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [symptoms, setSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  
  // Diagnosis states
  const [diagnosing, setDiagnosing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [diagnoses, setDiagnoses] = useState([]);
  
  // Chat states
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: `👋 Hello! I am <b>IntelliBot</b>, your hybrid AI assistant.<br/>I can answer detailed medical questions based on our integrated Prolog rule-base and clinical history.<br/><br/>Feel free to query me about symptoms, precautions, treatments or medicines!`
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatBottomRef = useRef(null);

  // Knowledge base and History states
  const [kb, setKb] = useState({});
  const [kbSearch, setKbSearch] = useState('');
  const [history, setHistory] = useState([]);
  const [apiKey, setApiKey] = useState('');

  // Auto scroll chat to bottom
  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, chatLoading]);

  // Load initial data
  useEffect(() => {
    fetchSymptoms();
    fetchKnowledgeBase();
    fetchHistory();
    const savedKey = localStorage.getItem('gemini_api_key') || '';
    if (savedKey) {
      setApiKey(savedKey);
      syncApiKey(savedKey);
    }
  }, []);

  const fetchSymptoms = async () => {
    try {
      const res = await fetch('/api/symptoms');
      const data = await res.json();
      setSymptoms(data);
    } catch (e) {
      console.error('Failed to load symptoms:', e);
    }
  };

  const fetchKnowledgeBase = async () => {
    try {
      const res = await fetch('/api/knowledge_base');
      const data = await res.json();
      setKb(data);
    } catch (e) {
      console.error('Failed to load knowledge base:', e);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/history');
      const data = await res.json();
      setHistory(data);
    } catch (e) {
      console.error('Failed to load history:', e);
    }
  };

  const syncApiKey = async (key) => {
    try {
      await fetch('/api/set_api_key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key })
      });
    } catch (e) {
      console.error('Failed to sync API key to server:', e);
    }
  };

  // Symptom Chip select toggle
  const toggleSymptom = (symptom) => {
    if (selectedSymptoms.includes(symptom)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== symptom));
    } else {
      setSelectedSymptoms([...selectedSymptoms, symptom]);
    }
  };

  // Run clinical diagnosis
  const handleDiagnose = async () => {
    if (selectedSymptoms.length === 0) {
      alert('Please select at least one symptom to analyze.');
      return;
    }

    setDiagnosing(true);
    setDiagnoses([]);
    setProgress(0);

    // Simulate animated scanner
    let currentProgress = 0;
    const interval = setInterval(() => {
      currentProgress += 10;
      setProgress(currentProgress);
      if (currentProgress >= 100) {
        clearInterval(interval);
      }
    }, 100);

    try {
      const res = await fetch('/api/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms: selectedSymptoms })
      });
      const data = await res.json();
      clearInterval(interval);
      setProgress(100);

      setTimeout(() => {
        setDiagnosing(false);
        if (data.success) {
          setDiagnoses(data.diagnoses);
        } else {
          alert('Diagnostic analysis error: ' + data.message);
        }
        fetchHistory();
      }, 800);
    } catch (e) {
      clearInterval(interval);
      setDiagnosing(false);
      alert('Error connecting to Prolog Inference Server.');
    }
  };

  // Chatbot message submission
  const handleSendChat = async () => {
    const text = chatInput.trim();
    if (!text) return;

    setMessages(prev => [...prev, { sender: 'user', text }]);
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { sender: 'bot', text: data.reply }]);
    } catch (e) {
      setMessages(prev => [...prev, { sender: 'bot', text: 'Sorry, I am having trouble fetching a response.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Save Settings API Key
  const handleSaveApiKey = () => {
    localStorage.setItem('gemini_api_key', apiKey.trim());
    syncApiKey(apiKey.trim());
    alert('Gemini API key saved and synchronized successfully!');
  };

  // SQLite Logs Erase
  const handleClearHistory = async () => {
    if (confirm('Are you sure you want to completely erase SQLite diagnostic logs?')) {
      await fetch('/api/clear_history', { method: 'POST' });
      fetchHistory();
    }
  };

  // Stats Calculator
  const totalQueries = history.length;
  const avgConfidence = totalQueries > 0
    ? (history.reduce((sum, h) => sum + parseFloat(h.confidence), 0) / totalQueries).toFixed(1)
    : '0.0';

  return (
    <div className="app-container">
      {/* ── Sidebar Navigation ── */}
      <aside className="sidebar">
        <div className="brand-section">
          <h1 className="brand-logo">IntelliExpert</h1>
          <p className="brand-tagline">AI Medical Platform</p>
        </div>
        <nav>
          <ul className="nav-list">
            <li className="nav-item">
              <button 
                onClick={() => setActiveTab('dashboard')} 
                className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
              >
                Dashboard Overview
              </button>
            </li>
            <li className="nav-item">
              <button 
                onClick={() => setActiveTab('diagnose')} 
                className={`nav-button ${activeTab === 'diagnose' ? 'active' : ''}`}
              >
                Clinical Diagnostics
              </button>
            </li>
            <li className="nav-item">
              <button 
                onClick={() => setActiveTab('chatbot')} 
                className={`nav-button ${activeTab === 'chatbot' ? 'active' : ''}`}
              >
                AI Chatbot Assistant
              </button>
            </li>
            <li className="nav-item">
              <button 
                onClick={() => setActiveTab('kb')} 
                className={`nav-button ${activeTab === 'kb' ? 'active' : ''}`}
              >
                Knowledge Base
              </button>
            </li>
            <li className="nav-item">
              <button 
                onClick={() => setActiveTab('history')} 
                className={`nav-button ${activeTab === 'history' ? 'active' : ''}`}
              >
                Query History
              </button>
            </li>
            <li className="nav-item">
              <button 
                onClick={() => setActiveTab('settings')} 
                className={`nav-button ${activeTab === 'settings' ? 'active' : ''}`}
              >
                System Settings
              </button>
            </li>
          </ul>
        </nav>
      </aside>

      {/* ── Main Panel ── */}
      <main className="main-content">
        <header className="top-navbar">
          <h2 className="navbar-title">
            {activeTab === 'dashboard' && 'Dashboard Overview'}
            {activeTab === 'diagnose' && 'Clinical Inference Engine'}
            {activeTab === 'chatbot' && 'IntelliBot Chat System'}
            {activeTab === 'kb' && 'Medical Knowledge Base'}
            {activeTab === 'history' && 'SQLite Logs & Audits'}
            {activeTab === 'settings' && 'System Configuration'}
          </h2>
          <div className="system-status">
            <span className="status-dot"></span>
            AI Online Fallbacks Ready
          </div>
        </header>

        {/* ── Tab Content Panes ── */}
        
        {/* Dashboard Overview */}
        <section className={`content-pane ${activeTab === 'dashboard' ? 'active' : ''}`}>
          <div className="dashboard-banner" style={{ backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.75)), url(${medicalBanner})` }}>
            <h2 className="banner-title">Welcome to IntelliExpert AI</h2>
            <p className="banner-description">
              A hybrid symbolic reasoning clinical platform leveraging Prolog logic statements, local database contexts, and live search engines to recommend safe treatments.
            </p>
          </div>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-label">Symbolic Clinical Facts</span>
              <span className="stat-value primary">35 Facts Active</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Logical Inference Rules</span>
              <span className="stat-value success">18 Rules Active</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Total Clinical Queries</span>
              <span className="stat-value secondary">{totalQueries} Queries</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">AI Confidence Average</span>
              <span className="stat-value warning">{avgConfidence}% Average</span>
            </div>
          </div>
        </section>

        {/* Clinical Diagnostics */}
        <section className={`content-pane ${activeTab === 'diagnose' ? 'active' : ''}`}>
          <div className="card-container">
            <h3 className="section-title">Inference Diagnostics</h3>
            <p className="section-description">Select the clinical symptoms currently experienced by the patient to process the Prolog-structured expert logic rules.</p>
            
            <div className="symptoms-grid">
              {symptoms.map(s => {
                const label = s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                const isSelected = selectedSymptoms.includes(s);
                return (
                  <label key={s} className={`symptom-chip ${isSelected ? 'selected' : ''}`}>
                    <input 
                      type="checkbox" 
                      checked={isSelected} 
                      onChange={() => toggleSymptom(s)} 
                    />
                    <span>{label}</span>
                  </label>
                );
              })}
            </div>

            <button 
              onClick={handleDiagnose} 
              disabled={diagnosing} 
              className="btn-primary"
            >
              {diagnosing ? 'Executing Prolog Rules...' : 'Run Diagnostics'}
            </button>

            {diagnosing && (
              <div className="progress-bar-container">
                <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
              </div>
            )}
          </div>

          {diagnoses.length > 0 && (
            <div className="diagnostic-results">
              <h3 className="section-title">Matching Diagnoses & Treatment Guidelines</h3>
              {diagnoses.map(diag => {
                const recs = diag.details.recommendations;
                const precautions = diag.details.precautions;
                const meds = diag.details.medicines;

                return (
                  <div key={diag.disease} className="results-card">
                    <div className="results-header">
                      <h3>{diag.disease.replace(/_/g, ' ')}</h3>
                      <span className="confidence-badge">{diag.confidence.toFixed(1)}% Match Confidence</span>
                    </div>
                    <pre className="reasoning-box">{diag.explanation}</pre>
                    
                    {recs && recs.length > 0 && (
                      <div>
                        <strong>📋 Suggested Care Guidelines:</strong>
                        <ul className="result-list">
                          {recs.map((r, i) => <li key={i}>{r}</li>)}
                        </ul>
                      </div>
                    )}

                    {precautions && precautions.length > 0 && (
                      <div style={{ marginTop: '5px' }}>
                        <strong>🛡️ Safety Precautions:</strong>
                        <ul className="result-list prec-list">
                          {precautions.map((p, i) => <li key={i}>{p}</li>)}
                        </ul>
                      </div>
                    )}

                    {meds && meds.length > 0 && (
                      <div style={{ marginTop: '5px' }}>
                        <strong>💊 Recommended Safe Medicines:</strong>
                        <div className="result-med-chips">
                          {meds.map((m, i) => <span key={i} className="med-badge">{m}</span>)}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {diagnoses.length === 0 && !diagnosing && selectedSymptoms.length > 0 && (
            <div className="results-card" style={{ textAlign: 'center', color: '#9CA3AF' }}>
              Select symptoms and click Run Diagnostics to view results.
            </div>
          )}
        </section>

        {/* AI Chatbot Assistant */}
        <section className={`content-pane ${activeTab === 'chatbot' ? 'active' : ''}`}>
          <div className="chat-window">
            <header className="chat-header">
              <div className="status-dot"></div>
              <strong>IntelliBot Clinical Chat Agent</strong>
            </header>
            <div className="chat-messages">
              {messages.map((m, i) => (
                <div key={i} className={`chat-message ${m.sender}`}>
                  <div 
                    className="message-bubble"
                    dangerouslySetInnerHTML={{ __html: m.text }}
                  />
                </div>
              ))}
              {chatLoading && (
                <div className="chat-message bot">
                  <div className="message-bubble" style={{ color: '#9CA3AF' }}>
                    IntelliBot is searching & evaluating rules...
                  </div>
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>
            <div className="chat-input-bar">
              <input 
                type="text" 
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                placeholder="Ask about migraine, symptoms of fever, contraindications..." 
                className="chat-input"
              />
              <button onClick={handleSendChat} className="btn-primary">
                Send Query
              </button>
            </div>
          </div>
        </section>

        {/* Knowledge Base */}
        <section className={`content-pane ${activeTab === 'kb' ? 'active' : ''}`}>
          <div className="search-bar-container">
            <input 
              type="text" 
              value={kbSearch}
              onChange={(e) => setKbSearch(e.target.value)}
              placeholder="Search medical knowledge corpus by disease name or keywords..." 
              className="search-input"
            />
          </div>
          <div className="kb-cards-grid">
            {Object.entries(kb)
              .filter(([disease, info]) => {
                const q = kbSearch.toLowerCase().trim();
                return (
                  disease.toLowerCase().includes(q) ||
                  info.full_name.toLowerCase().includes(q) ||
                  info.symptoms.some(s => s.toLowerCase().includes(q))
                );
              })
              .map(([disease, info]) => (
                <div key={disease} className="kb-card">
                  <h3>{info.full_name}</h3>
                  <p>{info.description}</p>
                  <div className="kb-sections">
                    <div><b>Symptoms:</b> {info.symptoms.join(', ')}</div>
                    <div><b>Prescriptions:</b> {info.medicines.join(', ')}</div>
                    <div><b>Care Guidelines:</b> {info.recommendations.join(', ')}</div>
                    <div><b>Precautions:</b> {info.precautions.join(', ')}</div>
                  </div>
                </div>
              ))}
          </div>
        </section>

        {/* History Logs */}
        <section className={`content-pane ${activeTab === 'history' ? 'active' : ''}`}>
          <div className="card-container" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 className="section-title">SQLite Audit Reports</h3>
                <p className="section-description" style={{ marginBottom: 0 }}>Review all logged patient cases in SQLite diagnostics databases.</p>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <a href="/api/export_pdf" target="_blank" className="btn-primary" style={{ textDecoration: 'none' }}>
                  Export PDF Report
                </a>
                <button onClick={handleClearHistory} className="btn-primary btn-clear">
                  Erase SQL Logs
                </button>
              </div>
            </div>

            <div className="table-container">
              <table className="audit-table">
                <thead>
                  <tr>
                    <th>Case ID</th>
                    <th>Timestamp</th>
                    <th>Query Symptoms</th>
                    <th>Matched Diagnosis</th>
                    <th>Confidence (%)</th>
                  </tr>
                </thead>
                <tbody>
                  {history.length === 0 ? (
                    <tr>
                      <td colSpan="5" style={{ textAlign: 'center', color: '#9CA3AF' }}>
                        No diagnostic log queries found in SQLite diagnostic logs.
                      </td>
                    </tr>
                  ) : (
                    history.map(item => (
                      <tr key={item.id}>
                        <td>{item.id}</td>
                        <td>{item.timestamp}</td>
                        <td>{item.symptoms}</td>
                        <td><b>{item.diagnosis.toUpperCase()}</b></td>
                        <td>{parseFloat(item.confidence).toFixed(1)}%</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Settings Configuration */}
        <section className={`content-pane ${activeTab === 'settings' ? 'active' : ''}`}>
          <div className="card-container">
            <h3 className="section-title">AI Engine Settings</h3>
            <p className="section-description">Input and configure clinical credentials to synchronize and authenticate Gemini API queries.</p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', maxWidth: '500px' }}>
              <label style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Google Gemini API Key
              </label>
              <input 
                type="password" 
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter Gemini API key (e.g. AIzaSy...)" 
                className="chat-input"
              />
              <button onClick={handleSaveApiKey} className="btn-primary">
                Save & Synchronize Credentials
              </button>
            </div>
          </div>
        </section>

      </main>
    </div>
  );
}
