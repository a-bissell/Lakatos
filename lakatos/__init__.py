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
                        + the check-scope tags (exhaustive / sampled / decider_test)
  lakatos.proof_kernel  Farkas certificate kernel (needs sympy, an optional
                        dependency — `pip install lakatos[proof]`; import it
                        explicitly: `from lakatos.proof_kernel import Ctx`)

The universal currency across every seam is one triple, never a domain object:

    (holds: bool, witness: Any|None, n_cases: int)

Each module runs its unit checks at import (repo convention); they are
milliseconds. The package itself loads submodules LAZILY (PEP 562), so
`from lakatos import refute` runs the refuter's checks and nothing else, and
`python3 -m lakatos.<module>` runs that module's own ledger without runpy's
"found in sys.modules" warning. To run every module's checks at once:

    python3 -m lakatos              # all ledgers, one line each
    python3 -m lakatos refuter      # one module's full ledger + demo
"""
import importlib

_EXPORTS = {
    'Decider': 'lakatos.protocols', 'Recognizer': 'lakatos.protocols',
    'CandidateSource': 'lakatos.protocols', 'InstanceTest': 'lakatos.protocols',
    'Triple': 'lakatos.protocols', 'check_conjecture_spec': 'lakatos.protocols',
    'check_parametric': 'lakatos.protocols', 'check_plugs': 'lakatos.protocols',
    'SCOPES': 'lakatos.protocols', 'declare_scope': 'lakatos.protocols',
    'exhaustive': 'lakatos.protocols', 'sampled': 'lakatos.protocols',
    'test_scope': 'lakatos.protocols', 'decider_test': 'lakatos.protocols',
    'Axis': 'lakatos.schedule', 'derive_schedule': 'lakatos.schedule',
    'auto_conjecture': 'lakatos.schedule',
    'FeatureBasis': 'lakatos.fitter', 'exact_fit': 'lakatos.fitter',
    'fit_tree': 'lakatos.fitter', 'tree_eval': 'lakatos.fitter',
    'tree_str': 'lakatos.fitter', 'simplify_tree': 'lakatos.fitter',
    'Leaf': 'lakatos.fitter', 'Node': 'lakatos.fitter',
    'SuppressedLog': 'lakatos.oracle', 'RecognizerSet': 'lakatos.oracle',
    'classify': 'lakatos.oracle',
    'Conjecture': 'lakatos.refuter', 'confirmatory_verdict': 'lakatos.refuter',
    'refute': 'lakatos.refuter',
    'run_engine': 'lakatos.engine', 'EngineCandidate': 'lakatos.engine',
    'DEFAULT_BUDGET': 'lakatos.engine',
}

__all__ = sorted(_EXPORTS)

# every module with an import-time ledger, in dependency order
LEDGER_MODULES = ('protocols', 'schedule', 'fitter', 'oracle', 'refuter',
                  'engine', 'proof_kernel')


def __getattr__(name):
    if name in _EXPORTS:
        value = getattr(importlib.import_module(_EXPORTS[name]), name)
        globals()[name] = value           # cache: __getattr__ runs once per name
        return value
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def __dir__():
    return sorted(set(globals()) | set(_EXPORTS))
