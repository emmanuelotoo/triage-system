# Triage  System

## Overview

A rule-based expert system using **Prolog** for inference and **Python** for the user interface. Classifies symptom urgency as Critical, Urgent, Moderate, or Low using backward chaining.

## Prerequisites

- [SWI-Prolog](https://www.swi-prolog.org/Download.html) (on PATH)
- Python 3.8+
- `pyswip` (`pip install pyswip`)

## Quick Start

```bash
pip install -r requirements.txt
python triage.py
```

## Project Structure

```
triage_kb.pl       Prolog knowledge base — symptoms, rules, inference engine
triage.py          Python CLI + pyswip integration
test_triage.py     Automated test suite (28 tests)
requirements.txt   Python dependencies
```

## How It Works

1. User selects symptoms via the CLI
2. Python asserts symptom facts into Prolog at runtime via pyswip
3. Prolog evaluates rules in priority order (Critical → Urgent → Moderate → Low) using backward chaining
4. The highest matching urgency level is returned with explanations of which rules fired

### Adding Rules

Add a `triage_rule/3` clause and `available_symptom/2` fact in `triage_kb.pl` — no Python changes needed:

```prolog
triage_rule(urgent, rule_burns,
    'Burns covering a large area require urgent medical attention.') :-
    has(severe_burns).

available_symptom(severe_burns, 'Severe burns').
```

## Tests

```bash
python test_triage.py
# or
pytest test_triage.py -v
```

## License

Educational use only.
