"""core/engine.py — the integration loop, domain-agnostic.

    candidates -> novelty oracle -> conjecture former -> refuter

as one runnable, with per-run BUDGETS, the suppressed log as the live DRIFT
metric, and eight dispositions. Extracted from engine.py (engine item 5) per
FRAMEWORK.md step 4: the LOOP is here; the card wiring (which oracle, which
former, the dry-run acceptance ledger) lives in the domain (engine.py).

The domain injects three plugs (keyword-only), so the loop names no
domain function directly:

  classify(oracle_view_result, log) -> verdict
      the rediscovery filter's dispatcher. verdict is a dict with
      'verdict' in {MATCHED, ABSTAIN, NOT_MATCHED} (+ family / reason /
      families_checked). If None, the oracle stage is skipped.
  fit(query, grid) -> model | None
      the conjecture former. model must expose .n_points (int, for case
      accounting); None is an honest refusal (candidate -> UNSTRUCTURED).
  make_instance_test(model, query) -> instance_test
      packages model-vs-black-box comparison into the (ok, witness,
      n_cases) shape the refuter's Conjecture expects.

Dispositions:
  SUPPRESSED / REVIEW / ROUTED    (oracle: matched / abstain / not-matched)
  UNSTRUCTURED                    (former refused: outside its grammar)
  SURVIVOR / REFUTED / DOWNGRADED (refuter: robust / killed / too-timid)
  SKIPPED (budget)                (candidate-atomic; every skip is named)

Budgets are candidate-atomic: checked at candidate entry, so a candidate
either runs its full pipeline or is skipped whole. No silent truncation.
"""
import time

from core.oracle import SuppressedLog
from core.schedule import Axis, auto_conjecture
from core.refuter import refute


class EngineCandidate:
    """One unit of candidate output. Any subset of the three views:
    oracle_view() -> a behavioral object the injected classify matches on;
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


def run_engine(candidates, budget=None, verbose=True, *,
               classify=None, fit=None, make_instance_test=None):
    """Run the pipeline over candidates under a budget. Returns a report:
    {'rows': [...], 'drift': suppressed-log summary, 'cases': int,
     'elapsed': float, 'skipped': [names]}.

    classify / fit / make_instance_test are the domain plugs (see module
    docstring). A candidate whose oracle_view is set but classify is None
    simply skips the oracle stage; a parametric candidate requires fit and
    make_instance_test."""
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
        if cand.oracle_view is not None and classify is not None:
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
                model = fit(p['query'], grid)
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


# ---- unit checks (run at import; conjecture_spec path needs no domain plug) --

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


_unit_engine()


if __name__ == '__main__':
    print('core/engine.py unit checks: PASS (dispositions, budget-atomic '
          'skip; conjecture_spec path, no domain plug needed)')
