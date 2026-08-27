"""former_acceptance.py — acceptance ledger for engine item 3 (conjecture former).

Queue acceptance criterion: "it must re-derive the general-b law from raw
round maps without hints." The ledger, in order:

  0 NO-HINTS GUARD    former.py's source contains no simulator or law
                      vocabulary — the boundary is enforced, not promised.
  1 STRUCTURE FIT     black-box Gergonne round maps -> exact piecewise
                      closed form (the rediscovered pile-size algebra).
  2 REFUTER LADDER    battery auto-derived from the fit grid's signature;
                      the fitted model must reach ROBUST_CONJECTURE.
  3 NEGATIVE CONTROL  a non-affine black box (down-under elimination) must
                      be REFUSED, not approximated.
  4 LAW CROSS-CERT    the fitted model certifies t22's law_vector for every
                      target at every cert config (incl. tight N=52 b=6 r=3).
  5 GROUND TRUTH      model-planned pickup vectors pass verify() on the
                      simulator over the full (card x target) domain.

Every check prints PASS/FAIL; the exit summary is the ledger verdict.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from deck_sim import make_packet, deal_into_piles, gather_position, verify
from former import (fit_round_model, make_instance_test, auto_battery,
                    targeting_vectors)
from refuter import Conjecture, refute


# ---- wiring: the black boxes the former is allowed to query ------------------

def gergonne_query(N, b, a):
    """One Gergonne round as an opaque position map: deal N tokens into b
    piles, spectator points to the pile holding the tracked token, gather
    with a other piles above it. newpos[x] = landing position of start x."""
    out = [None] * N
    for x in range(N):
        piles = deal_into_piles(make_packet(N), b)
        j = next(i for i, p in enumerate(piles) if x in p)
        out[x] = gather_position(piles, j, a).index(x)
    return out


def down_under_query(N, b, a):
    """Negative control: the down-under elimination order (Josephus k=2).
    Its position map is bit-reversal-structured, genuinely outside the
    affine-in-floor grammar. Ignores a; b only shapes the residue lens the
    former will try (and must fail) to impose."""
    order = [None] * N
    q = list(range(N))
    t, down = 0, True
    while q:
        c = q.pop(0)
        if down:
            order[c] = t
            t += 1
        else:
            q.append(c)
        down = not down
    return order


# Diversity principle: every atom the former's grammar mentions must vary
# across the grid, INCLUDING at its floor — q0 spans 1, 2, 3, 5, 7 and every
# rho appears for each b. (The first fit attempt used q0 >= 3 only; the
# refuter battery promptly killed the overfit pocket at N=11 b=6, q0=1.)
FIT_GRID = sorted({(q * b + t, b)
                   for b in range(2, 7) for q in (1, 2, 3) for t in range(b)
                   if q * b + t >= b + 1} |
                  {(5 * b, b) for b in range(2, 7)} |
                  {(5 * b + 1, b) for b in range(2, 7)} |
                  {(7 * b - 1, b) for b in range(2, 7)})

CERT_GRID = [(16, 2, 5), (32, 2, 6), (27, 3, 4), (25, 5, 3),
             (36, 6, 3), (52, 4, 4), (52, 6, 3)]

GROUND_TRUTH_GRID = [(52, 6, 3), (32, 2, 6), (25, 5, 3)]


# ---- ledger checks -----------------------------------------------------------

def check_no_hints():
    src = open(os.path.join(ROOT, 'former.py')).read()
    banned = ('deck_sim', 'gather', 'deal', 'pile', 'corr',
              'gergonne', 'Gergonne', 'law_vector')
    found = [w for w in banned if w in src]
    return not found, found


def check_structure_fit():
    model = fit_round_model(gergonne_query, FIT_GRID)
    return model


def check_refuter_ladder(model):
    battery = auto_battery(FIT_GRID)
    conj = Conjecture(
        name='FORMED  affine-in-floor round law (machine-fitted, no hints)',
        claim='newpos(x) = slope*floor(x/b) + intercept per the fitted '
              'model tree, for every (N, b, a) with N >= b',
        instance_test=make_instance_test(model, gergonne_query),
        scale=lambda N, b: N * b,
        inspiring=list(FIT_GRID),
        boundary=battery['boundary'],
        beyond=battery['beyond'],
        random_draw=battery['random_draw'],
    )
    return refute(conj)


def check_negative_control():
    return fit_round_model(down_under_query, FIT_GRID) is None


def check_law_crosscert(model):
    sys.path.insert(0, os.path.join(ROOT, 'tricks'))
    import t22_general_b_law as t22
    certified = 0
    for N, b, r in CERT_GRID:
        leaves = targeting_vectors(model, N, b, r)
        for n in range(1, N + 1):
            vec = tuple(t22.law_vector(n, N, b, r))
            if leaves.get(vec) != frozenset({n - 1}):
                return False, {'N': N, 'b': b, 'r': r, 'n': n,
                               'law_vec': vec,
                               'model_image': sorted(leaves.get(vec, ()))}, certified
            certified += 1
    return True, None, certified


def run_ground_truth(model, N, b, r):
    """Plan every target's pickup vector FROM THE MODEL ONLY, then let the
    simulator judge over the entire (card x target) domain."""
    leaves = targeting_vectors(model, N, b, r)
    plan = {}
    for n in range(1, N + 1):
        good = sorted(v for v, P in leaves.items() if P == frozenset({n - 1}))
        if not good:
            return (False, [({'n': n}, 'no model vector', None)]), 0
        plan[n] = good[0]

    def trick(deck, choices):
        d = list(deck)
        for a in plan[choices['n']]:
            piles = deal_into_piles(d, b)
            j = next(i for i, p in enumerate(piles) if choices['card'] in p)
            d = gather_position(piles, j, a)
        return d

    domain = [{'card': c, 'n': n}
              for c in range(N) for n in range(1, N + 1)]
    ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1],
                         deck_factory=lambda: make_packet(N))
    return (ok, counter), len(domain)


if __name__ == '__main__':
    ledger = []

    ok, found = check_no_hints()
    ledger.append(('0 no-hints guard', ok))
    print(f"[0] no-hints guard: {'PASS' if ok else 'FAIL ' + str(found)}"
          f" (former.py free of simulator/law vocabulary)")

    model = check_structure_fit()
    ledger.append(('1 structure fit', model is not None))
    if model is None:
        print('[1] structure fit: FAIL — former refused the Gergonne box')
        sys.exit(1)
    print(f"[1] structure fit: PASS — exact closed form from "
          f"{len(FIT_GRID)} black-box configs")
    print('    ' + model.describe().replace('\n', '\n    '))

    res = check_refuter_ladder(model)
    ok = res['status'] == 'ROBUST_CONJECTURE'
    ledger.append(('2 refuter ladder', ok))
    print(f"[2] refuter ladder: {'PASS' if ok else 'FAIL'} — status "
          f"{res['status']}"
          + (f", {res['attacks_survived']} attacks survived, max scale "
             f"{res['max_scale']}" if ok else f", witness {res.get('witness')}"))

    ok = check_negative_control()
    ledger.append(('3 negative control', ok))
    print(f"[3] negative control: {'PASS' if ok else 'FAIL'} — down-under "
          f"elimination {'refused (outside grammar)' if ok else 'WRONGLY FIT'}")

    ok, witness, certified = check_law_crosscert(model)
    ledger.append(('4 law cross-cert', ok))
    print(f"[4] law cross-cert: {'PASS' if ok else 'FAIL ' + str(witness)} — "
          f"{certified} t22 law vectors certified by the fitted model "
          f"across {len(CERT_GRID)} (N, b, r) configs")

    total_cases, all_ok = 0, True
    for N, b, r in GROUND_TRUTH_GRID:
        (ok, counter), cases = run_ground_truth(model, N, b, r)
        total_cases += cases
        all_ok &= ok
        print(f"[5] ground truth N={N} b={b} r={r}: "
              f"{'PASS' if ok else 'FAIL'} over {cases} cases"
              + ('' if ok else f'  e.g. {counter[:2]}'))
    ledger.append(('5 ground truth', all_ok))

    verdict = all(ok for _, ok in ledger)
    print(f"\nACCEPTANCE {'PASS' if verdict else 'FAIL'} "
          f"({sum(ok for _, ok in ledger)}/{len(ledger)}; "
          f"{total_cases} simulator-verified cases) — the former "
          f"{'re-derived the general-b law unaided' if verdict else 'did NOT meet the bar'}")
