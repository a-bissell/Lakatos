"""engine.py — card wiring for the integration loop (engine item 5).

The loop itself (run_engine, EngineCandidate, per-run BUDGETS, the eight
dispositions, the suppressed log as the live DRIFT metric) is domain-agnostic
and lives in lakatos/engine.py (FRAMEWORK.md step 4). This module wires the CARD
plugs into it — the novelty oracle as the rediscovery filter and the
affine-in-floor round former — and holds the dry-run that doubles as the
acceptance ledger, replaying a fixed candidate mix that exercises every
pipeline path against real library material:

  disposition          path exercised
  SUPPRESSED           oracle exact match on exhaustive sample (logged
                       with witness; the drift metric counts these)
  REVIEW               oracle ABSTAIN (e.g. the sampling pin: a family
                       match on a partial sample never suppresses)
  ROUTED               oracle NOT_MATCHED, no parametric content — a
                       procedure for the study backlog
  UNSTRUCTURED         former REFUSED the parametric family (outside its
                       grammar) — honest refusal, backlog for a richer
                       grammar, never a hallucinated fit
  SURVIVOR             former fit a closed form and the refuter awarded
                       ROBUST_CONJECTURE on a signature-derived schedule
                       (needs a PROVENANCE.md record before any
                       novelty claim — see provenance_audit.py)
  REFUTED              the refuter killed it; witness recorded — a kill
                       is a result, not a failure
  DOWNGRADED           refuter returned CANDIDATE/CONJECTURE (schedule
                       could not attack beyond inspiring scale)
  SKIPPED (budget)     run budget exhausted BEFORE this candidate — every
                       skip is named in the report; no silent truncation
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tricks'))

from lakatos.engine import run_engine as _core_run_engine, EngineCandidate
from lakatos.schedule import Axis
from novelty_oracle import Candidate as OracleCandidate, classify as _classify
from former import (fit_round_model as _fit_model,
                    make_instance_test as _make_instance_test)


def run_engine(candidates, budget=None, verbose=True):
    """The card-wired engine: the novelty oracle as the rediscovery filter and
    the affine-in-floor round former, plugged into lakatos.engine's loop."""
    return _core_run_engine(candidates, budget=budget, verbose=verbose,
                            classify=_classify, fit=_fit_model,
                            make_instance_test=_make_instance_test)


# ---- unit checks (run at import; lakatos.engine's own units ran on its import) --

