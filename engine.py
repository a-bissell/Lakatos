"""engine.py — the integration loop (engine item 5).

    generator -> novelty oracle -> conjecture former -> refuter

as one runnable, with per-run BUDGETS, the suppressed log as the live
DRIFT metric, and a dry-run mode that doubles as the acceptance ledger.

The generator slot is an interface — item 6 supplies the real one. Until
then the dry-run replays a fixed candidate mix that exercises every
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

Budgets are candidate-atomic: they are checked at candidate entry, so a
candidate either runs its full pipeline or is skipped whole.
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tricks'))

from novelty_oracle import Candidate as OracleCandidate, SuppressedLog, classify
from former import fit_round_model, make_instance_test
from refuter import refute
from core.schedule import Axis, auto_conjecture


class EngineCandidate:
    """One unit of generator output. Any subset of the three views:
    oracle_view() -> novelty_oracle.Candidate (behavioral, for matching);
    parametric = dict(query, fit_grid, axes, valid, cost, cap, claim) for
    the former; conjecture_spec = dict(instance, axes, inspiring, valid,
    cost, cap, claim) for candidates that arrive as ready-made claims."""

    def __init__(self, name, provenance, oracle_view=None, parametric=None,
                 conjecture_spec=None):
        self.name = name
        self.provenance = provenance
        self.oracle_view = oracle_view
        self.parametric = parametric
        self.conjecture_spec = conjecture_spec


DEFAULT_BUDGET = dict(max_candidates=50, max_cases=5_000_000,
                      max_seconds=600.0)


def run_engine(candidates, budget=None, verbose=True):
    """Run the pipeline over candidates under a budget. Returns a report:
    {'rows': [...], 'drift': suppressed-log summary, 'cases': int,
     'elapsed': float, 'skipped': [names]}."""
    budget = dict(DEFAULT_BUDGET, **(budget or {}))
    log = SuppressedLog()
    rows, skipped = [], []
    cases_used, processed = 0, 0
    t0 = time.monotonic()

    def say(s):
        if verbose:
            print(s)

    for cand in candidates:
        elapsed = time.monotonic() - t0
        if (processed >= budget['max_candidates']
                or cases_used >= budget['max_cases']
                or elapsed >= budget['max_seconds']):
            skipped.append(cand.name)
            rows.append(dict(name=cand.name, disposition='SKIPPED (budget)',
                             detail=f'at candidate {processed + 1}: '
                                    f'{cases_used} cases, {elapsed:.1f}s'))
            continue
        processed += 1
        say(f'\n[{processed}] {cand.name}  (from: {cand.provenance})')
        review_note, oracle_verdict = None, None

        # ---- stage 1: novelty oracle (log-and-suppress) ----------------
        if cand.oracle_view is not None:
            v = classify(cand.oracle_view(), log)
            oracle_verdict = v['verdict']
            if v['verdict'] == 'MATCHED':
                say(f"    oracle: MATCHED {v['family']} -> suppressed "
                    f"(witness logged)")
                rows.append(dict(name=cand.name, disposition='SUPPRESSED',
                                 oracle='MATCHED',
                                 detail=f"{v['family']}: {v['witness']}"))
                continue
            if v['verdict'] == 'ABSTAIN':
                review_note = v['reason']
                say(f"    oracle: ABSTAIN ({review_note}) -> surfaced, "
                    f"routed onward")
            else:
                say(f"    oracle: NOT_MATCHED "
                    f"({v.get('families_checked')} families) -> routed on")

        # ---- stages 2+3: former <-> refuter (with bounded repair) ------
        # A parametric candidate whose conjecture is REFUTED gets the
        # killing config ADDED to its fit grid and is refit — the refuter
        # teaching the former — at most MAX_REPAIRS times. Direct
        # conjectures have nothing to refit and die where they die.
        MAX_REPAIRS = 2
        conj, report, model, res, repairs = None, None, None, None, 0
        if cand.parametric is not None:
            p = cand.parametric
            grid = list(p['fit_grid'])
            while True:
                model = fit_round_model(p['query'], grid)
                if model is None:
                    break
                conj, report = auto_conjecture(
                    cand.name, p['claim'],
                    make_instance_test(model, p['query']),
                    p['axes'], grid, p['valid'], p['cost'], p['cap'])
                res = refute(conj, verbose=False)
                cases_used += model.n_points + res['cases']
                if (res['status'] in ('REFUTED', 'NOT_A_CANDIDATE')
                        and repairs < MAX_REPAIRS):
                    repairs += 1
                    grid.append(tuple(res['killed_at']))
                    say(f"    repair {repairs}: refuted at "
                        f"{res['killed_at']} — adding it to the fit grid "
                        f"and refitting")
                    continue
                break
            if model is None:
                say('    former: REFUSED (outside grammar) -> backlog')
                rows.append(dict(name=cand.name, disposition='UNSTRUCTURED',
                                 oracle=oracle_verdict,
                                 detail='former refused: not affine-in-floor '
                                        'over the declared grid'
                                        + (f' (after {repairs} repairs)'
                                           if repairs else '')
                                        + (f'; review: {review_note}'
                                           if review_note else '')))
                continue
            say(f'    former: fit ({model.n_points} cells'
                + (f', {repairs} repairs' if repairs else '') + ')')
        elif cand.conjecture_spec is not None:
            s = cand.conjecture_spec
            conj, report = auto_conjecture(
                cand.name, s['claim'], s['instance'], s['axes'],
                s['inspiring'], s['valid'], s['cost'], s['cap'])
            res = refute(conj, verbose=False)
            cases_used += res['cases']

        if res is not None:
            st = res['status']
            repair_note = f' (after {repairs} repairs)' if repairs else ''
            n_att = res.get('attacks_survived',
                            res.get('attacks_before_kill', 0))
            say(f"    refuter: {st} ({n_att} attacks, {res['cases']} cases)"
                f"  axes: {report}")
            if st == 'ROBUST_CONJECTURE':
                rows.append(dict(
                    name=cand.name, disposition='SURVIVOR', model=model,
                    oracle=oracle_verdict, repairs=repairs,
                    detail=f"ROBUST_CONJECTURE, envelope {res['envelope']}"
                           f"{repair_note}; provenance log required "
                           f"(PROVENANCE.md)"))
            elif st in ('REFUTED', 'NOT_A_CANDIDATE'):
                rows.append(dict(
                    name=cand.name, disposition='REFUTED',
                    oracle=oracle_verdict, repairs=repairs,
                    detail=f"killed at {res.get('killed_at')}, witness "
                           f"{res.get('witness')}{repair_note}"))
            else:
                rows.append(dict(
                    name=cand.name, disposition='DOWNGRADED',
                    oracle=oracle_verdict,
                    detail=f'{st}: schedule could not attack beyond '
                           f'inspiring scale; axes: {report}'))
            continue

        # ---- nothing left to test: route or surface --------------------
        if review_note:
            rows.append(dict(name=cand.name, disposition='REVIEW',
                             oracle=oracle_verdict, detail=review_note))
        else:
            rows.append(dict(name=cand.name, disposition='ROUTED',
                             oracle=oracle_verdict,
                             detail='not matched, no parametric content — '
                                    'study backlog'))

    drift = log.summary()
    elapsed = time.monotonic() - t0
    if verbose:
        print('\n---- run report ----')
        for r in rows:
            print(f"  {r['name']:<38} {r['disposition']:<18} {r['detail']}")
        n_sup = sum(r['disposition'] == 'SUPPRESSED' for r in rows)
        print(f"  drift: {n_sup}/{processed} suppressed as known "
              f"{dict(drift['by_family'])}; review queue "
              f"{drift['needs_review']}")
        print(f"  budget: {processed} candidates, {cases_used} cases, "
              f"{elapsed:.1f}s "
              f"(caps {budget['max_candidates']}/{budget['max_cases']}/"
              f"{budget['max_seconds']:.0f}s)")
        if skipped:
            print(f"  skipped on budget ({len(skipped)}): "
                  f"{', '.join(skipped)}")
    return dict(rows=rows, drift=drift, cases=cases_used, elapsed=elapsed,
                skipped=skipped)


# ---- unit checks (run at import, per project convention) ---------------------

def _unit_engine():
    good = EngineCandidate(
        'unit-good', 'unit', conjecture_spec=dict(
            claim='always true', instance=lambda n: (True, None, 1),
            axes=[Axis('n', lo=1)], inspiring=[(4,)],
            valid=lambda n: n >= 1, cost=lambda n: n, cap=64))
    bad = EngineCandidate(
        'unit-bad', 'unit', conjecture_spec=dict(
            claim='fails past 5', instance=lambda n:
                (n <= 5, None if n <= 5 else {'n': n}, 1),
            axes=[Axis('n', lo=1)], inspiring=[(4,)],
            valid=lambda n: n >= 1, cost=lambda n: n, cap=64))
    out = run_engine([good, bad], verbose=False)
    d = {r['name']: r['disposition'] for r in out['rows']}
    assert d == {'unit-good': 'SURVIVOR', 'unit-bad': 'REFUTED'}, d
    # budget: candidate-atomic skip, named in the report
    out = run_engine([good, bad], budget=dict(max_candidates=1),
                     verbose=False)
    d = {r['name']: r['disposition'] for r in out['rows']}
    assert d['unit-good'] == 'SURVIVOR'
    assert d['unit-bad'] == 'SKIPPED (budget)' and out['skipped'] == ['unit-bad']


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


_unit_engine()
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
    print('engine.py unit checks: PASS (dispositions, budget-atomic skip)')
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
