% knowledge_base.pl - 35 Clinical Facts representing structured medical relationships

% -- Disease Symptoms Facts (20 Facts) --
has_symptom(flu, fever).
has_symptom(flu, cough).
has_symptom(flu, fatigue).
has_symptom(flu, sore_throat).
has_symptom(migraine, headache).
has_symptom(migraine, nausea).
has_symptom(migraine, sensitivity_to_light).
has_symptom(diabetes, fatigue).
has_symptom(diabetes, increased_thirst).
has_symptom(diabetes, frequent_urination).
has_symptom(asthma, cough).
has_symptom(asthma, chest_pain).
has_symptom(asthma, shortness_of_breath).
has_symptom(hypertension, headache).
has_symptom(hypertension, chest_pain).
has_symptom(covid, fever).
has_symptom(covid, cough).
has_symptom(covid, loss_of_taste).
has_symptom(pneumonia, fever).
has_symptom(pneumonia, chest_pain).

% -- Prescribed Medications Facts (8 Facts) --
has_medicine(flu, paracetamol).
has_medicine(flu, ibuprofen).
has_medicine(migraine, sumatriptan).
has_medicine(diabetes, metformin).
has_medicine(asthma, albuterol).
has_medicine(hypertension, lisinopril).
has_medicine(covid, paxlovid).
has_medicine(pneumonia, amoxicillin).

% -- Contraindications Facts (5 Facts) --
contraindicated(ibuprofen, asthma).
contraindicated(sumatriptan, hypertension).
contraindicated(metformin, kidney_disease).
contraindicated(albuterol, irregular_heartbeat).
contraindicated(lisinopril, pregnancy).

% -- Symptom Severity Facts (4 Facts) --
severity_tier(fever, high).
severity_tier(shortness_of_breath, high).
severity_tier(chest_pain, critical).
severity_tier(runny_nose, low).
