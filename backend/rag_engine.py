"""
rag_engine.py
Retrieval-Augmented Generation engine using the local medical knowledge base and Google Gemini integration.
Allows API key entry and automatically falls back to offline local RAG matching if no key is supplied.
"""

import re
import json
import urllib.request
import os
from collections import Counter

# ── Comprehensive Medical Knowledge Corpus ──────────────────────────────────
MEDICAL_CORPUS = {
    "flu": {
        "full_name": "Influenza (Flu)",
        "description": "A contagious respiratory illness caused by influenza viruses that infect the nose, throat, and sometimes the lungs.",
        "symptoms": ["fever", "cough", "headache", "fatigue", "sore throat"],
        "recommendations": ["Rest at home", "Drink plenty of fluids", "Take antipyretics for fever", "Gargle with salt water"],
        "precautions": ["Wash hands frequently", "Avoid close contact with sick people", "Cover mouth when coughing", "Get annual flu vaccine"],
        "medicines": ["Paracetamol", "Ibuprofen", "Oseltamivir (Tamiflu – if prescribed)", "Decongestants"],
        "severity": "Moderate",
        "contagious": True,
    },
    "migraine": {
        "full_name": "Migraine",
        "description": "A neurological condition causing intense, debilitating headaches often accompanied by nausea and light sensitivity.",
        "symptoms": ["headache", "nausea", "sensitivity to light", "visual aura", "vomiting"],
        "recommendations": ["Rest in a dark quiet room", "Apply cold compress to forehead", "Take pain relievers early", "Stay hydrated"],
        "precautions": ["Identify and avoid personal triggers", "Maintain regular sleep schedule", "Manage stress", "Limit screen time"],
        "medicines": ["Sumatriptan", "Ibuprofen", "Naproxen", "Amitriptyline (preventive)"],
        "severity": "Moderate to Severe",
        "contagious": False,
    },
    "diabetes": {
        "full_name": "Diabetes Mellitus",
        "description": "A metabolic disease causing persistently high blood sugar levels due to insufficient insulin production or action.",
        "symptoms": ["fatigue", "increased thirst", "frequent urination", "blurred vision", "slow wound healing"],
        "recommendations": ["Monitor blood sugar levels daily", "Follow a balanced low-carb diet", "Exercise for 30 min daily", "Regular medical checkups"],
        "precautions": ["Maintain healthy weight", "Avoid sugary drinks", "Get regular physical activity", "Inspect feet daily"],
        "medicines": ["Metformin", "Glipizide", "Insulin (if prescribed)", "Empagliflozin"],
        "severity": "Chronic — requires lifelong management",
        "contagious": False,
    },
    "asthma": {
        "full_name": "Asthma",
        "description": "A condition in which airways narrow, swell, and may produce extra mucus, making breathing difficult.",
        "symptoms": ["cough", "chest pain", "shortness of breath", "wheezing", "chest tightness"],
        "recommendations": ["Use prescribed inhaler regularly", "Avoid asthma triggers", "Follow an asthma action plan", "Monitor peak flow"],
        "precautions": ["Avoid smoke and strong odors", "Keep indoor air clean", "Get flu and pneumonia vaccines", "Stay indoors on high-pollution days"],
        "medicines": ["Albuterol (rescue inhaler)", "Fluticasone (inhaled steroid)", "Montelukast", "Formoterol"],
        "severity": "Moderate to Severe",
        "contagious": False,
    },
    "hypertension": {
        "full_name": "Hypertension (High Blood Pressure)",
        "description": "A condition where the force of blood against artery walls is persistently too high, straining the heart.",
        "symptoms": ["headache", "fatigue", "chest pain", "irregular heartbeat", "dizziness"],
        "recommendations": ["Reduce sodium intake to <2g/day", "Exercise 30 min most days", "Manage stress with meditation", "Limit alcohol"],
        "precautions": ["Eat a heart-healthy DASH diet", "Maintain healthy weight", "Stop smoking", "Limit caffeine"],
        "medicines": ["Lisinopril", "Amlodipine", "Losartan", "Hydrochlorothiazide"],
        "severity": "Chronic — silent killer if unmanaged",
        "contagious": False,
    },
    "covid": {
        "full_name": "COVID-19",
        "description": "An infectious respiratory disease caused by the SARS-CoV-2 coronavirus, ranging from mild to severe.",
        "symptoms": ["fever", "cough", "fatigue", "loss of taste", "loss of smell", "shortness of breath", "body aches"],
        "recommendations": ["Isolate immediately", "Monitor oxygen levels (SpO2 >95%)", "Rest and hydrate", "Seek ER if breathing is very difficult"],
        "precautions": ["Wear N95 mask in crowds", "Wash hands for 20 seconds", "Get vaccinated and boosted", "Ventilate indoor spaces"],
        "medicines": ["Paracetamol", "Paxlovid (if prescribed within 5 days)", "Dexamethasone (severe cases)", "Vitamin C & Zinc (supportive)"],
        "severity": "Mild to Critical",
        "contagious": True,
    },
    "allergies": {
        "full_name": "Allergic Reaction",
        "description": "An immune system overreaction to a foreign substance (allergen) such as pollen, dust, pet dander, or certain foods.",
        "symptoms": ["sneezing", "runny nose", "itchy eyes", "cough", "skin rash", "hives"],
        "recommendations": ["Avoid known allergens", "Take antihistamines before exposure", "Use nasal corticosteroid sprays", "Carry EpiPen if prescribed"],
        "precautions": ["Keep windows closed during high pollen season", "Use air purifiers with HEPA filters", "Shower after outdoor activity", "Use dust-mite-proof bedding"],
        "medicines": ["Cetirizine (Zyrtec)", "Loratadine (Claritin)", "Fexofenadine (Allegra)", "Fluticasone nasal spray"],
        "severity": "Mild to Moderate (anaphylaxis = severe emergency)",
        "contagious": False,
    },
    "pneumonia": {
        "full_name": "Pneumonia",
        "description": "An infection that inflames the air sacs (alveoli) in one or both lungs, filling them with fluid or pus.",
        "symptoms": ["fever", "cough", "chest pain", "fatigue", "difficulty breathing", "chills", "bluish lips"],
        "recommendations": ["Complete full course of antibiotics", "Get plenty of rest", "Drink at least 8 glasses of water daily", "Use fever reducer"],
        "precautions": ["Get pneumococcal and flu vaccines", "Practice good hand hygiene", "Do not smoke", "Avoid close contact with infected people"],
        "medicines": ["Amoxicillin (bacterial)", "Azithromycin (bacterial)", "Ceftriaxone (severe)", "Oseltamivir (if viral)"],
        "severity": "Moderate to Severe (life-threatening in elderly/immunocompromised)",
        "contagious": True,
    },
}

