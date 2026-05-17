% rules.pl
% Rules for mapping and recommendation
recommendation(flu, ['Rest', 'Drink plenty of fluids', 'Take antipyretics for fever']).
recommendation(migraine, ['Rest in a dark, quiet room', 'Take pain relievers', 'Stay hydrated']).
recommendation(diabetes, ['Monitor blood sugar levels', 'Follow a balanced diet', 'Exercise regularly']).
recommendation(asthma, ['Use an inhaler', 'Avoid triggers', 'Seek immediate help if breathing becomes very difficult']).
recommendation(hypertension, ['Reduce sodium intake', 'Exercise regularly', 'Manage stress']).
recommendation(covid, ['Isolate yourself', 'Monitor oxygen levels', 'Rest and hydrate', 'Seek medical attention if symptoms worsen']).
recommendation(allergies, ['Avoid allergens', 'Take antihistamines', 'Use eye drops for itching']).
recommendation(pneumonia, ['Get plenty of rest', 'Drink fluids', 'Take prescribed antibiotics if bacterial']).

precaution(flu, ['Wash hands frequently', 'Avoid close contact with sick people', 'Cover mouth when coughing']).
precaution(migraine, ['Identify and avoid triggers', 'Maintain a regular sleep schedule', 'Manage stress']).
precaution(diabetes, ['Maintain a healthy weight', 'Eat a healthy diet', 'Get regular physical activity']).
precaution(asthma, ['Identify and avoid asthma triggers', 'Get vaccinated for influenza and pneumonia']).
precaution(hypertension, ['Eat a heart-healthy diet', 'Maintain a healthy weight', 'Limit alcohol consumption']).
precaution(covid, ['Wear a mask in crowded places', 'Wash hands frequently', 'Get vaccinated']).
precaution(allergies, ['Keep windows closed during high pollen seasons', 'Use air purifiers']).
precaution(pneumonia, ['Get vaccinated', 'Practice good hygiene', 'Don''t smoke']).

medicines(flu, ['Paracetamol', 'Ibuprofen', 'Oseltamivir (if prescribed)']).
medicines(migraine, ['Sumatriptan', 'Ibuprofen', 'Naproxen']).
medicines(diabetes, ['Metformin', 'Insulin (if prescribed)']).
medicines(asthma, ['Albuterol', 'Fluticasone']).
medicines(hypertension, ['Lisinopril', 'Amlodipine']).
medicines(covid, ['Paracetamol', 'Paxlovid (if prescribed)']).
medicines(allergies, ['Cetirizine', 'Loratadine', 'Fexofenadine']).
medicines(pneumonia, ['Amoxicillin (if bacterial)', 'Azithromycin (if bacterial)']).
