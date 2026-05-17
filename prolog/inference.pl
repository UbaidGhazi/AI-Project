% inference.pl
:- dynamic symptom/1.

% Rule to find matching diseases based on asserted symptoms
match_disease(Disease, MatchedSymptoms, Confidence) :-
    disease(Disease, DiseaseSymptoms),
    findall(S, (member(S, DiseaseSymptoms), symptom(S)), MatchedSymptoms),
    length(DiseaseSymptoms, Total),
    length(MatchedSymptoms, MatchedCount),
    MatchedCount > 0,
    Confidence is (MatchedCount / Total) * 100.

% Find all matches sorted by confidence
diagnose(Matches) :-
    findall([Disease, MatchedSymptoms, Confidence], match_disease(Disease, MatchedSymptoms, Confidence), UnsortedMatches),
    predsort(compare_confidence, UnsortedMatches, Matches).

% Helper for sorting by confidence descending
compare_confidence(Order, [_, _, Conf1], [_, _, Conf2]) :-
    (Conf1 < Conf2 -> Order = >
    ; Conf1 > Conf2 -> Order = <
    ; Order = =).
