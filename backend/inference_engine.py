from .prolog_connector import PrologConnector

class InferenceEngine:
    def __init__(self):
        self.connector = PrologConnector()

    def diagnose(self, symptoms):
        self.connector.retract_all_symptoms()
        for s in symptoms:
            self.connector.assert_symptom(s)
            
        results = self.connector.query("diagnose(Matches)")
        
        diagnoses = []
        if results and results[0].get('Matches'):
            for match in results[0]['Matches']:
                disease = match[0]
                matched_symptoms = [str(s) for s in match[1]]
                confidence = float(match[2])
                diagnoses.append({
                    'disease': str(disease),
                    'matched_symptoms': matched_symptoms,
                    'confidence': confidence
                })
        return diagnoses
