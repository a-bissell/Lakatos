"""refuter_battery.py — the whole-library regression ladder (engine item 4).

Conjecture objects are GENERATED from LIBRARY entries: each spec below
names the entry, states its claim as a parametric instance test, and
declares only the parameter SIGNATURE (axes, validity, cost model). The
attack schedule is derived by refuter_auto — no curated lists.

Also runs the LAUNDERING DEMO the README promised: a false conjecture
("the parity digit rule targets any position for EVERY packet size
N <= b^r, uneven piles included") whose inspiring data and a hand-curated
adversary both sample only N = b^r — diverse-looking, secretly blind.
The curated battery stamps it ROBUST; the derived schedule kills it.

Coverage map (library entry -> battery conjecture):
  general-b-radix-law, universal-radix-law (b=3), four-pile-universal-law
  (b=4), alternating-radix-law, fixed-vector-uneven-acaan  -> GENERAL-B
  (t22's corr reproduces the b=3/b=4 tables exactly; inspiring includes
  entry configs from t20/t21)
  radix-placement law (t6)                                 -> PARITY
  any-card-any-packet-size / down-under J(n)               -> JOSEPHUS
  gilbreath-principle / gilbreath-suit-divination          -> GILBREATH
  two-card-agreement-conservation                          -> CONSERVATION
  six-pile-bucket-rule                                     -> BUCKET
Excluded, with reasons: strategy-search entries (t15/t16-B/t17 adaptive &
reactive strategies — their proof scripts are their regression; no free
parameter to escalate), spelling/census constructions (t7/t12: finite
domains already exhaustively enumerated), engine entries (own acceptance
ledgers: oracle_audit, library_known_audit, former_acceptance).

Budget note: this is a REGRESSION battery, deliberately outside the
per-task 8-verify budget; caps below hold the full run to minutes. Where
a cap trims a historically proven envelope (e.g. the parity law's
scale-512 demo in refuter.py __main__), the axis report says so — the
historical envelope stands on its own record.
"""
import os
import sys
import time
from itertools import product
from math import factorial

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tricks'))

from deck_sim import (make_packet, deal_into_piles, gather_position,
                      gather_order, deal_pile, riffle_merge,
                      down_under_survivor, verify)
from refuter import Conjecture, refute, targeting_instance
from refuter_auto import Axis, auto_conjecture
import t22_general_b_law as t22
from t23_six_pile_buckets import bucket_digit, argmin_digit


# ---- instance tests (each: params -> (ok, witness, n_cases)) -----------------

def general_b_instance(b, N, r):
    vec = {n: t22.law_vector(n, N, b, r) for n in range(1, N + 1)}

    def trick(deck, ch):
        d = list(deck)
        for a in vec[ch['n']]:
            piles = deal_into_piles(d, b)
            j = next(i for i, p in enumerate(piles) if ch['card'] in p)
            d = gather_position(piles, j, a)
        return d

    domain = [{'card': c, 'n': n}
              for c in range(N) for n in range(1, N + 1)]
    ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1],
                         deck_factory=lambda: make_packet(N))
    return ok, (counter[0] if counter else None), len(domain)


def reversed_rest_instance(b, N, r):
    import t26_reversed_rest_acaan as t26
    vec = {n: t26.law_vector_rr(n, N, b, r) for n in range(1, N + 1)}

    def trick(deck, ch):
        d = list(deck)
        for c in vec[ch['n']]:
            piles = deal_into_piles(d, b)
            j = next(i for i, p in enumerate(piles) if ch['card'] in p)
            d = t26.gather_rr(piles, j, c)
        return d

    domain = [{'card': c, 'n': n}
              for c in range(N) for n in range(1, N + 1)]
    ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1],
                         deck_factory=lambda: make_packet(N))
    return ok, (counter[0] if counter else None), len(domain)


def parity_instance(b, r):
    return targeting_instance(b, r, parity=True)


