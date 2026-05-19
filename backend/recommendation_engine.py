from .prolog_connector import PrologConnector
from .python_rule_engine import PythonRuleEngine

class RecommendationEngine:
    def __init__(self):
        self.connector = PrologConnector()
        self.fallback = PythonRuleEngine()

    def get_details(self, disease, patient_symptoms=None):
        if self.connector.available:
            try:
                recommendations = [str(r['R']) for r in self.connector.query(f"care_guidelines({disease}, R)")]
                precautions = [str(p['P']) for p in self.connector.query(f"default_precaution({disease}, P)")]
                medicines = [str(m['M']) for m in self.connector.query(f"suggest_safe_medicine({disease}, M)")]
            except Exception as e:
                print(f"[WARN] Prolog recommendations failed, falling back to Python: {e}")
                if patient_symptoms:
                    self.fallback.set_symptoms(patient_symptoms)
                recommendations = self.fallback.get_care_guidelines(disease)
                precautions = self.fallback.get_precautions(disease)
                medicines = self.fallback.get_safe_medicines(disease)
        else:
            if patient_symptoms:
                self.fallback.set_symptoms(patient_symptoms)
            recommendations = self.fallback.get_care_guidelines(disease)
            precautions = self.fallback.get_precautions(disease)
            medicines = self.fallback.get_safe_medicines(disease)
            
        return {
            'recommendations': recommendations,
            'precautions': precautions,
            'medicines': medicines
        }


