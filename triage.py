"""Neutral Minds — Medical Triage Expert System (Python CLI + Prolog integration)."""

import sys
from pathlib import Path

try:
    from pyswip import Prolog
except ImportError:
    print("ERROR: pyswip is not installed.")
    print("Install it with:  pip install pyswip")
    print("Also ensure SWI-Prolog is installed and on your system PATH.")
    sys.exit(1)


KB_PATH = Path(__file__).parent / "triage_kb.pl"

DISCLAIMER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║  ⚠  DISCLAIMER                                                            ║
║                                                                            ║
║  Neutral Minds is a DEMONSTRATION rule-based triage system.                ║
║  It is NOT a medical diagnostic tool.                                      ║
║  It does NOT replace professional medical advice, diagnosis, or treatment. ║
║                                                                            ║
║  If you are experiencing a medical emergency, call your local emergency    ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

URGENCY_COLORS = {
    "critical": "\033[91m",
    "urgent":   "\033[93m",
    "moderate": "\033[96m",
    "low":      "\033[92m",
    "none":     "\033[90m",
}
RESET_COLOR = "\033[0m"
BOLD = "\033[1m"


class TriageEngine:
    """Wraps pyswip's Prolog interface for symptom management and triage querying."""

    def __init__(self, kb_path: str | Path = KB_PATH):
        self.prolog = Prolog()
        kb_posix = str(Path(kb_path).resolve()).replace("\\", "/")
        if not Path(kb_path).exists():
            raise FileNotFoundError(f"Knowledge base not found: {kb_path}")
        self.prolog.consult(kb_posix)
        list(self.prolog.query("clear_symptoms"))

    def add_symptom(self, symptom: str) -> None:
        list(self.prolog.query(f"add_symptom({symptom})"))

    def remove_symptom(self, symptom: str) -> None:
        list(self.prolog.query(f"remove_symptom({symptom})"))

    def clear_symptoms(self) -> None:
        list(self.prolog.query("clear_symptoms"))

    def get_current_symptoms(self) -> list[str]:
        results = list(self.prolog.query("current_symptoms(S)"))
        if results:
            return [str(s) for s in results[0]["S"]]
        return []

    def get_available_symptoms(self) -> list[tuple[str, str]]:
        results = list(self.prolog.query("available_symptom(Id, Desc)"))
        return [(str(r["Id"]), str(r["Desc"])) for r in results]

    def run_triage(self) -> tuple[str, list[str]]:
        results = list(self.prolog.query("triage(Level, Explanations)"))
        if results:
            level = str(results[0]["Level"])
            explanations = [str(e) for e in results[0]["Explanations"]]
            return level, explanations
        return "none", ["Unable to determine triage level."]

    def run_triage_all(self) -> list[tuple[str, list[str]]]:
        all_levels = []
        for level in ["critical", "urgent", "moderate", "low"]:
            results = list(self.prolog.query(
                f"fired_rules({level}, Rules), Rules \\= [], "
                f"extract_explanations(Rules, Explanations)"
            ))
            if results:
                explanations = [str(e) for e in results[0]["Explanations"]]
                all_levels.append((level, explanations))
        return all_levels


def print_banner():
    print(f"""
{BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║               🏥  NEUTRAL MINDS  —  Medical Triage Expert System             ║
║                        Rule-Based Urgency Classification                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{RESET_COLOR}
""")


def print_disclaimer():
    print(f"{URGENCY_COLORS['urgent']}{DISCLAIMER}{RESET_COLOR}")


def display_symptom_menu(symptoms: list[tuple[str, str]]):
    print(f"\n{BOLD}Available Symptoms:{RESET_COLOR}")
    print("-" * 50)
    for i, (sid, desc) in enumerate(symptoms, 1):
        print(f"  {i:>2}. {desc} ({sid})")
    print("-" * 50)
    print(f"  {BOLD} 0.  Done — Run triage{RESET_COLOR}")
    print(f"  {BOLD}-1.  Clear all symptoms{RESET_COLOR}")
    print(f"  {BOLD}-2.  Quit{RESET_COLOR}")
    print()


