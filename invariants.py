"""invariants.py — generator schema v2: INVARIANT SEARCH.

Generator v1 asked one question ("where does a token land after one round
of op X?"). This schema asks a different one, mechanically:

    Is there a QUANTITY of the state, read off a few tracked cards, that
    every op in a family leaves unchanged — or moves in a fixed, simple way?

It knows nothing about any committed invariant. It is handed an op family
(one round = deal into b piles, gather the piles in ANY order) and a small
GRAMMAR of quantities, and it enumerates:

  quantities   per-position base-k digits for several lenses k (fixed
               radices and the op's own radix); per-digit PAIR relations
               (equal / less / difference mod k / sum mod k) aggregated by
               count, tuple, sorted tuple, or sum mod k; position-level
               features (order, gap, residues). Arity one (a single tracked
               card) and arity two (a pair).
  transports   how the quantity is allowed to change per round: fixed, or
               for tuple-valued quantities a cyclic shift left/right or a
               reversal. A claim is (quantity, transport):
                   Q(after r rounds) == transport^r(Q(before)).

A PILOT (two tiny configs, every gather order, every tracked choice) then
drops constants (a quantity with one value is not an invariant of
anything), drops claims that already fail, and collapses claims that are
extensionally the same partition of the pilot domain. What is left is
handed to the engine as ready-made conjecture specs whose instance tests
are built THROUGH the cards Decider — exhaustive over every tracked choice
and every gather-order sequence at each (m, b, rounds) — so the refuter's
schedule escalates every axis and a survivor earns ROBUST_CONJECTURE, not
ROBUST_SAMPLED.

Regime breaking, mechanically: every even-pile survivor also spawns a probe
over ARBITRARY packet sizes N (same claim, hypothesis N = b^m dropped). Its
inspiring points are even configs, so if the hypothesis is load-bearing the
derived schedule's residue probes find the boundary and the refuter records
the witness — the machine locating the edge of its own claim.

The search is deliberately ignorant of what is known. In the oracle-on run
the library-as-known recognizer decides what is a rediscovery; the blind
run (oracle off) is the retrodiction test in invariants_acceptance.py.
"""
import os
import sys
from itertools import permutations, product
from math import factorial

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from deck_sim import deal_into_piles, gather_order, make_packet
from domains.cards import DECIDER, OracleCandidate
from lakatos.schedule import Axis
from lakatos.engine import EngineCandidate, run_engine as _run_engine


# ---- the op family: one round = deal into b piles, gather in order sigma -----

def all_orders(b):
    return list(permutations(range(b)))


def final_deck(N, b, orders):
    """The packet after the rounds in `orders` (each a gather order)."""
    d = make_packet(N)
    for o in orders:
        d = gather_order(deal_into_piles(d, b), list(o))
    return d


def inverse(deck):
    pos = [0] * len(deck)
    for p, x in enumerate(deck):
        pos[x] = p
    return pos


# ---- position features -------------------------------------------------------

def width(N, k):
    w = 1
    while k ** w < N:
        w += 1
    return w


