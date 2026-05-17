from .prolog_connector import PrologConnector

class ExplanationEngine:
    def __init__(self):
        self.connector = PrologConnector()

    def generate_explanation(self, diagnosis):
        disease = diagnosis['disease']
        matched = diagnosis['matched_symptoms']
        
        explanation = f"🔍 Logical Diagnostic Trace (Prolog Expert System)\n"
        explanation += f"==============================================\n"
        explanation += f"Deducted Target: {disease.upper()}\n\n"
        
        explanation += f"Patient Symptoms Triggered:\n"
        for s in matched:
            explanation += f"  ✔ {s.replace('_', ' ').capitalize()} -> Confirmed Present\n"
            
        explanation += f"\nInference Rule Trace:\n"
        explanation += f"  disease({disease}, Symptoms) :-\n"
        explanation += " ,\n".join([f"    asserted({s})" for s in matched]) + ".\n\n"
        
        # Query Threat Level from rule 6
        threat = self.connector.query("threat_level(Level)")
        level = str(threat[0]['Level']) if threat else "normal"
        explanation += f"Calculated Patient Severity Risk: {level.upper()}\n"
        
        # Check contraindications from rule 7
        warnings = self.connector.query("medication_warning(Med, Symptom)")
        if warnings:
            explanation += f"\n⚠️ Drug Contraindication Warnings Logged:\n"
            for w in warnings:
                explanation += f"  ❌ Contraindicated: {str(w['Med']).upper()} is unsafe due to symptom '{str(w['Symptom']).upper()}'\n"
                
        return explanation
