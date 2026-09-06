"""lakatos/protocols.py — the published contract between the engine and a domain.

FRAMEWORK.md step 5. A domain supplies four plugs and inherits everything else;
the universal currency across every seam is one triple, never a domain object:

    (holds: bool, witness: Any|None, n_cases: int)

The four plugs:

  Plug 1  Decider           the one non-negotiable. A total, deterministic,
                            exhaustive check over a bounded free-choice domain.
                            A domain without one can still run the loop, but
                            the refuter degrades to sampling and the
                            false-confidence delta loses its teeth — SAY SO.
  Plug 2  Recognizers       bare callables cand -> hit|None, where hit =
                            {'family': str, 'confidence': 'exact'|'abstain',
                             'witness': str}. Family names travel IN THE HIT
                            (and in RecognizerSet.checked), not as attributes —
                            recognizers are typically plain functions. The
                            policy (asymmetric error, sampling pin, log-and-
                            suppress) is lakatos.oracle's; only the list is
                            the domain's.
  Plug 3  Candidate source  an iterable of candidates; each has .name and
                            .provenance plus any subset of oracle_view /
                            parametric / conjecture_spec. EngineCandidate in
                            lakatos.engine is the reference shape.
  Plug 4  Parameter sig.    pure data: axes, inspiring, valid, cost, cap,
                            instance_test. The refuter attacks from this
                            signature and never touches a domain object.

Check scope — the refuter's sampling pin. Every instance test DECLARES how
much of the free-choice domain it checked at each parameter point:

  'exhaustive'  every case at the point was checked. Earned by construction
                through decider_test() (Plug 1 building Plug 4), or vouched
                for by the domain author with exhaustive(). Only this scope
                can reach ROBUST_CONJECTURE.
  'sampled'     anything less. The top rung is then ROBUST_SAMPLED.

Undeclared means 'sampled' — the same asymmetric-error rule as the oracle's
sampling pin: exhaustiveness must be earned, never assumed. This is what makes
the Decider load-bearing rather than decorative: the engine cannot inspect an
instance test, so the tag is how a Decider check is told apart from a loop
that merely claims to be one.

Honesty note on the Protocol classes: @runtime_checkable isinstance checks
attribute EXISTENCE only — not signatures, not return shapes. The real teeth
are the check_* validators below (mechanical key/callable checks that name
what is missing) and, above them, a domain's own conformance ledger: for
cards, the engine dry-run (engine.py). A Protocol match is a hint; a passing
ledger is the claim.
"""
from typing import Any, Callable, Iterator, Optional, Protocol, Tuple, \
    runtime_checkable

# the universal triple: (holds, witness, n_cases)
Triple = Tuple[bool, Any, int]

# an instance test maps one parameter tuple to the triple
InstanceTest = Callable[..., Triple]


# ---- check scope (the refuter's sampling pin) --------------------------------

SCOPES = ('exhaustive', 'sampled')
DEFAULT_SCOPE = 'sampled'          # undeclared = sampled: earn it, never assume


def declare_scope(test, scope):
    """Tag an instance test with its check scope. Returns the test."""
    assert scope in SCOPES, f'scope must be one of {SCOPES}, got {scope!r}'
    test.scope = scope
    return test


def exhaustive(test):
    """The domain author's word that `test` checks its ENTIRE free-choice
    domain at every parameter point. Prefer decider_test, which earns the tag
    by construction instead of by say-so."""
    return declare_scope(test, 'exhaustive')


def sampled(test):
    return declare_scope(test, 'sampled')


def test_scope(test):
    """The declared scope of an instance test; undeclared = 'sampled'."""
    return getattr(test, 'scope', DEFAULT_SCOPE)


def decider_test(decider, claim_of, domain_of, kwargs_of=None):
    """Plug 4 from Plug 1. Build an instance test that routes EVERY parameter
    point through the Decider:  params -> decider.check(claim_of(*params),
    domain_of(*params), **kwargs_of(*params)).  Tagged 'exhaustive' by
    construction — the Decider's contract is the exhaustive check, so a test
    built this way cannot be anything else."""
    def instance_test(*params):
        kw = kwargs_of(*params) if kwargs_of is not None else {}
        return decider.check(claim_of(*params), domain_of(*params), **kw)
    instance_test.__name__ = 'decider_test'
    return exhaustive(instance_test)


# ---- Plug 1: the Decider -----------------------------------------------------

@runtime_checkable
class Decider(Protocol):
    def check(self, claim, domain) -> Triple:
        """Evaluate `claim` over the ENTIRE free-choice `domain`. Total and
        deterministic: the harness decides correctness, never a narrative
        about it. Returns (holds, witness_or_None, n_cases)."""
        ...


