from .prolog_connector import PrologConnector

class RecommendationEngine:
    def __init__(self):
        self.connector = PrologConnector()

    def get_details(self, disease):
        recommendations = [str(r) for res in self.connector.query(f"recommendation({disease}, R)") for r in res.get('R', [])]
        precautions = [str(p) for res in self.connector.query(f"precaution({disease}, P)") for p in res.get('P', [])]
        medicines = [str(m) for res in self.connector.query(f"medicines({disease}, M)") for m in res.get('M', [])]
        
        return {
            'recommendations': recommendations,
            'precautions': precautions,
            'medicines': medicines
        }