def josephus_instance(n):
    for m in range(1, n + 1):
        L = m - (1 << (m.bit_length() - 1))
        want = 2 * L if L else m
        got = down_under_survivor(list(range(1, m + 1)))
        if got != want:
            return False, {'m': m, 'got': got, 'want': want}, m
    return True, None, n


def gilbreath_instance(N, k):
    cases = 0
    for pat in product((0, 1), repeat=N):
        m = pat.count(0)
        pile, rest = deal_pile(list(range(N)), m)
        out = riffle_merge(pile, rest, list(pat))
        cases += 1
        if any({c % k for c in out[i:i + k]} != set(range(k))
               for i in range(0, N, k)):
            return False, {'N': N, 'k': k, 'pattern': pat}, cases
    return True, None, cases


def _digits(x, b, m):
    return tuple((x // b ** i) % b for i in range(m))


def conservation_instance(m, b, rounds):
    N = b ** m
    from itertools import permutations
    G = []
    for order in permutations(range(b)):
        d = gather_order(deal_into_piles(list(range(N)), b), list(order))
        pos = [0] * N
        for newp, x in enumerate(d):
            pos[x] = newp
        G.append(pos)
    cases = 0
    for tx in range(N):
        for ty in range(N):
            if tx == ty:
                continue
            cases += 1
            B = {(tx, ty)}
            for _ in range(rounds):
                B = {(x, y) for x in range(N) for y in range(N) if x != y
                     if any((g[x], g[y]) in B for g in G)}
            tc = sum(u == v for u, v in
                     zip(_digits(tx, b, m), _digits(ty, b, m)))
            for x, y in B:
                if sum(u == v for u, v in
                       zip(_digits(x, b, m), _digits(y, b, m))) != tc:
                    return False, {'target': (tx, ty), 'pair': (x, y),
                                   'm': m, 'b': b, 'rounds': rounds}, cases
    return True, None, cases


def bucket_instance(R):
    for z in range(-R, R + 1):
        if bucket_digit(z) != argmin_digit(z):
            return False, {'z': z, 'bucket': bucket_digit(z),
                           'argmin': argmin_digit(z)}, 2 * R + 1
    return True, None, 2 * R + 1


# ---- the false specimen (laundering demo) ------------------------------------

def _parity_place(n, b, r):
    x = n - 1
    ds = []
    for _ in range(r):
        ds.append(x % b)
        x //= b
    return [d if (r - 1 - i) % 2 == 0 else (b - 1) - d
            for i, d in enumerate(ds)]


def naive_uneven_instance(b, N, r):
    """FALSE claim: the pure parity digit rule targets any n for every
    N <= b^r (uneven piles included). True exactly when N = b^r."""
    cases = 0
    for card in range(N):
        for n in range(1, N + 1):
            cases += 1
            d = make_packet(N)
            for a in _parity_place(n, b, r):
                piles = deal_into_piles(d, b)
                j = next(i for i, p in enumerate(piles) if card in p)
                d = gather_position(piles, j, a)
            if d[n - 1] != card:
                return False, {'b': b, 'N': N, 'r': r, 'card': card,
                               'n': n}, cases
    return True, None, cases


# ---- library conjecture specs ------------------------------------------------

T22_GRID = [(2, 10, 5), (2, 16, 5), (2, 21, 6), (2, 32, 6),
            (5, 12, 3), (5, 15, 3), (5, 18, 3), (5, 21, 3), (5, 24, 3),
            (5, 25, 3), (5, 27, 4), (5, 39, 4), (5, 52, 4),
            (6, 20, 3), (6, 27, 3), (6, 33, 3), (6, 36, 3), (6, 45, 4),
            (6, 52, 4),
            (7, 30, 3), (7, 44, 3), (7, 49, 3), (7, 52, 4),
            (8, 33, 3), (8, 40, 3), (8, 47, 3), (8, 52, 3)]
T20_T21_REPS = [(3, 14, 4), (3, 27, 4), (3, 52, 5),
                (4, 16, 3), (4, 30, 4), (4, 52, 4)]

SPECS = [
    dict(name='general-b radix law  [general-b-radix-law + b=3/b=4 entries]',
         claim='law_vector(n, N, b, r) sends every card to position n '
               'whenever N >= b and b^(r-1) >= N',
         instance=general_b_instance,
         axes=[Axis('b', lo=2), Axis('N', lo=2),
               Axis('r', lo=1, step='increment')],
         inspiring=T22_GRID + T20_T21_REPS,
         valid=lambda b, N, r: N >= b >= 2 and r >= 1
               and b ** (r - 1) >= N,
         cost=lambda b, N, r: N ** 3 * r, cap=int(1.2e8)),
    dict(name='largest-first ACAAN law  [t26, theorem #3]',
         claim='law_vector_rr(n, N, b, r) sends every card to position '
               'n under largest-first pickups whenever N >= b and '
               'b^(r-1) >= N',
         instance=reversed_rest_instance,
         axes=[Axis('b', lo=2), Axis('N', lo=2),
               Axis('r', lo=1, step='increment')],
         inspiring=[(3, 7, 3), (4, 10, 3), (5, 23, 3), (6, 33, 3),
                    (5, 25, 3), (6, 36, 3), (2, 32, 6), (4, 52, 4),
                    (6, 52, 4)],
         valid=lambda b, N, r: N >= b >= 2 and r >= 1
               and b ** (r - 1) >= N,
         cost=lambda b, N, r: N ** 3 * r, cap=int(1.2e8)),
    dict(name='parity radix law  [radix-placement law, t6]',
         claim='base-b digits of n-1, parity-complemented, target any n '
               'in a b^r packet',
         instance=parity_instance,
         axes=[Axis('b', lo=2), Axis('r', lo=1, step='increment')],
         inspiring=[(3, 3), (4, 2)],
         valid=lambda b, r: b >= 2 and r >= 1,
         cost=lambda b, r: (b ** r) ** 3 * r, cap=int(6e7)),
    dict(name='Josephus survivor closed form  [any-card-any-packet-size]',
         claim='down-under survivor of m cards is card 2L (L = m minus '
               'the largest power of 2 <= m), or m when L = 0 — checked '
               'for every m up to the parameter',
         instance=josephus_instance,
         axes=[Axis('n', lo=1)],
         inspiring=[(52,)],
         valid=lambda n: n >= 1,
         cost=lambda n: n * n, cap=int(4.5e7)),
    dict(name='Gilbreath block invariant  [gilbreath-principle]',
         claim='after deal-off (reversal) + ANY riffle, every k-block '
               'holds all k residues (checked over all 2^N interleavings)',
         instance=gilbreath_instance,
         axes=[Axis('N', lo=4), Axis('k', lo=2)],
         inspiring=[(12, 4), (16, 4)],
         valid=lambda N, k: k >= 2 and N >= 2 * k and N % k == 0,
         cost=lambda N, k: (2 ** N) * N, cap=int(2.2e7)),
    dict(name='two-card agreement conservation  '
              '[two-card-agreement-conservation]',
         claim='with even piles (N = b^m), the count of base-b digit '
               'positions where two cards agree is conserved by every '
               'gather strategy (full-information back-reachability)',
         instance=conservation_instance,
         axes=[Axis('m', lo=2, step='increment'), Axis('b', lo=2),
               Axis('rounds', lo=1, step='increment')],
         inspiring=[(3, 3, 3), (3, 3, 4), (3, 3, 5)],
         valid=lambda m, b, rounds: m >= 2 and b >= 2 and rounds >= 1,
         cost=lambda m, b, rounds: rounds * (b ** m) ** 4 * factorial(b),
         cap=int(3e7)),
    dict(name='six-pile bucket == argmin  [six-pile-bucket-rule]',
         claim='the fixed thresholds reproduce the tie-broken argmin '
               'digit for every integer z in [-R, R]',
         instance=bucket_instance,
         axes=[Axis('R', lo=10)],
         inspiring=[(400,)],
         valid=lambda R: R >= 10,
         cost=lambda R: R, cap=int(2e6)),
]


def laundering_demo(verbose=False):
    """The README's promised failure mode, made concrete. Same false
    conjecture, two adversaries."""
    inspiring = [(2, 4, 2), (2, 8, 3), (3, 9, 2), (2, 16, 4), (4, 16, 2),
                 (5, 25, 2), (3, 27, 3)]
    # the curated adversary: MORE bases, MORE rounds — looks diverse,
    # never lets N off the powers. This list is the anti-pattern exhibit.
    curated = [(2, 32, 5), (6, 36, 2), (7, 49, 2), (2, 64, 6)]
    scale = lambda b, N, r: N * N * r
    c_curated = Conjecture(
        name='NAIVE-UNEVEN (curated adversary)',
        claim='parity digit rule targets any n for every N <= b^r',
        instance_test=naive_uneven_instance, scale=scale,
        inspiring=inspiring, beyond=curated,
        param_names=('b', 'N', 'r'))
    res_curated = refute(c_curated, verbose=verbose)

    conj, report = auto_conjecture(
        name='NAIVE-UNEVEN (derived schedule)',
        claim='parity digit rule targets any n for every N <= b^r',
        instance_test=naive_uneven_instance,
        axes=[Axis('b', lo=2), Axis('N', lo=2),
              Axis('r', lo=1, step='increment')],
        inspiring=inspiring,
        valid=lambda b, N, r: 2 <= b <= N <= b ** r,
        cost=scale, cap=50000, scale=scale)
    res_auto = refute(conj, verbose=verbose)
    return res_curated, res_auto, report


if __name__ == '__main__':
    t0 = time.monotonic()
    ledger = []

    print('=== LAUNDERING DEMO (curated adversary vs derived schedule) ===')
    res_c, res_a, _ = laundering_demo()
    launder_ok = (res_c['status'] == 'ROBUST_CONJECTURE'
                  and res_a['status'] == 'REFUTED')
    print(f"  curated:  {res_c['status']} after "
          f"{res_c.get('attacks_survived', 0)} attacks "
          f"({res_c['cases']} cases) — the FALSE robust stamp")
    print(f"  derived:  {res_a['status']} at {res_a.get('killed_at')} "
          f"witness {res_a.get('witness')}")
    print(f"  -> {'PASS' if launder_ok else 'FAIL'}: the derived schedule "
          f"kills what the curated one launders")
    ledger.append(('laundering demo', launder_ok))

    print('\n=== LIBRARY REGRESSION LADDER ===')
    total_cases = 0
    for spec in SPECS:
        t1 = time.monotonic()
        conj, report = auto_conjecture(
            spec['name'], spec['claim'], spec['instance'], spec['axes'],
            spec['inspiring'], spec['valid'], spec['cost'], spec['cap'])
        res = refute(conj, verbose=False)
        dt = time.monotonic() - t1
        total_cases += res['cases']
        ok = res['status'] == 'ROBUST_CONJECTURE'
        # no-silent-caps: every axis escalated or explicitly limited,
        # and at least one axis escalated
        escalated = [a for a, v in report.items() if v.startswith('escalated')]
        sched_ok = len(report) == len(spec['axes']) and escalated
        ledger.append((spec['name'], ok and bool(sched_ok)))
        print(f"\n  {spec['name']}")
        print(f"    status: {res['status']}"
              + (f"  witness: {res.get('witness')}" if not ok else '')
              + f"  ({res.get('attacks_survived', 0)} attacks, "
                f"{res['cases']} cases, {dt:.1f}s)")
        print(f"    envelope: {res.get('envelope')}")
        print(f"    axes: {report}")

    verdict = all(ok for _, ok in ledger)
    print(f"\nBATTERY {'PASS' if verdict else 'FAIL'} "
          f"({sum(ok for _, ok in ledger)}/{len(ledger)} checks, "
          f"{total_cases} cases, {time.monotonic() - t0:.0f}s total)")
    for name, ok in ledger:
        if not ok:
            print(f"  FAILED: {name}")