def display_triage_result(level: str, explanations: list[str],
                          all_levels: list[tuple[str, list[str]]] | None = None):
    color = URGENCY_COLORS.get(level, "")

    print(f"\n{'=' * 70}")
    print(f"{BOLD}{color}  TRIAGE RESULT:  {level.upper()}{RESET_COLOR}")
    print(f"{'=' * 70}")

    print(f"\n{BOLD}Triggered Rules (highest priority — {level.upper()}):{RESET_COLOR}")
    for i, exp in enumerate(explanations, 1):
        print(f"  {color}▸ Rule {i}:{RESET_COLOR} {exp}")

    if all_levels and len(all_levels) > 1:
        print(f"\n{BOLD}Other matching levels (lower priority):{RESET_COLOR}")
        for lvl, exps in all_levels:
            if lvl == level:
                continue  # already shown above
            lvl_color = URGENCY_COLORS.get(lvl, "")
            print(f"\n  {lvl_color}[{lvl.upper()}]{RESET_COLOR}")
            for exp in exps:
                print(f"    ▸ {exp}")

    print(f"\n{BOLD}Recommended Action:{RESET_COLOR}")
    actions = {
        "critical": "🚨 Seek IMMEDIATE emergency medical attention. Call emergency services NOW.",
        "urgent":   "⚠️  Seek medical attention as soon as possible (within hours).",
        "moderate":  "🩺 Schedule a medical appointment soon (within 24-48 hours).",
        "low":      "💊 Monitor symptoms. Visit a healthcare provider if they persist or worsen.",
        "none":     "ℹ️  No matching rules. Consider consulting a healthcare provider if concerned.",
    }
    print(f"  {color}{actions.get(level, actions['none'])}{RESET_COLOR}")
    print()


def run_interactive():
    print_banner()
    print_disclaimer()

    try:
        engine = TriageEngine()
    except FileNotFoundError as e:
        print(f"\n{URGENCY_COLORS['critical']}ERROR: {e}{RESET_COLOR}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{URGENCY_COLORS['critical']}ERROR initializing Prolog engine: {e}{RESET_COLOR}")
        sys.exit(1)

    available = engine.get_available_symptoms()
    if not available:
        print("WARNING: No available symptoms loaded from knowledge base.")
        sys.exit(1)

    selected_symptoms: list[str] = []

    while True:
        if selected_symptoms:
            print(f"\n{BOLD}Currently selected symptoms:{RESET_COLOR}")
            for sym in selected_symptoms:
                desc = next((d for s, d in available if s == sym), sym)
                print(f"  ✓ {desc} ({sym})")

        display_symptom_menu(available)

        try:
            choice = input(f"{BOLD}Enter symptom number(s) (comma-separated) or command: {RESET_COLOR}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not choice:
            continue

        entries = [c.strip() for c in choice.split(",")]

        should_run_triage = False

        for entry in entries:
            try:
                num = int(entry)
            except ValueError:
                matching = [s for s, d in available if s == entry.lower().replace(" ", "_")]
                if matching:
                    sym_id = matching[0]
                    if sym_id not in selected_symptoms:
                        engine.add_symptom(sym_id)
                        selected_symptoms.append(sym_id)
                        desc = next((d for s, d in available if s == sym_id), sym_id)
                        print(f"  ✓ Added: {desc}")
                else:
                    print(f"  ✗ Unknown input: '{entry}'")
                continue

            if num == 0:
                should_run_triage = True
                continue
            elif num == -1:
                engine.clear_symptoms()
                selected_symptoms.clear()
                print("  ✓ All symptoms cleared.")
                continue
            elif num == -2:
                print("\nGoodbye! Remember: consult a real medical professional.\n")
                return
            elif 1 <= num <= len(available):
                sym_id, desc = available[num - 1]
                if sym_id in selected_symptoms:
                    print(f"  ⓘ Already selected: {desc}")
                else:
                    engine.add_symptom(sym_id)
                    selected_symptoms.append(sym_id)
                    print(f"  ✓ Added: {desc}")
            else:
                print(f"  ✗ Invalid number: {num}")

        if should_run_triage:
            if not selected_symptoms:
                print("\n  ⚠ No symptoms selected. Please add at least one symptom.")
                continue

            level, explanations = engine.run_triage()

            try:
                all_levels = engine.run_triage_all()
            except Exception:
                all_levels = None

            display_triage_result(level, explanations, all_levels)
            print_disclaimer()

            try:
                again = input(f"{BOLD}Run another triage? (y/n): {RESET_COLOR}").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n\nGoodbye!")
                break

            if again in ("y", "yes"):
                engine.clear_symptoms()
                selected_symptoms.clear()
                print("\n  ✓ Symptoms cleared for new assessment.\n")
            else:
                print("\nGoodbye! Remember: consult a real medical professional.\n")
                break


def run_triage_for_symptoms(symptoms: list[str]) -> dict:
    """Programmatic API: returns triage result dict for a list of symptom IDs."""
    engine = TriageEngine()

    for symptom in symptoms:
        engine.add_symptom(symptom)

    level, explanations = engine.run_triage()

    try:
        all_levels = engine.run_triage_all()
        all_levels_dict = {lvl: exps for lvl, exps in all_levels}
    except Exception:
        all_levels_dict = {}

    return {
        "level": level,
        "explanations": explanations,
        "all_levels": all_levels_dict,
        "symptoms": symptoms,
    }


if __name__ == "__main__":
    run_interactive()
