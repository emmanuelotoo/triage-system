% Neutral Minds — Prolog Knowledge Base & Inference Engine
% Uses backward chaining. Priority order: Critical > Urgent > Moderate > Low.

:- dynamic symptom/1.

has(Symptom) :- symptom(Symptom).

% --- CRITICAL ---

triage_rule(critical, rule_chest_pain_breathing,
    'Chest pain combined with shortness of breath may indicate a cardiac or pulmonary emergency.') :-
    has(chest_pain),
    has(shortness_of_breath).

triage_rule(critical, rule_chest_pain_arm_pain,
    'Chest pain with left arm pain is a classic sign of myocardial infarction.') :-
    has(chest_pain),
    has(left_arm_pain).

triage_rule(critical, rule_unresponsive,
    'Patient is unresponsive — immediate emergency intervention required.') :-
    has(unresponsive).

triage_rule(critical, rule_severe_bleeding,
    'Severe or uncontrolled bleeding requires emergency care.') :-
    has(severe_bleeding).

triage_rule(critical, rule_seizure,
    'Active seizure requires immediate medical attention.') :-
    has(seizure).

triage_rule(critical, rule_difficulty_breathing_cyanosis,
    'Difficulty breathing with cyanosis (blue skin) indicates critical oxygen deprivation.') :-
    has(shortness_of_breath),
    has(cyanosis).

triage_rule(critical, rule_stroke_signs,
    'Sudden numbness with confusion and severe headache may indicate a stroke.') :-
    has(sudden_numbness),
    has(confusion),
    has(severe_headache).

% --- URGENT ---

triage_rule(urgent, rule_high_fever_vomiting,
    'High fever with persistent vomiting suggests a serious infection or systemic illness.') :-
    has(high_fever),
    has(persistent_vomiting).

triage_rule(urgent, rule_high_fever_stiff_neck,
    'High fever with stiff neck may indicate meningitis.') :-
    has(high_fever),
    has(stiff_neck).

triage_rule(urgent, rule_chest_pain_alone,
    'Chest pain alone warrants urgent evaluation to rule out cardiac causes.') :-
    has(chest_pain).

triage_rule(urgent, rule_moderate_bleeding,
    'Moderate bleeding that is difficult to control needs urgent care.') :-
    has(moderate_bleeding).

triage_rule(urgent, rule_severe_abdominal_pain,
    'Severe abdominal pain may indicate appendicitis, obstruction, or other surgical emergency.') :-
    has(severe_abdominal_pain).

triage_rule(urgent, rule_high_fever_rash,
    'High fever with rash may indicate a serious infectious disease.') :-
    has(high_fever),
    has(rash).

triage_rule(urgent, rule_difficulty_breathing,
    'Significant shortness of breath without other critical signs requires urgent assessment.') :-
    has(shortness_of_breath).

triage_rule(urgent, rule_confusion,
    'Acute confusion or altered mental status requires urgent evaluation.') :-
    has(confusion).

% --- MODERATE ---

triage_rule(moderate, rule_fever_cough,
    'Fever with cough may indicate a respiratory infection requiring medical review.') :-
    has(fever),
    has(cough).

triage_rule(moderate, rule_mild_abdominal_pain,
    'Mild to moderate abdominal pain should be evaluated in a timely manner.') :-
    has(abdominal_pain).

triage_rule(moderate, rule_persistent_vomiting,
    'Persistent vomiting without high fever needs medical evaluation for dehydration risk.') :-
    has(persistent_vomiting).

triage_rule(moderate, rule_moderate_headache,
    'Moderate headache with other symptoms warrants a medical consultation.') :-
    has(headache),
    has(dizziness).

triage_rule(moderate, rule_minor_bleeding,
    'Minor bleeding that is controllable but persistent needs attention.') :-
    has(minor_bleeding).

triage_rule(moderate, rule_fever_body_ache,
    'Fever with body aches suggests flu or viral illness requiring monitoring.') :-
    has(fever),
    has(body_ache).

