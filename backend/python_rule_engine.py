"""
python_rule_engine.py
A complete, pure-Python symbolic inference engine that matches the SWI-Prolog 
rules and knowledge base facts EXACTLY. Used as a robust, always-available fallback.
"""

DISEASE_SYMPTOMS = {
    "flu": ["fever", "cough", "fatigue", "sore_throat"],
    "migraine": ["headache", "nausea", "sensitivity_to_light"],
    "diabetes": ["fatigue", "increased_thirst", "frequent_urination"],
    "asthma": ["cough", "chest_pain", "shortness_of_breath"],
    "hypertension": ["headache", "chest_pain"],
    "covid": ["fever", "cough", "loss_of_taste"],
    "pneumonia": ["fever", "chest_pain"]
}

MEDICINES = {
    "flu": ["paracetamol", "ibuprofen"],
    "migraine": ["sumatriptan"],
    "diabetes": ["metformin"],
    "asthma": ["albuterol"],
    "hypertension": ["lisinopril"],
    "covid": ["paxlovid"],
    "pneumonia": ["amoxicillin"]
}

CONTRAINDICATIONS = {
    "ibuprofen": ["asthma"],
    "sumatriptan": ["hypertension"],
    "metformin": ["kidney_disease"],
    "albuterol": ["irregular_heartbeat"],
    "lisinopril": ["pregnancy"]
}

SEVERITY_TIERS = {
    "fever": "high",
    "shortness_of_breath": "high",
    "chest_pain": "critical",
    "runny_nose": "low"
}


class PythonRuleEngine:
    def __init__(self):
        self.patient_symptoms = []

    def set_symptoms(self, symptoms):
        self.patient_symptoms = [s.strip().lower().replace(" ", "_") for s in symptoms]

    def is_symptom_present(self, symptom):
        return symptom in self.patient_symptoms

    def is_critical(self, disease):
        # Rule 13: is_critical(Disease) :- has_symptom(Disease, chest_pain).
        return "chest_pain" in DISEASE_SYMPTOMS.get(disease, [])

    def requires_urgent_care(self, disease):
        # Rule 10: requires_urgent_care(Disease) :- has_symptom(Disease, chest_pain); has_symptom(Disease, shortness_of_breath).
        sympts = DISEASE_SYMPTOMS.get(disease, [])
        return "chest_pain" in sympts or "shortness_of_breath" in sympts

    def urgency_alert(self, disease):
        # Rule 11
        return "high" if self.requires_urgent_care(disease) else "low"

    def default_precaution(self, disease):
        # Rule 12
        if self.is_critical(disease):
            return "Avoid self-medication"
        elif disease == "covid":
            return "Rest and isolate"
        else:
            return "Drink plenty of water"

    def get_precautions(self, disease):
        return [self.default_precaution(disease)]

    def get_care_guidelines(self, disease):
        # Rule 15
        guidelines = []
        if disease == "flu":
            guidelines.append("Increase hydration")
        elif disease == "migraine":
            guidelines.append("Rest in dark room")
        elif disease == "diabetes":
            guidelines.append("Monitor sugar levels")
            
        if self.requires_urgent_care(disease):
            guidelines.append("Seek active help")
            
        return guidelines

    def get_safe_medicines(self, disease):
        # Rule 8: suggest_safe_medicine(Disease, Med)
        safe = []
        for med in MEDICINES.get(disease, []):
            contra_conds = CONTRAINDICATIONS.get(med.lower(), [])
            is_contraindicated = False
            for cond in contra_conds:
                if self.is_symptom_present(cond):
                    is_contraindicated = True
                    break
            if not is_contraindicated:
                safe.append(med)
        return safe

    def get_medication_warnings(self):
        # Rule 7: medication_warning(Med, Symptom)
        warnings = []
        for med, conds in CONTRAINDICATIONS.items():
            for cond in conds:
                if self.is_symptom_present(cond):
                    warnings.append({"Med": med, "Symptom": cond})
        return warnings

    def get_threat_level(self):
        # Rules 4, 5, 6
        has_critical = False
        has_high = False
        
        for sym in self.patient_symptoms:
            tier = SEVERITY_TIERS.get(sym)
            if tier == "critical":
                has_critical = True
            elif tier == "high":
                has_high = True
                
        if has_critical:
            return "critical"
        elif has_high:
            return "high"
        else:
            return "normal"

    def diagnose(self, symptoms):
        self.set_symptoms(symptoms)
        diagnoses = []
        
        for disease, disease_sympts in DISEASE_SYMPTOMS.items():
            matched = [s for s in disease_sympts if self.is_symptom_present(s)]
            if matched:
                confidence = (len(matched) / len(disease_sympts)) * 100
                diagnoses.append({
                    "disease": disease,
                    "matched_symptoms": matched,
                    "confidence": confidence
                })
                
        # Sort descending by confidence
        diagnoses.sort(key=lambda x: x["confidence"], reverse=True)
        return diagnoses
