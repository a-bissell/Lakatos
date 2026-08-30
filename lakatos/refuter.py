"""lakatos/refuter.py — the adversarial promotion path, domain-agnostic.

Extracted from refuter.py (FRAMEWORK.md step 4). The anti-drift core:
  * The refuter's JOB is to kill conjectures; it is built to want them dead.
  * A conjecture NEVER earns THEOREM from testing alone. Empirical
    non-refutation is not a proof. The top status this module awards is
    ROBUST_CONJECTURE.
  * refute() reports the FALSE-CONFIDENCE DELTA: the gap between what a
    confirmatory loop (test only the inspiring scales) would commit, and what
    survives adversarial attack — the drift being measured.

A Conjecture is pure data over a domain's own parameter tuples: an
instance_test(*params) -> (ok, witness, n_cases) and a scale(*params) -> int
(bigger = harder). Nothing here is card-specific; the card targeting instances
and the drift specimens live in the domain (refuter.py).

Status ladder (load-bearing labels):
  NOT_A_CANDIDATE    fails even at the scales that inspired it
  CANDIDATE          holds at inspiring scales; not yet attacked
  CONJECTURE         survived some attack beyond inspiring scales
  ROBUST_CONJECTURE  survived the full adversarial battery; still no proof
  THEOREM            has a proof  <-- UNREACHABLE HERE, BY DESIGN
  REFUTED            counterexample found (witness recorded)
"""
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Conjecture:
    name: str
    claim: str
    instance_test: Callable[..., tuple]   # param -> (ok, witness, n_cases)
    scale: Callable[..., int]             # param -> difficulty (bigger = harder)
    inspiring: list                       # params that suggested the pattern
    beyond: list = field(default_factory=list)     # params of larger scale
    boundary: list = field(default_factory=list)   # extreme params
    random_draw: list = field(default_factory=list)
    param_names: tuple = None             # optional, for envelope reporting


def confirmatory_verdict(conj):
    """The LAZY loop this project keeps drifting into: test only the inspiring
    scales; if they pass, commit. Returns (committed, cases)."""
    cases = 0
    for p in conj.inspiring:
        ok, _, nc = conj.instance_test(*p); cases += nc
        if not ok:
            return False, cases
    return True, cases


def refute(conj, verbose=True):
    """Adversarial promotion path. Attacks in cost order, stops at first kill."""
    log = []
    def line(s):
        log.append(s)
        if verbose: print(s)

    line(f"── {conj.name} ──")
    line(f"   claim: {conj.claim}")

    # 0. must hold where it was seen, or it was never even a candidate
    max_insp, cases = 0, 0
    for p in conj.inspiring:
        ok, w, nc = conj.instance_test(*p)
        max_insp = max(max_insp, conj.scale(*p))
        cases += nc
        if not ok:
            line(f"   [inspiring {p}] FAILS -> NOT_A_CANDIDATE  witness={w}")
            return {'status': 'NOT_A_CANDIDATE', 'witness': w, 'cases': cases,
                    'log': log}
    line(f"   inspiring scales hold (max scale {max_insp}); "
         f"a confirmatory loop would COMMIT this now.")

    # 1. adversarial battery: boundary + beyond + random, cheapest first
    attack = []
    for tag, params in (('boundary', conj.boundary),
                        ('beyond', conj.beyond),
                        ('random', conj.random_draw)):
        for p in params:
            attack.append((conj.scale(*p), tag, p))
    attack.sort()  # cheap first so a kill costs little

    tested = 0
    for sc, tag, p in attack:
        ok, w, nc = conj.instance_test(*p)
        tested += 1
        cases += nc
        beyond_flag = " (scale>inspiring)" if sc > max_insp else ""
        if not ok:
            line(f"   [{tag} {p}]{beyond_flag} COUNTEREXAMPLE -> REFUTED")
            line(f"      witness: {w}")
            line(f"      false-confidence delta: confirmatory loop COMMITS; "
                 f"refuter KILLS at scale {sc}.")
            return {'status': 'REFUTED', 'witness': w, 'killed_at': p,
                    'attacks_before_kill': tested, 'cases': cases, 'log': log}
        else:
            line(f"   [{tag} {p}]{beyond_flag} holds ({nc} cases)")

    # graded verdict — 'robust' is earned by scale BEYOND inspiring, not by
    # merely having a list of attacks. An empty or too-timid battery must
    # not launder a CANDIDATE into a robust stamp.
    envelope = None
    if conj.param_names:
        allp = list(conj.inspiring) + [p for _, _, p in attack]
        envelope = {nm: max(p[i] for p in allp)
                    for i, nm in enumerate(conj.param_names)}
    span = [sc for sc, _, _ in attack]
    if tested == 0:
        line("   NO attacks scheduled -> CANDIDATE (holds where seen; "
             "not yet attacked).")
        return {'status': 'CANDIDATE', 'witness': None, 'attacks_survived': 0,
                'max_scale': max_insp, 'cases': cases, 'envelope': envelope,
                'log': log}
    if all(sc <= max_insp for sc in span):
        line(f"   survived {tested} attacks, but none exceeded inspiring "
             f"scale {max_insp} -> CONJECTURE (never attacked beyond).")
        return {'status': 'CONJECTURE', 'witness': None,
                'attacks_survived': tested, 'max_scale': max(span),
                'cases': cases, 'envelope': envelope, 'log': log}
    line(f"   survived {tested} adversarial params, scale up to {max(span)} "
         f"(inspiring max {max_insp}).")
    if envelope:
        line(f"   envelope: {envelope}")
    line(f"   -> ROBUST_CONJECTURE (empirical). NOT a theorem: no proof exists.")
    return {'status': 'ROBUST_CONJECTURE', 'witness': None,
            'attacks_survived': tested, 'max_scale': max(span),
            'cases': cases, 'envelope': envelope, 'log': log}


# ---- unit checks (run at import; over generic integer-parameter conjectures) --

def _unit_refuter():
    # holds everywhere -> attacked beyond inspiring -> ROBUST_CONJECTURE
    true_c = Conjecture(
        name='unit-true', claim='always holds',
        instance_test=lambda n: (True, None, 1), scale=lambda n: n,
        inspiring=[(2,)], beyond=[(10,)], param_names=('n',))
    r = refute(true_c, verbose=False)
    assert r['status'] == 'ROBUST_CONJECTURE', r['status']
    assert confirmatory_verdict(true_c)[0] is True
    # fails past 5 -> the beyond attack kills it, witness recorded
    false_c = Conjecture(
        name='unit-false', claim='n <= 5',
        instance_test=lambda n: (n <= 5, None if n <= 5 else {'n': n}, 1),
        scale=lambda n: n, inspiring=[(3,)], beyond=[(9,)], param_names=('n',))
    r = refute(false_c, verbose=False)
    assert r['status'] == 'REFUTED' and r['killed_at'] == (9,), r
    # holds only where seen, never attacked beyond -> CONJECTURE, not ROBUST
    timid = Conjecture(
        name='unit-timid', claim='untested beyond',
        instance_test=lambda n: (True, None, 1), scale=lambda n: n,
        inspiring=[(5,)], boundary=[(2,)], param_names=('n',))
    assert refute(timid, verbose=False)['status'] == 'CONJECTURE'


_unit_refuter()


if __name__ == '__main__':
    print('lakatos/refuter.py unit checks: PASS (ROBUST / REFUTED / CONJECTURE '
          'grading; a timid battery cannot launder a robust stamp)')
