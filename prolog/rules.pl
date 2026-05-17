% rules.pl - Exactly 18 Logical Inference Rules for Clinical Diagnostics and Explanation Tracing

% Rule 1: Determine if a symptom has been asserted by the patient
is_symptom_present(S) :- symptom(S).

% Rule 2: Fetch all symptoms configured for a specific disease
disease_symptoms(Disease, List) :- findall(S, has_symptom(Disease, S), List).

% Rule 3: Find matches and compute confidence logic
match_disease_logic(Disease, Matched, Confidence) :-
    disease_symptoms(Disease, All),
    findall(S, (member(S, All), symptom(S)), Matched),
    length(All, Total),
    length(Matched, MatchedCount),
    MatchedCount > 0,
    Confidence is (MatchedCount / Total) * 100.

% Rule 4: Identify if patient has critical severity symptoms
has_critical_symptoms :- symptom(S), severity_tier(S, critical).

% Rule 5: Identify if patient has high severity symptoms
has_high_symptoms :- symptom(S), severity_tier(S, high).

% Rule 6: Determine general threat level of the patient based on symptoms
threat_level(critical) :- has_critical_symptoms.
threat_level(high) :- has_high_symptoms, \+ has_critical_symptoms.
threat_level(normal) :- \+ has_high_symptoms, \+ has_critical_symptoms.

% Rule 7: Detect potential medication contraindications based on patient symptoms
medication_warning(Med, Symptom) :- contraindicated(Med, Symptom), symptom(Symptom).

% Rule 8: Suggest safe medicines excluding contraindicated ones
suggest_safe_medicine(Disease, Med) :-
    has_medicine(Disease, Med),
    \+ (contraindicated(Med, Cond), symptom(Cond)).

% Rule 9: Check if a medicine is unsafe for high-risk conditions
is_unsafe_med(Med) :- contraindicated(Med, Cond), symptom(Cond).

% Rule 10: Identify if disease requires immediate hospitalization
requires_urgent_care(Disease) :- has_symptom(Disease, chest_pain).
requires_urgent_care(Disease) :- has_symptom(Disease, shortness_of_breath).

% Rule 11: Alert high care urgency
urgency_alert(Disease, high) :- requires_urgent_care(Disease).
urgency_alert(Disease, low) :- \+ requires_urgent_care(Disease).

% Rule 12: Generate primary precautions
default_precaution(Disease, 'Avoid self-medication') :- is_critical(Disease).
default_precaution(Disease, 'Rest and isolate') :- Disease = covid.
default_precaution(Disease, 'Drink plenty of water') :- \+ is_critical(Disease).

% Rule 13: Check if a disease is marked critical
is_critical(Disease) :- has_symptom(Disease, chest_pain).

% Rule 14: Logic to trace active triggers (XAI Explanation helper)
explanation_trace(Disease, Explanation) :-
    match_disease_logic(Disease, Matched, Confidence),
    Confidence >= 50,
    Explanation = 'Traced via Prolog logic rules'.

% Rule 15: General rules for clinical recommendations
care_guidelines(Disease, 'Increase hydration') :- Disease = flu.
care_guidelines(Disease, 'Rest in dark room') :- Disease = migraine.
care_guidelines(Disease, 'Monitor sugar levels') :- Disease = diabetes.
care_guidelines(Disease, 'Seek active help') :- requires_urgent_care(Disease).

% Rule 16: Check if a symptom is minor
is_minor_symptom(S) :- severity_tier(S, low).

% Rule 17: Trace matches sorted (Helper rule for PySWIP integration)
find_matches(Matches) :-
    findall([D, M, C], match_disease_logic(D, M, C), Unsorted),
    predsort(compare_confidence, Unsorted, Matches).

% Rule 18: Compare confidence levels for sorting descending
compare_confidence(Order, [_, _, Conf1], [_, _, Conf2]) :-
    (Conf1 < Conf2 -> Order = >
    ; Conf1 > Conf2 -> Order = <
    ; Order = =).