triage_rule(moderate, rule_sprain_swelling,
    'Joint pain with swelling suggests a sprain or fracture needing evaluation.') :-
    has(joint_pain),
    has(swelling).

% --- LOW ---

triage_rule(low, rule_mild_headache,
    'A mild headache without other concerning symptoms is low urgency.') :-
    has(headache).

triage_rule(low, rule_mild_fever,
    'Low-grade fever without additional symptoms is typically low urgency.') :-
    has(fever).

triage_rule(low, rule_runny_nose,
    'A runny nose or nasal congestion alone suggests a common cold.') :-
    has(runny_nose).

triage_rule(low, rule_sore_throat,
    'A sore throat without high fever is usually low urgency.') :-
    has(sore_throat).

triage_rule(low, rule_mild_cough,
    'A mild cough without fever is typically low urgency.') :-
    has(cough).

triage_rule(low, rule_fatigue,
    'General fatigue without other alarming symptoms is low urgency.') :-
    has(fatigue).

triage_rule(low, rule_skin_irritation,
    'Minor skin irritation or rash without fever is low urgency.') :-
    has(rash).

% --- INFERENCE ENGINE ---

fired_rules(Level, Rules) :-
    findall(
        rule(RuleName, Explanation),
        triage_rule(Level, RuleName, Explanation),
        Rules
    ).

priority(critical, 1).
priority(urgent,   2).
priority(moderate, 3).
priority(low,      4).

triage(Level, Explanations) :-
    member(Level, [critical, urgent, moderate, low]),
    fired_rules(Level, Rules),
    Rules \= [],
    extract_explanations(Rules, Explanations),
    !.

triage(none, ['No triage rules matched the reported symptoms. Please seek professional medical advice.']).

triage_all(Results) :-
    findall(
        level(Level, Explanations),
        (   member(Level, [critical, urgent, moderate, low]),
            fired_rules(Level, Rules),
            Rules \= [],
            extract_explanations(Rules, Explanations)
        ),
        Results
    ).

extract_explanations([], []).
extract_explanations([rule(_, Exp) | Rest], [Exp | Exps]) :-
    extract_explanations(Rest, Exps).

% --- SYMPTOM MANAGEMENT ---

add_symptom(S) :-
    ( symptom(S) -> true ; assert(symptom(S)) ).

remove_symptom(S) :-
    retractall(symptom(S)).

clear_symptoms :-
    retractall(symptom(_)).

current_symptoms(Symptoms) :-
    findall(S, symptom(S), Symptoms).

% --- AVAILABLE SYMPTOMS ---
available_symptom(chest_pain,          'Chest pain').
available_symptom(shortness_of_breath, 'Shortness of breath').
available_symptom(left_arm_pain,       'Left arm pain').
available_symptom(unresponsive,        'Unresponsive / unconscious').
available_symptom(severe_bleeding,     'Severe bleeding').
available_symptom(seizure,             'Active seizure').
available_symptom(cyanosis,            'Blue skin (cyanosis)').
available_symptom(sudden_numbness,     'Sudden numbness').
available_symptom(confusion,           'Confusion / altered mental status').
available_symptom(severe_headache,     'Severe headache').
available_symptom(high_fever,          'High fever (>39C / 102F)').
available_symptom(persistent_vomiting, 'Persistent vomiting').
available_symptom(stiff_neck,          'Stiff neck').
available_symptom(moderate_bleeding,   'Moderate bleeding').
available_symptom(severe_abdominal_pain,'Severe abdominal pain').
available_symptom(fever,               'Fever').
available_symptom(cough,              'Cough').
available_symptom(abdominal_pain,      'Abdominal pain').
available_symptom(headache,            'Headache').
available_symptom(dizziness,           'Dizziness').
available_symptom(minor_bleeding,      'Minor bleeding').
available_symptom(body_ache,           'Body ache').
available_symptom(joint_pain,          'Joint pain').
available_symptom(swelling,            'Swelling').
available_symptom(runny_nose,          'Runny nose').
available_symptom(sore_throat,         'Sore throat').
available_symptom(fatigue,             'Fatigue').
available_symptom(rash,               'Rash / skin irritation').
