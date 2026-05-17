% run_demo.pl - Standalone Pure Prolog Diagnostic Engine Demo
% Allows running and testing all clinical facts and rules in native Prolog!

:- consult('knowledge_base.pl').
:- consult('rules.pl').
:- consult('inference.pl').

:- initialization(run_demo).

run_demo :-
    writeln('=================================================='),
    writeln('   INTELLIEXPERT AI - native PROLOG LOGIC ENGINE   '),
    writeln('=================================================='),
    nl,
    writeln('--- ASSERTING PATIENT SYMPTOMS ---'),
    writeln('Asserting: fever, cough, fatigue...'),
    assertz(symptom(fever)),
    assertz(symptom(cough)),
    assertz(symptom(fatigue)),
    nl,
    writeln('--- RUNNING LOGICAL INFERENCE DEDUCTION ---'),
    evaluate_diagnosis(Matches),
    print_matches(Matches),
    nl,
    writeln('--- EVALUATING CLINICAL THREAT LEVEL ---'),
    (threat_level(Level) -> format('Evaluated Patient Risk Threat: ~w~n', [Level]) ; writeln('Risk Level: normal')),
    nl,
    writeln('=================================================='),
    halt.

print_matches([]) :- writeln('End of diagnoses list.').
print_matches([[Disease, MatchedSymptoms, Confidence]|Rest]) :-
    format('Deducted Disease: ~w~n', [Disease]),
    format('  * Confidence Certainty: ~2f%~n', [Confidence]),
    format('  * Matched Symptoms: ~w~n', [MatchedSymptoms]),
    (requires_urgent_care(Disease) -> writeln('  ⚠️ WARNING: Patient requires immediate hospitalization/urgent care!') ; true),
    nl,
    print_matches(Rest).