class RAGEngine:
    def __init__(self):
        self.corpus = MEDICAL_CORPUS
        self.query_processor = None
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self._build_index()

    def set_query_processor(self, qp):
        self.query_processor = qp

    def set_api_key(self, key):
        self.api_key = key.strip()

    def _build_index(self):
        self.index = {}
        for disease, info in self.corpus.items():
            keywords = (
                [disease]
                + info["symptoms"]
                + info["medicines"]
                + info["full_name"].lower().split()
            )
            for kw in keywords:
                kw = kw.lower().strip("()")
                self.index.setdefault(kw, [])
                if disease not in self.index[kw]:
                    self.index[kw].append(disease)

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return [w for w in text.split() if len(w) > 2]

    def _retrieve(self, query: str) -> list[str]:
        tokens = self._tokenize(query)
        scores = Counter()
        for token in tokens:
            if token in self.index:
                for d in self.index[token]:
                    scores[d] += 3
            for kw, diseases in self.index.items():
                if token in kw or kw in token:
                    for d in diseases:
                        scores[d] += 1
        return [d for d, _ in scores.most_common(3)]

    def _detect_intent(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["hello", "hi ", "hey", "greet"]):
            return "greeting"
        if any(w in q for w in ["help", "what can you", "what do you"]):
            return "help"
        if any(w in q for w in ["history", "past diagnos", "previous diagnos", "my diagnos"]):
            return "history"
        if any(w in q for w in ["list all", "all disease", "all condition", "diseases in"]):
            return "list_diseases"
        if any(w in q for w in ["symptom", "sign", "feel", "experien", "show", "indicate"]):
            return "symptoms"
        if any(w in q for w in ["medicine", "drug", "medication", "take", "prescri", "pill"]):
            return "medicines"
        if any(w in q for w in ["treat", "cure", "recommend", "suggest", "manage"]):
            return "recommendations"
        if any(w in q for w in ["prevent", "avoid", "precaution", "protect", "safe"]):
            return "precautions"
        if any(w in q for w in ["what is", "describe", "explain", "about", "defin", "tell me"]):
            return "description"
        if any(w in q for w in ["contagious", "spread", "infect", "transmit", "catch"]):
            return "contagious"
        if any(w in q for w in ["sever", "serious", "danger", "risk", "bad"]):
            return "severity"
        return "general"

    # ── Response Generation ───────────────────────────────────────────────────

    def chat(self, user_message: str) -> str:
        intent = self._detect_intent(user_message)

        if intent == "greeting":
            return (
                "👋 Hello! I'm **IntelliBot**, your hybrid AI Medical Assistant.\n\n"
                "I can answer questions about:\n"
                "• Symptoms of any disease in the knowledge base\n"
                "• Medicines and treatments\n"
                "• Precautions and preventive measures\n"
                "• Your past diagnosis history\n\n"
                "How can I help you today?"
            )

        if intent == "help":
            return (
                "🤖 **Here are some things you can ask me:**\n\n"
                "• *What are the symptoms of flu?*\n"
                "• *What medicines are used for migraine?*\n"
                "• *How do I prevent COVID-19?*\n"
                "• *Tell me about diabetes*\n"
                "• *Show my diagnosis history*\n"
                "• *List all diseases*\n"
                "• *Is pneumonia contagious?*\n"
                "• *How severe is asthma?*"
            )

        if intent == "history":
            return self._history_response()

        if intent == "list_diseases":
            names = [f"• {info['full_name']}" for info in self.corpus.values()]
            return (
                f"🏥 **Diseases in Knowledge Base ({len(names)} total):**\n\n"
                + "\n".join(names)
                + "\n\nAsk me about any of these!"
            )

    def _search_web(self, query: str) -> list[str]:
        try:
            import urllib.parse
            # Standardize query
            q = query.strip()
            # Clean up query
            q_clean = re.sub(r"[^\w\s]", " ", q).strip()
            search_query = q_clean + " medical clinical symptoms treatment"
            url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(search_query)
            
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
                }
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8', errors='ignore')
                snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
                results = []
                for s in snippets[:3]:
                    clean = re.sub(r'<[^>]*>', '', s)
                    clean = clean.replace('&amp;', '&').replace('&quot;', '"').replace('&#x27;', "'").replace('&apos;', "'").strip()
                    if clean:
                        results.append(clean)
                return results
        except Exception as e:
            print(f"[WARN] DDG Web search failed: {e}")
            return []

    def chat(self, user_message: str) -> str:
        intent = self._detect_intent(user_message)

        if intent == "greeting":
            return (
                "👋 Hello! I'm **IntelliBot**, your hybrid AI Medical Assistant.\n\n"
                "I can answer questions about:\n"
                "• Symptoms of any disease in the knowledge base\n"
                "• Medicines and treatments\n"
                "• Precautions and preventive measures\n"
                "• Your past diagnosis history\n\n"
                "How can I help you today?"
            )

        if intent == "help":
            return (
                "🤖 **Here are some things you can ask me:**\n\n"
                "• *What are the symptoms of flu?*\n"
                "• *What medicines are used for migraine?*\n"
                "• *How do I prevent COVID-19?*\n"
                "• *Tell me about diabetes*\n"
                "• *Show my diagnosis history*\n"
                "• *List all diseases*\n"
                "• *Is pneumonia contagious?*\n"
                "• *How severe is asthma?*"
            )

        if intent == "history":
            return self._history_response()

        if intent == "list_diseases":
            names = [f"• {info['full_name']}" for info in self.corpus.values()]
            return (
                f"🏥 **Diseases in Knowledge Base ({len(names)} total):**\n\n"
                + "\n".join(names)
                + "\n\nAsk me about any of these!"
            )

        # Retrieve local relevant diseases semantically
        relevant_diseases = self._retrieve(user_message)
        
        # 1. Fetch live search insights
        search_results = self._search_web(user_message)
        search_str = "\n".join([f"• {r}" for r in search_results]) if search_results else ""

        # 2. Extract symptoms and apply Symbolic rules using PythonRuleEngine fallback
        from utils.constants import ALL_SYMPTOMS
        from backend.python_rule_engine import PythonRuleEngine
        
        rule_engine = PythonRuleEngine()
        q_clean = user_message.lower().replace(" ", "_")
        mentioned_symptoms = []
        for sym in ALL_SYMPTOMS:
            space_sym = sym.replace("_", " ")
            if sym in q_clean or space_sym in user_message.lower():
                mentioned_symptoms.append(sym)
                
        diagnoses = []
        threat_level = "normal"
        warnings = []
        safe_medicines = []
        precautions = []
        care_guidelines = []
        
        if mentioned_symptoms:
            diagnoses = rule_engine.diagnose(mentioned_symptoms)
            threat_level = rule_engine.get_threat_level()
            warnings = rule_engine.get_medication_warnings()
            if diagnoses:
                top_disease = diagnoses[0]['disease']
                safe_medicines = rule_engine.get_safe_medicines(top_disease)
                precautions = rule_engine.get_precautions(top_disease)
                care_guidelines = rule_engine.get_care_guidelines(top_disease)
        else:
            # Check if a disease name is directly mentioned in query or relevant local retrieval
            target_disease = None
            for disease in self.corpus.keys():
                if disease in user_message.lower():
                    target_disease = disease
                    break
            if not target_disease and relevant_diseases:
                target_disease = relevant_diseases[0]
                
            if target_disease:
                safe_medicines = rule_engine.get_safe_medicines(target_disease)
                precautions = rule_engine.get_precautions(target_disease)
                care_guidelines = rule_engine.get_care_guidelines(target_disease)

        # Format detailed medical context
        clinical_context = {
            "web_search_insights": search_results,
            "local_corpus_matches": [self.corpus[d] for d in relevant_diseases if d in self.corpus],
            "suspected_diagnoses": diagnoses[:2] if diagnoses else "None",
            "patient_symptoms": [s.replace("_", " ").title() for s in mentioned_symptoms],
            "threat_level": threat_level.upper(),
            "suggested_medicines": [m.title() for m in safe_medicines],
            "care_guidelines": care_guidelines,
            "precautions": precautions,
            "contraindications": [{"medicine": w["Med"].title(), "unsafe_due_to": w["Symptom"].replace("_", " ").title()} for w in warnings]
        }

        # 3. Google Gemini Integration (if API key provided)
        if self.api_key:
            gemini_response = self._query_gemini(user_message, json.dumps(clinical_context, indent=2))
            if gemini_response:
                return gemini_response

        # 4. Fallback offline response formatting (if no Gemini API key)
        resp = ""
        
        # Add live search if available
        if search_str:
            resp += "🔍 **Google Search Insights (Live DDG):**\n"
            resp += f"{search_str}\n\n"
            
        # Add rich local corpus details
        if relevant_diseases:
            resp += "📖 **Clinical Corpus Details:**\n"
            for d in relevant_diseases[:2]:
                if d in self.corpus:
                    info = self.corpus[d]
                    resp += f"• **{info['full_name']}** ({info['severity']} Severity):\n"
                    resp += f"  *Description:* {info['description']}\n"
                    resp += f"  *Contagious:* {'Yes' if info['contagious'] else 'No'}\n"
                    resp += f"  *Common Symptoms:* {', '.join(info['symptoms'])}\n"
            resp += "\n"
            
        if mentioned_symptoms:
            resp += "⚙️ **Symbolic AI Diagnostics & Inference Rules:**\n"
            resp += f"• **Patient Severity Risk:** {threat_level.upper()}\n"
            if diagnoses:
                matches_str = ", ".join([f"{d['disease'].title()} ({d['confidence']:.1f}%)" for d in diagnoses[:2]])
                resp += f"• **Deducted Target(s):** {matches_str}\n"
            resp += "\n"

        if safe_medicines:
            resp += "💊 **Recommended Safe Medications:**\n"
            resp += "\n".join([f"• {m.title()}" for m in safe_medicines]) + "\n\n"

        if precautions or care_guidelines:
            resp += "🛡️ **Care Guidelines & Precautions:**\n"
            for g in care_guidelines:
                resp += f"• Care: {g}\n"
            for p in precautions:
                resp += f"• Precaution: {p}\n"
            resp += "\n"

        if warnings:
            resp += "🚨 **Contraindications & Safety Warnings:**\n"
            for w in warnings:
                resp += f"• ❌ {w['Med'].upper()} is contraindicated for patients experiencing '{w['Symptom'].replace('_', ' ').capitalize()}'\n"
            resp += "\n"

        if not resp:
            return self._fallback()

        resp += "⚠️ *Disclaimer: This clinical AI provides diagnostic insights based on symbolic medical rules. Always consult a licensed physician for real clinical issues.*"
        return resp


    def _query_gemini(self, message: str, context: str) -> str:
        prompt = (
            "You are a friendly, highly professional clinical AI medical expert system assistant.\n"
            "Help the patient answer their question using the provided clinical context which contains real-time web search insights, symbolic diagnostics, recommended safe medicines, precautions, and contraindications.\n\n"
            "CRITICAL RULES:\n"
            "1. You MUST include web search insights and clearly recommend safe medicines based on the context.\n"
            "2. Highlight any contraindications and patient severity risk.\n"
            "3. Format your output professionally in clear, distinct sections (e.g. Google Search Insights, Recommended Safe Medications, Care Guidelines & Precautions, Contraindications & Safety Warnings, and Symbolic AI Diagnostics).\n"
            "4. Keep formatting clean, use standard markdown list points (•) and bold tags (**text**). Avoid complex HTML or excessive emoji symbols. Ensure there are no unrendered asterisks.\n"
            "5. Always conclude with a professional clinical disclaimer advising them to consult a doctor.\n\n"
            f"CLINICAL CONTEXT:\n{context}\n\n"
            f"Patient Question: {message}"
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        body = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"[WARN] Gemini API request failed: {e}")
            return None


    def _history_response(self) -> str:
        if not self.query_processor:
            return "⚠️ Database not connected. Please run a diagnosis first."
        try:
            rows = self.query_processor.get_history()
            if not rows:
                return "📭 No diagnosis history yet. Go to the **Diagnosis** tab to run your first analysis."
            lines = []
            for r in rows[:8]:
                conf = float(r[4]) if r[4] else 0.0
                lines.append(f"• **{r[1]}** → *{r[3].title()}* ({conf:.1f}% confidence)\n  Symptoms: {r[2]}")
            return "📊 **Recent Diagnosis History:**\n\n" + "\n\n".join(lines)
        except Exception as e:
            return f"⚠️ Could not retrieve history: {e}"

    def _format_response(self, disease: str, info: dict, intent: str, query: str) -> str:
        name = info["full_name"]

        if intent == "symptoms":
            items = "\n".join(f"  • {s.title()}" for s in info["symptoms"])
            return f"🩺 **Symptoms of {name}:**\n\n{items}"

        if intent == "medicines":
            items = "\n".join(f"  • {m}" for m in info["medicines"])
            return (
                f"💊 **Medicines for {name}:**\n\n{items}\n\n"
                "⚠️ *Always consult a licensed physician before taking any medication.*"
            )

        if intent == "recommendations":
            items = "\n".join(f"  • {r}" for r in info["recommendations"])
            return f"✅ **Recommendations for {name}:**\n\n{items}"

        if intent == "precautions":
            items = "\n".join(f"  • {p}" for p in info["precautions"])
            return f"🛡️ **Precautions for {name}:**\n\n{items}"

        if intent == "description":
            return (
                f"📖 **{name}**\n\n"
                f"{info['description']}\n\n"
                f"**Severity:** {info['severity']}\n"
                f"**Contagious:** {'✅ Yes' if info['contagious'] else '❌ No'}"
            )

        if intent == "contagious":
            tag = "✅ **Yes, it IS contagious.**" if info["contagious"] else "❌ **No, it is NOT contagious.**"
            return f"🦠 **{name} — Contagious?**\n\n{tag}"

        if intent == "severity":
            return f"⚠️ **{name} — Severity Level:**\n\n{info['severity']}"

        # General fallback
        syms = ", ".join(info["symptoms"][:4])
        meds = ", ".join(info["medicines"][:3])
        return (
            f"🏥 **{name}**\n\n"
            f"{info['description']}\n\n"
            f"**Common Symptoms:** {syms}\n"
            f"**Medicines:** {meds}\n"
            f"**Severity:** {info['severity']}\n"
            f"**Contagious:** {'Yes' if info['contagious'] else 'No'}"
        )

    def _fallback(self) -> str:
        return (
            "🤔 I couldn't find specific information for that query.\n\n"
            "Try asking about a specific disease, e.g.:\n"
            "• *'What are the symptoms of asthma?'*\n"
            "• *'Tell me about hypertension'*\n"
            "• *'List all diseases'*"
        )
