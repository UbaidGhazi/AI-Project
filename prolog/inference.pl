% inference.pl - Inference Engine Entrypoint
% Connects dynamic patient symptoms to rule-based diagnosis queries.

:- dynamic symptom/1.

% Run full rule evaluation and diagnostic deduction
evaluate_diagnosis(Matches) :-
    find_matches(Matches).
