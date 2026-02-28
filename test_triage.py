"""Neutral Minds — Automated test suite for triage rules."""

import sys
import unittest

try:
    from triage import TriageEngine, run_triage_for_symptoms
except ImportError as e:
    print(f"Import error: {e}")
    print("Ensure triage.py and triage_kb.pl are in the same directory.")
    sys.exit(1)


class TestTriageRules(unittest.TestCase):

    def test_critical_chest_pain_and_breathing(self):
        """Chest pain + shortness of breath → CRITICAL"""
        result = run_triage_for_symptoms(["chest_pain", "shortness_of_breath"])
        self.assertEqual(result["level"], "critical")
        self.assertTrue(any("cardiac" in e.lower() or "pulmonary" in e.lower()
                            for e in result["explanations"]))

    def test_critical_chest_pain_and_arm_pain(self):
        """Chest pain + left arm pain → CRITICAL"""
        result = run_triage_for_symptoms(["chest_pain", "left_arm_pain"])
        self.assertEqual(result["level"], "critical")
        self.assertTrue(any("myocardial" in e.lower()
                            for e in result["explanations"]))

    def test_critical_unresponsive(self):
        """Unresponsive → CRITICAL"""
        result = run_triage_for_symptoms(["unresponsive"])
        self.assertEqual(result["level"], "critical")

    def test_critical_severe_bleeding(self):
        """Severe bleeding → CRITICAL"""
        result = run_triage_for_symptoms(["severe_bleeding"])
        self.assertEqual(result["level"], "critical")

    def test_critical_seizure(self):
        """Seizure → CRITICAL"""
        result = run_triage_for_symptoms(["seizure"])
        self.assertEqual(result["level"], "critical")

    def test_critical_stroke_signs(self):
        """Sudden numbness + confusion + severe headache → CRITICAL (stroke)"""
        result = run_triage_for_symptoms(["sudden_numbness", "confusion", "severe_headache"])
        self.assertEqual(result["level"], "critical")
        self.assertTrue(any("stroke" in e.lower()
                            for e in result["explanations"]))

    def test_urgent_high_fever_vomiting(self):
        """High fever + persistent vomiting → URGENT"""
        result = run_triage_for_symptoms(["high_fever", "persistent_vomiting"])
        self.assertEqual(result["level"], "urgent")

    def test_urgent_high_fever_stiff_neck(self):
        """High fever + stiff neck → URGENT (meningitis risk)"""
        result = run_triage_for_symptoms(["high_fever", "stiff_neck"])
        self.assertEqual(result["level"], "urgent")
        self.assertTrue(any("meningitis" in e.lower()
                            for e in result["explanations"]))

    def test_urgent_severe_abdominal_pain(self):
        """Severe abdominal pain → URGENT"""
        result = run_triage_for_symptoms(["severe_abdominal_pain"])
        self.assertEqual(result["level"], "urgent")

    def test_urgent_chest_pain_alone(self):
        """Chest pain alone → URGENT (not critical without second symptom)"""
        result = run_triage_for_symptoms(["chest_pain"])
        self.assertEqual(result["level"], "urgent")

    def test_moderate_fever_cough(self):
        """Fever + cough → MODERATE"""
        result = run_triage_for_symptoms(["fever", "cough"])
        self.assertEqual(result["level"], "moderate")

    def test_moderate_headache_dizziness(self):
        """Headache + dizziness → MODERATE"""
        result = run_triage_for_symptoms(["headache", "dizziness"])
        self.assertEqual(result["level"], "moderate")

    def test_moderate_fever_bodyache(self):
        """Fever + body ache → MODERATE"""
        result = run_triage_for_symptoms(["fever", "body_ache"])
        self.assertEqual(result["level"], "moderate")

    def test_moderate_joint_pain_swelling(self):
        """Joint pain + swelling → MODERATE"""
        result = run_triage_for_symptoms(["joint_pain", "swelling"])
        self.assertEqual(result["level"], "moderate")

    def test_low_headache_alone(self):
        """Headache alone → LOW"""
        result = run_triage_for_symptoms(["headache"])
        self.assertEqual(result["level"], "low")

    def test_low_runny_nose(self):
        """Runny nose → LOW"""
        result = run_triage_for_symptoms(["runny_nose"])
        self.assertEqual(result["level"], "low")

    def test_low_sore_throat(self):
        """Sore throat → LOW"""
        result = run_triage_for_symptoms(["sore_throat"])
        self.assertEqual(result["level"], "low")

    def test_low_fatigue(self):
        """Fatigue → LOW"""
        result = run_triage_for_symptoms(["fatigue"])
        self.assertEqual(result["level"], "low")

    def test_none_no_symptoms(self):
        """No symptoms → NONE"""
        result = run_triage_for_symptoms([])
        self.assertEqual(result["level"], "none")

    def test_priority_critical_beats_urgent(self):
        """
        Chest pain + shortness of breath fires CRITICAL.
        Chest pain alone also fires URGENT.
        Critical should win.
        """
        result = run_triage_for_symptoms(["chest_pain", "shortness_of_breath"])
        self.assertEqual(result["level"], "critical")

    def test_priority_urgent_beats_moderate(self):
        """
        High fever + persistent vomiting → URGENT.
        Persistent vomiting alone → MODERATE.
        Urgent should win.
        """
        result = run_triage_for_symptoms(["high_fever", "persistent_vomiting"])
        self.assertEqual(result["level"], "urgent")

    def test_priority_moderate_beats_low(self):
        """
        Fever + cough → MODERATE.
        Fever alone → LOW; Cough alone → LOW.
        Moderate should win.
        """
        result = run_triage_for_symptoms(["fever", "cough"])
        self.assertEqual(result["level"], "moderate")

    def test_complex_multi_symptom(self):
        """
        Many symptoms: chest_pain + shortness_of_breath + fever + cough + headache
        Should be CRITICAL (chest_pain + shortness_of_breath fires critical rule).
        """
        result = run_triage_for_symptoms([
            "chest_pain", "shortness_of_breath", "fever", "cough", "headache"
        ])
        self.assertEqual(result["level"], "critical")

    def test_all_levels_populated(self):
        """
        With a rich symptom set, multiple urgency levels should be present
        in the all_levels breakdown.
        """
        result = run_triage_for_symptoms([
            "chest_pain", "shortness_of_breath",  # critical
            "high_fever", "persistent_vomiting",   # urgent
            "fever", "cough",                       # moderate
            "headache",                             # low
        ])
        self.assertEqual(result["level"], "critical")
        # Check that lower levels are also reported
        self.assertIn("urgent", result.get("all_levels", {}))
        self.assertIn("low", result.get("all_levels", {}))


class TestEngineManagement(unittest.TestCase):

    def setUp(self):
        self.engine = TriageEngine()

    def test_add_and_list_symptoms(self):
        """Symptoms can be added and retrieved."""
        self.engine.add_symptom("fever")
        self.engine.add_symptom("cough")
        current = self.engine.get_current_symptoms()
        self.assertIn("fever", current)
        self.assertIn("cough", current)

    def test_clear_symptoms(self):
        """Clearing symptoms removes all."""
        self.engine.add_symptom("fever")
        self.engine.clear_symptoms()
        current = self.engine.get_current_symptoms()
        self.assertEqual(len(current), 0)

    def test_idempotent_add(self):
        """Adding the same symptom twice does not duplicate it."""
        self.engine.add_symptom("fever")
        self.engine.add_symptom("fever")
        current = self.engine.get_current_symptoms()
        self.assertEqual(current.count("fever"), 1)

    def test_available_symptoms_populated(self):
        """The knowledge base provides a non-empty list of available symptoms."""
        available = self.engine.get_available_symptoms()
        self.assertGreater(len(available), 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
