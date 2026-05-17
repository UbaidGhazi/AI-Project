class ExplanationEngine:
    def generate_explanation(self, diagnosis):
        disease = diagnosis['disease']
        matched = diagnosis['matched_symptoms']
        
        explanation = f"Diagnosis: {disease.capitalize()}\n\nReason:\n"
        for s in matched:
            explanation += f"- {s.replace('_', ' ').capitalize()} detected\n"
            
        explanation += f"\nTriggered Rule:\n"
        explanation += f"{disease}(X) :-\n"
        explanation += ",\n".join([f"    {s}(X)" for s in matched]) + ".\n"
        
        return explanation
