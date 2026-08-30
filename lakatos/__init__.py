"""lakatos/ — the domain-agnostic Lakatos discovery engine.

Extracted from the card domain per FRAMEWORK.md (the package was `core/`
through step 4; renamed at packaging so it can be pip-installed under a
non-colliding name). Nothing in this package may import from a domain
(deck_sim, generator schemas, the card recognizers/proofs). Domains depend
on lakatos, never the reverse.

  lakatos.schedule      refuter attack-schedule derivation  (was refuter_auto.py)
  lakatos.fitter        exact fits + model trees over an injected FeatureBasis
  lakatos.oracle        rediscovery-filter policy: SuppressedLog, RecognizerSet, classify
  lakatos.refuter       Conjecture, refute(), the status ladder, false-confidence delta
  lakatos.engine        run_engine(): budgets, eight dispositions, drift metric
  lakatos.protocols     the published four-plug contract + mechanical validators
  lakatos.proof_kernel  Farkas certificate kernel (NOT imported here: needs sympy,
                        an optional dependency — `pip install lakatos[proof]`;
                        import it explicitly: `from lakatos.proof_kernel import Ctx`)

The universal currency across every seam is one triple, never a domain object:

    (holds: bool, witness: Any|None, n_cases: int)

Importing this package runs each module's import-time unit checks (repo
convention); they are milliseconds. Run any module's ledger as
`python3 -m lakatos.<module>` from the repo root (as a script the package
import would fail — the root would not be on sys.path).
"""
from lakatos.schedule import Axis, derive_schedule, auto_conjecture
from lakatos.fitter import (FeatureBasis, exact_fit, fit_tree, tree_eval,
                            tree_str, simplify_tree, Leaf, Node)
from lakatos.oracle import SuppressedLog, RecognizerSet, classify
from lakatos.refuter import Conjecture, confirmatory_verdict, refute
from lakatos.engine import run_engine, EngineCandidate, DEFAULT_BUDGET
from lakatos.protocols import (Decider, Recognizer, CandidateSource,
                               InstanceTest, Triple, check_conjecture_spec,
                               check_parametric, check_plugs)

__all__ = [
    'Decider', 'Recognizer', 'CandidateSource', 'InstanceTest', 'Triple',
    'check_conjecture_spec', 'check_parametric', 'check_plugs',
    'Axis', 'derive_schedule', 'auto_conjecture',
    'FeatureBasis', 'exact_fit', 'fit_tree', 'tree_eval', 'tree_str',
    'simplify_tree', 'Leaf', 'Node',
    'SuppressedLog', 'RecognizerSet', 'classify',
    'Conjecture', 'confirmatory_verdict', 'refute',
    'run_engine', 'EngineCandidate', 'DEFAULT_BUDGET',
]