# ---- Plug 2: a Recognizer ----------------------------------------------------

@runtime_checkable
class Recognizer(Protocol):
    def __call__(self, cand) -> Optional[dict]:
        """None = no opinion. A hit dict carries family / confidence /
        witness; 'exact' is only safe on an exhaustive sample (the policy's
        sampling pin enforces that — do not work around it)."""
        ...


# ---- Plug 3: a Candidate source ----------------------------------------------

@runtime_checkable
class CandidateSource(Protocol):
    def __iter__(self) -> Iterator: ...


# ---- run_engine's injected plugs (see lakatos.engine docstring) --------------

Classify = Callable[..., dict]           # (oracle_view_result, log) -> verdict
Fit = Callable[..., Any]                 # (query, grid) -> model | None
MakeInstanceTest = Callable[..., InstanceTest]   # (model, query) -> test


# ---- the validators (the real teeth) -----------------------------------------

_CONJ_KEYS = ('claim', 'instance', 'axes', 'inspiring', 'valid', 'cost', 'cap')
_PARAM_KEYS = ('claim', 'query', 'fit_grid', 'axes', 'valid', 'cost', 'cap')


def _need(spec, keys, callables, what):
    missing = [k for k in keys if k not in spec]
    assert not missing, f'{what}: missing {missing}'
    bad = [k for k in callables if not callable(spec[k])]
    assert not bad, f'{what}: not callable: {bad}'


def check_conjecture_spec(spec):
    """A ready-made claim (EngineCandidate.conjecture_spec): the zero-plug
    path — this is all a new domain needs to run the refuter."""
    _need(spec, _CONJ_KEYS, ('instance', 'valid', 'cost'), 'conjecture_spec')


def check_parametric(spec):
    """A black-box family for the former (EngineCandidate.parametric)."""
    _need(spec, _PARAM_KEYS, ('query', 'valid', 'cost'), 'parametric')


def check_plugs(classify=None, fit=None, make_instance_test=None):
    """Validate a domain's run_engine wiring. Any plug may be None (the loop
    skips that stage) but a supplied plug must be callable, and fit and
    make_instance_test only make sense together."""
    for name, f in (('classify', classify), ('fit', fit),
                    ('make_instance_test', make_instance_test)):
        assert f is None or callable(f), f'plug {name} is not callable'
    assert (fit is None) == (make_instance_test is None), \
        'fit and make_instance_test must be supplied together'


# ---- unit checks (run at import) ---------------------------------------------

def _unit_protocols():
    ok = dict(claim='c', instance=lambda n: (True, None, 1), axes=[],
              inspiring=[(2,)], valid=lambda n: True, cost=lambda n: n,
              cap=10)
    check_conjecture_spec(ok)
    for missing_key in ('instance', 'cap'):
        bad = {k: v for k, v in ok.items() if k != missing_key}
        try:
            check_conjecture_spec(bad)
        except AssertionError:
            continue
        raise AssertionError(f'accepted spec missing {missing_key}')
    try:
        check_conjecture_spec(dict(ok, valid='not callable'))
    except AssertionError:
        pass
    else:
        raise AssertionError('accepted non-callable valid')
    check_plugs()                       # all-None: the zero-plug path
    check_plugs(classify=lambda c, l: {})
    try:
        check_plugs(fit=lambda q, g: None)   # fit without make_instance_test
    except AssertionError:
        pass
    else:
        raise AssertionError('accepted fit without make_instance_test')

    class D:
        def check(self, claim, domain, k=1):
            return (claim == len(domain), None, len(domain) * k)
    assert isinstance(D(), Decider)
    assert not isinstance(object(), Decider)

    # scope: undeclared is SAMPLED; declared sticks; junk is rejected
    f = lambda n: (True, None, 1)
    assert test_scope(f) == 'sampled'
    assert test_scope(exhaustive(f)) == 'exhaustive'
    assert test_scope(sampled(f)) == 'sampled'
    try:
        declare_scope(f, 'partial')
    except AssertionError:
        pass
    else:
        raise AssertionError('accepted an unknown scope')
    # a Decider-built test is exhaustive by construction and threads kwargs
    t = decider_test(D(), lambda n: n, lambda n: list(range(n)),
                     lambda n: {'k': 2})
    assert test_scope(t) == 'exhaustive'
    assert t(3) == (True, None, 6), t(3)
    assert decider_test(D(), lambda n: n + 1, lambda n: list(range(n)))(3)[0] \
        is False


_unit_protocols()


if __name__ == '__main__':
    print('lakatos/protocols.py unit checks: PASS (spec validators reject '
          'missing keys / non-callables; plug pairing enforced; Decider '
          'protocol structurally checkable; scope: undeclared = sampled, '
          'decider_test = exhaustive by construction)')