def digits(p, k, w):
    return tuple((p // k ** i) % k for i in range(w))


# ---- the grammar ---------------------------------------------------------------

LENSES = (2, 3, 4, 5, 'radix')      # 'radix' = the op's own pile count

# per-digit pair relations: (u, v, k) -> int
RELATIONS = {
    'equal': lambda u, v, k: int(u == v),
    'less': lambda u, v, k: int(u < v),
    'diff': lambda u, v, k: (u - v) % k,
    'sum': lambda u, v, k: (u + v) % k,
}

# aggregates over a digit-indexed vector: (vec, k) -> hashable
AGGREGATES = {
    'count': lambda vec, k: sum(vec),
    'tuple': lambda vec, k: tuple(vec),
    'sorted': lambda vec, k: tuple(sorted(vec)),
    'sum-mod': lambda vec, k: sum(vec) % k,
}

# transports: how a tuple-valued quantity may move per round
TRANSPORTS = {
    'fixed': lambda v: v,
    'cycle-left': lambda v: v[1:] + v[:1],
    'cycle-right': lambda v: v[-1:] + v[:-1],
    'reverse': lambda v: v[::-1],
}
TUPLE_ONLY = ('cycle-left', 'cycle-right', 'reverse')


class Quantity:
    """A named function of one or two positions. `fn(pos_tuple, ctx)` where
    ctx = dict(N, k, w, D) and D[p] = digits of p in base k, width w."""

    def __init__(self, name, arity, lens, fn, tuple_valued=False):
        self.name, self.arity, self.lens = name, arity, lens
        self.fn, self.tuple_valued = fn, tuple_valued

    def radix(self, b):
        return b if self.lens == 'radix' else self.lens


def quantities():
    qs = []
    for lens in LENSES:
        L = f'lens={lens}'
        # arity 1: the digit vector itself, and its aggregates
        for agg, A in AGGREGATES.items():
            qs.append(Quantity(
                f'card digits {agg} ({L})', 1, lens,
                (lambda A: lambda ps, c: A(c['D'][ps[0]], c['k']))(A),
                tuple_valued=(agg == 'tuple')))
        qs.append(Quantity(f'card position mod k ({L})', 1, lens,
                           lambda ps, c: ps[0] % c['k']))
        qs.append(Quantity(f'card position div k ({L})', 1, lens,
                           lambda ps, c: ps[0] // c['k']))
        # arity 2: per-digit relations, aggregated
        for rel, R in RELATIONS.items():
            for agg, A in AGGREGATES.items():
                qs.append(Quantity(
                    f'pair digit-{rel} {agg} ({L})', 2, lens,
                    (lambda R, A: lambda ps, c: A(
                        [R(u, v, c['k']) for u, v in
                         zip(c['D'][ps[0]], c['D'][ps[1]])], c['k']))(R, A),
                    tuple_valued=(agg == 'tuple')))
        qs.append(Quantity(f'pair position order ({L})', 2, lens,
                           lambda ps, c: int(ps[0] < ps[1])))
        qs.append(Quantity(f'pair position gap ({L})', 2, lens,
                           lambda ps, c: abs(ps[0] - ps[1])))
        qs.append(Quantity(f'pair position diff mod k ({L})', 2, lens,
                           lambda ps, c: (ps[0] - ps[1]) % c['k']))
        qs.append(Quantity(f'pair position sum mod k ({L})', 2, lens,
                           lambda ps, c: (ps[0] + ps[1]) % c['k']))
    return qs


def claims():
    """Every (quantity, transport) the grammar can state."""
    out = []
    for q in quantities():
        out.append((q, 'fixed'))
        if q.tuple_valued:
            out.extend((q, t) for t in TUPLE_ONLY)
    return out


# ---- evaluation ----------------------------------------------------------------

def context(N, b, q):
    k = q.radix(b)
    w = width(N, k)
    return dict(N=N, k=k, w=w, D=[digits(p, k, w) for p in range(N)])


def tracked(N, arity):
    if arity == 1:
        return [(p,) for p in range(N)]
    return [(p, q) for p in range(N) for q in range(N) if p != q]


def transport_pow(name, r):
    T = TRANSPORTS[name]

    def Tr(v):
        for _ in range(r):
            v = T(v)
        return v
    return Tr


def claim_holds(q, tname, N, b, orders_list, r=1):
    """Exhaustive: every tracked choice x every gather-order sequence.
    Returns (ok, witness, n_cases, values_seen)."""
    c = context(N, b, q)
    Tr = transport_pow(tname, r)
    seen, cases = set(), 0
    for orders in product(orders_list, repeat=r):
        inv = inverse(final_deck(N, b, orders))
        for ps in tracked(N, q.arity):
            cases += 1
            before = q.fn(ps, c)
            seen.add(before)
            after = q.fn(tuple(inv[p] for p in ps), c)
            if after != Tr(before):
                return False, dict(orders=orders, tracked=ps, before=before,
                                   after=after, expected=Tr(before)), cases, seen
    return True, None, cases, seen


# ---- the pilot: drop constants, drop failures, dedupe extensionally -------------

PILOT = [(2, 3), (3, 2)]            # (m, b): N = 9 with 6 orders; N = 8 with 2


def _partition_key(q, N, b):
    c = context(N, b, q)
    vals = [q.fn(ps, c) for ps in tracked(N, q.arity)]
    ids, key = {}, []
    for v in vals:
        key.append(ids.setdefault(v, len(ids)))
    return tuple(key)


def _values(q, N, b):
    c = context(N, b, q)
    return [q.fn(ps, c) for ps in tracked(N, q.arity)]


def _implied(weak, strong):
    """Is claim `weak` = (q, t) a consequence of `strong` on the pilot?
    True iff on every pilot domain the weak quantity is a function f of the
    strong one AND the transports commute through f: T_w(f(v)) == f(T_s(v))
    for every observed value v. Pure partition logic — no domain content."""
    (qw, tw), (qs, ts) = weak, strong
    if qw.arity != qs.arity:
        return False
    Tw, Ts = TRANSPORTS[tw], TRANSPORTS[ts]
    for m, b in PILOT:
        N = b ** m
        vw, vs = _values(qw, N, b), _values(qs, N, b)
        f = {}
        for a, w_ in zip(vs, vw):
            if f.setdefault(a, w_) != w_:
                return False
        for a, w_ in f.items():
            ta = Ts(a) if isinstance(a, tuple) else a
            if ta not in f:
                return False
            tw_ = Tw(w_) if isinstance(w_, tuple) else w_
            if tw_ != f[ta]:
                return False
    return True


def pilot(verbose=False):
    """Returns (kept, report). kept: list of (quantity, transport) that
    survive: non-constant, hold on every pilot config, extensionally
    distinct, and not implied by a stronger survivor. report also lists
    the implied ones as (weak, strong) name pairs — corollaries the search
    derived on the way."""
    kept, seen = [], {}
    n_const = n_fail = n_dup = 0
    for q, t in claims():
        # constancy over the WHOLE pilot domain (independent of holding)
        if all(len(set(_values(q, b ** m, b))) == 1 for m, b in PILOT):
            n_const += 1
            continue
        if not all(claim_holds(q, t, b ** m, b, all_orders(b))[0]
                   for m, b in PILOT):
            n_fail += 1
            continue
        key = (t, tuple(_partition_key(q, b ** m, b) for m, b in PILOT))
        if key in seen:
            n_dup += 1
            if verbose:
                print(f'    dup: {q.name} | {t}  ==  {seen[key]}')
            continue
        seen[key] = f'{q.name} | {t}'
        kept.append((q, t))
    # implication: drop a survivor that is a function of another survivor
    # (with commuting transport) — it is a corollary, not a new claim
    implied = []
    strongest = []
    for cand in kept:
        by = next((s for s in kept if s is not cand and _implied(cand, s)
                   and not _implied(s, cand)), None)
        if by is not None:
            implied.append((f'{cand[0].name} | {cand[1]}',
                            f'{by[0].name} | {by[1]}'))
            if verbose:
                print(f'    implied: {implied[-1][0]}  <=  {implied[-1][1]}')
        else:
            strongest.append(cand)
    report = dict(enumerated=len(claims()), constant=n_const, failed=n_fail,
                  duplicate=n_dup, implied=implied, kept=len(strongest))
    return strongest, report


# ---- conjecture specs: instance tests THROUGH the Decider ----------------------

def _spec_family(q, tname, even):
    """even=True: axes (m, b, rounds), N = b^m. even=False: the regime-break
    probe, axes (N, b, rounds), any N >= b — the hypothesis dropped."""

    def claim_of(*params):
        if even:
            m, b, r = params
            N = b ** m
        else:
            N, b, r = params
        c = context(N, b, q)
        Tr = transport_pow(tname, r)
        cache = {}

        def trick(deck, ch):
            # the final packet depends only on the gather orders, so each
            # order sequence is simulated once and reused across the
            # tracked choices that ride it (the harness still evaluates
            # every choice)
            orders = ch[0]
            if orders not in cache:
                d = list(deck)
                for o in orders:
                    d = gather_order(deal_into_piles(d, b), list(o))
                cache[orders] = (d, inverse(d))
            return cache[orders][0]

        def predicate(final, ch):
            inv = cache[ch[0]][1]
            ps = ch[1]
            return q.fn(tuple(inv[p] for p in ps), c) == Tr(q.fn(ps, c))
        return ('prop', trick, predicate)

    def domain_of(*params):
        if even:
            m, b, r = params
            N = b ** m
        else:
            N, b, r = params
        return [(orders, ps)
                for orders in product(all_orders(b), repeat=r)
                for ps in tracked(N, q.arity)]

    def packet_of(*params):
        N = params[1] ** params[0] if even else params[0]
        return lambda: make_packet(N)

    return DECIDER.instance_test(claim_of, domain_of, packet_of)


CAP = 600_000        # cases per attack (pairs x order sequences)


def candidates(kept, oracle_ref=(3, 3)):
    """EngineCandidates for the pilot survivors: an even-pile conjecture
    each, plus a regime-break probe each. oracle_ref = (m, b) of the
    reference config the oracle view samples exhaustively."""
    cands = []
    m_ref, b_ref = oracle_ref
    for q, t in kept:
        label = f'{q.name} | {t}'
        n_ref = b_ref ** m_ref
        c_ref = context(n_ref, b_ref, q)
        cands.append(EngineCandidate(
            f'{label}  [N = b^m]',
            'generator v2, schema invariant-search, family deal-and-gather '
            '(any order), even piles',
            oracle_view=(lambda q, t, c_ref, n_ref, b_ref: lambda:
                         OracleCandidate(
                             f'{q.name} | {t}', n_ref, 'invariant',
                             quantity=lambda ps: q.fn(ps, c_ref),
                             arity=q.arity, transport=t, radix=b_ref,
                             sample_scope='exhaustive'))(q, t, c_ref, n_ref,
                                                         b_ref),
            conjecture_spec=dict(
                claim=f'{label}: for N = b^m, every gather-order sequence '
                      f'of r rounds sends the quantity to transport^r of '
                      f'itself, for every tracked choice',
                instance=_spec_family(q, t, even=True),
                axes=[Axis('m', lo=1, step='increment'), Axis('b', lo=2),
                      Axis('rounds', lo=1, step='increment')],
                inspiring=[(m, b, 1) for m, b in PILOT],
                valid=lambda m, b, r: m >= 1 and b >= 2 and r >= 1,
                cost=(lambda ar: lambda m, b, r:
                      factorial(b) ** r * b ** (ar * m))(q.arity),
                cap=CAP)))
        cands.append(EngineCandidate(
            f'{label}  [any N]',
            'generator v2, schema invariant-search, regime-break probe: '
            'same claim with the N = b^m hypothesis dropped',
            conjecture_spec=dict(
                claim=f'{label}: for EVERY packet size N >= b (hypothesis '
                      f'N = b^m dropped), every gather-order sequence sends '
                      f'the quantity to transport^r of itself',
                instance=_spec_family(q, t, even=False),
                axes=[Axis('N', lo=2), Axis('b', lo=2),
                      Axis('rounds', lo=1, step='increment')],
                inspiring=[(b ** m, b, 1) for m, b in PILOT],
                valid=lambda N, b, r: N >= b >= 2 and r >= 1,
                cost=(lambda ar: lambda N, b, r:
                      factorial(b) ** r * N ** ar)(q.arity),
                cap=CAP)))
    return cands


BUDGET = dict(max_candidates=60, max_cases=30_000_000, max_seconds=900.0)


def search(blind=True, verbose=True, budget=None):
    """Run the schema through the engine. blind=True: no oracle stage (the
    retrodiction setting). blind=False: the card oracle decides what is
    library-known. Returns (report, pilot_report, kept)."""
    kept, prep = pilot()
    cands = candidates(kept)
    if blind:
        out = _run_engine(cands, budget=budget or BUDGET, verbose=verbose)
    else:
        from engine import run_engine
        out = run_engine(cands, budget=budget or BUDGET, verbose=verbose)
    return out, prep, kept


# ---- unit checks (run at import) -----------------------------------------------

def _unit_grammar():
    qs = quantities()
    assert len({q.name for q in qs}) == len(qs)
    assert digits(11, 3, 3) == (2, 0, 1) and width(9, 3) == 2 and width(10, 3) == 3
    # transports are bijections on tuples and cycle-left/right are inverse
    v = (1, 2, 3, 4)
    assert TRANSPORTS['cycle-left'](TRANSPORTS['cycle-right'](v)) == v
    assert TRANSPORTS['reverse'](TRANSPORTS['reverse'](v)) == v
    # a constant quantity is recognised as such on the pilot
    const = Quantity('unit const', 2, 2, lambda ps, c: 0)
    _, _, _, vals = claim_holds(const, 'fixed', 9, 3, all_orders(3))
    assert vals == {0}
    # the decider-built instance test is exhaustive by construction and
    # matches claim_holds on a tiny config
    q = next(x for x in qs if x.name == 'pair digit-equal count (lens=radix)')
    t = _spec_family(q, 'fixed', even=True)
    assert getattr(t, 'scope') == 'exhaustive'
    ok, w, n = t(2, 2, 1)                      # N = 4, both orders, 12 pairs
    ok2, w2, n2, _ = claim_holds(q, 'fixed', 4, 2, all_orders(2))
    assert ok and ok2 and n == n2 == 24, ((ok, n), (ok2, n2))
    # and a failing claim is failing on both, with a witness
    q = next(x for x in qs if x.name == 'pair position order (lens=2)')
    ok, w, n = _spec_family(q, 'fixed', even=True)(1, 2, 1)
    assert not ok and w is not None
    assert not claim_holds(q, 'fixed', 2, 2, all_orders(2))[0]


_unit_grammar()


if __name__ == '__main__':
    print('invariants.py unit checks: PASS (grammar well-formed, transports, '
          'constant detection, decider-built test == exhaustive evaluator)')
    kept, prep = pilot(verbose=True)
    print(f'\npilot: {prep}')
    for q, t in kept:
        print(f'  kept: {q.name} | {t}')