def _unit_repair_loop():
    """The refuter must be able to TEACH the former: a family whose fit
    grid only samples rho = 0 fits a law missing the [j < rho] term; an
    off-grid attack kills it; the repair adds the killing config and the
    refit learns the term."""
    def q(N, b, a):
        return [(x // b) + (b if (x % b) < (N % b) else 0)
                for x in range(N)]
    cand = EngineCandidate(
        'unit-repair', 'unit', parametric=dict(
            query=q, fit_grid=[(6, 3), (9, 3), (12, 3), (30, 3)],
            axes=[Axis('N', lo=2), Axis('b', lo=2)],
            valid=lambda N, b: b == 3 and N >= b,
            cost=lambda N, b: N * b, cap=2000,
            claim='unit: slope 1, intercept b*[j<rho]'))
    out = run_engine([cand], verbose=False)
    r = out['rows'][0]
    assert r['disposition'] == 'SURVIVOR' and r['repairs'] >= 1, \
        (r['disposition'], r.get('repairs'), r['detail'])


_unit_repair_loop()


# ---- dry-run generator: fixed mix exercising every path ----------------------

def _round_perm(before, after):
    pos = {c: i for i, c in enumerate(before)}
    return tuple(pos[c] for c in after)


def dry_run_candidates():
    from collections import deque
    from deck_sim import deal_into_piles, gather_position
    import t22_general_b_law as t22
    from refuter_battery import naive_uneven_instance

    cands = []

    # 1. SUPPRESSED path: a fixed-vector targeting trick implemented with
    # adaptive-looking code (the t15 disguise) — library-as-known must bite.
    N27, target = 27, 14
    vec27 = t22.law_vector(target, N27, 3, 3)

    def dressed_rounds(ch):
        d = list(range(N27))
        perms = []
        for a in vec27:
            before = list(d)
            piles = deal_into_piles(d, 3)
            j = next(i for i, p in enumerate(piles) if ch['card'] in p)
            d = gather_position(piles, j, a)
            perms.append(_round_perm(before, d))
        return perms

    cands.append(EngineCandidate(
        'dressed adaptive ACAAN (27)', 'dry-run replay',
        oracle_view=lambda: OracleCandidate(
            'dressed adaptive ACAAN (27)', N27, 'permutation',
            round_perms=dressed_rounds,
            sample_choices=[{'card': c, 'n': target} for c in range(N27)],
            sample_scope='exhaustive')))

    # 2. SUPPRESSED path: out-faro, exhaustive sample
    def out_faro_rounds(ch):
        out = [0] * 52
        for k in range(26):
            out[2 * k], out[2 * k + 1] = k, 26 + k
        return [tuple(out)]

    cands.append(EngineCandidate(
        'out-faro round', 'dry-run replay',
        oracle_view=lambda: OracleCandidate(
            'out-faro round', 52, 'permutation',
            round_perms=out_faro_rounds, sample_choices=[{}],
            sample_scope='exhaustive')))

    # 3. REVIEW path: same faro, PARTIAL sample — the sampling pin abstains
    cands.append(EngineCandidate(
        'out-faro round (partial sample)', 'dry-run replay',
        oracle_view=lambda: OracleCandidate(
            'out-faro round (partial sample)', 52, 'permutation',
            round_perms=out_faro_rounds, sample_choices=[{}],
            sample_scope='partial')))

    # 4. SURVIVOR path: the Mongean shuffle as a parametric family —
    # outside the five families, inside the former's grammar. End to end:
    # oracle clears it, former fits its closed form, refuter escalates.
    def mongean_query(N, b, a):
        out = deque()
        for x in range(N):
            (out.appendleft if x % 2 == 0 else out.append)(x)
        pos = [0] * N
        for p, x in enumerate(out):
            pos[x] = p
        return pos

    cands.append(EngineCandidate(
        'Mongean position law', 'dry-run replay',
        oracle_view=lambda: OracleCandidate(
            'Mongean position law', 52, 'permutation',
            round_perms=lambda ch: [tuple(mongean_query(52, 2, 0))],
            sample_choices=[{}], sample_scope='exhaustive'),
        parametric=dict(
            query=mongean_query,
            fit_grid=[(N, 2) for N in (6, 7, 8, 9, 10, 11, 12, 13, 20, 21)],
            axes=[Axis('N', lo=2), Axis('b', lo=2)],
            valid=lambda N, b: b == 2 and N >= 2,
            cost=lambda N, b: N * b, cap=3000,
            claim='Mongean landing position is affine in floor(x/2) with '
                  'a residue case-split, for every packet size N')))

    # 5. UNSTRUCTURED path: the milk shuffle — also outside the five
    # families, but NOT affine-in-floor (rise-then-fold); former must refuse.
    def milk_query(N, b, a):
        d = list(range(N))
        out = []
        lo, hi = 0, N - 1
        while lo < hi:
            out += [d[lo], d[hi]]
            lo += 1
            hi -= 1
        if lo == hi:
            out.append(d[lo])
        pos = [0] * N
        for p, x in enumerate(out):
            pos[x] = p
        return pos

    cands.append(EngineCandidate(
        'milk-shuffle position law', 'dry-run replay',
        oracle_view=lambda: OracleCandidate(
            'milk-shuffle position law', 52, 'permutation',
            round_perms=lambda ch: [tuple(milk_query(52, 2, 0))],
            sample_choices=[{}], sample_scope='exhaustive'),
        parametric=dict(
            query=milk_query,
            fit_grid=[(N, 2) for N in (8, 9, 10, 11, 12, 13)],
            axes=[Axis('N', lo=2), Axis('b', lo=2)],
            valid=lambda N, b: b == 2 and N >= 2,
            cost=lambda N, b: N * b, cap=3000,
            claim='milk-shuffle landing position is affine in floor(x/2)')))

    # 6. ROUTED path: full reversal — clears the oracle, carries nothing
    # further to test
    cands.append(EngineCandidate(
        'full packet reversal', 'dry-run replay',
        oracle_view=lambda: OracleCandidate(
            'full packet reversal', 52, 'permutation',
            round_perms=lambda ch: [tuple(range(51, -1, -1))],
            sample_choices=[{}], sample_scope='exhaustive')))

    # 7. REFUTED path: the laundering specimen arrives as a ready-made
    # claim; the derived schedule must kill it inside the loop too
    cands.append(EngineCandidate(
        'naive parity law for all N<=b^r', 'dry-run replay',
        conjecture_spec=dict(
            claim='parity digit rule targets any n for every N <= b^r',
            instance=naive_uneven_instance,
            axes=[Axis('b', lo=2), Axis('N', lo=2),
                  Axis('r', lo=1, step='increment')],
            inspiring=[(2, 4, 2), (2, 8, 3), (3, 9, 2), (2, 16, 4),
                       (4, 16, 2), (5, 25, 2), (3, 27, 3)],
            valid=lambda b, N, r: 2 <= b <= N <= b ** r,
            cost=lambda b, N, r: N * N * r, cap=50000)))

    return cands


EXPECTED = {
    'dressed adaptive ACAAN (27)': 'SUPPRESSED',
    'out-faro round': 'SUPPRESSED',
    'out-faro round (partial sample)': 'REVIEW',
    'Mongean position law': 'SURVIVOR',
    'milk-shuffle position law': 'UNSTRUCTURED',
    'full packet reversal': 'ROUTED',
    'naive parity law for all N<=b^r': 'REFUTED',
}


if __name__ == '__main__':
    print('engine.py (card wiring): lakatos.engine units ran on import; '
          'repair-loop unit PASS')
    print('\n================ DRY RUN (doubles as acceptance ledger) '
          '================')
    out = run_engine(dry_run_candidates())

    print('\n---- acceptance ----')
    got = {r['name']: r['disposition'] for r in out['rows']}
    all_ok = True
    for name, want in EXPECTED.items():
        ok = got.get(name) == want
        all_ok &= ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: "
              f"{got.get(name)} (expected {want})")
    fams = set(out['drift']['by_family'])
    drift_ok = (out['drift']['total'] >= 2
                and {'LibraryTargeting', 'Faro'} <= fams
                and out['drift']['needs_review'] == 1)
    all_ok &= drift_ok
    print(f"  {'PASS' if drift_ok else 'FAIL'}  drift metric: "
          f"{out['drift']}")

    surv = next(r for r in out['rows']
                if r['disposition'] == 'SURVIVOR' and r.get('model'))
    print(f"\n  engine's first end-to-end product — machine-fitted law for "
          f"'{surv['name']}':")
    print('    ' + surv['model'].describe().replace('\n', '\n    '))

    print('\n---- budget drill (max_candidates=3) ----')
    out2 = run_engine(dry_run_candidates(),
                      budget=dict(max_candidates=3), verbose=False)
    n_skip = len(out2['skipped'])
    drill_ok = (n_skip == 4
                and all(r['disposition'] == 'SKIPPED (budget)'
                        for r in out2['rows'][3:]))
    all_ok &= drill_ok
    print(f"  {'PASS' if drill_ok else 'FAIL'}  3 processed, {n_skip} "
          f"skipped by name: {', '.join(out2['skipped'])}")

    print(f"\nENGINE DRY-RUN {'PASS' if all_ok else 'FAIL'} "
          f"({out['cases']} cases, {out['elapsed']:.1f}s)")
