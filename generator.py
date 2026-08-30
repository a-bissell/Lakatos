"""generator.py — generator v1 (engine item 6): question schemas over the
EXISTING op vocabulary. No new primitives.

v1 asks one question family well — the ROUND-POSITION-LAW question:
"where does a tracked token land after one round of [op], as a function
of its start position?" — instantiated over compositions of existing
deck_sim ops: pointed and fixed pickups after a deal, cut-then-deal,
perfect interleaves, the down-under elimination. Each instance is a full
EngineCandidate: an oracle view (behavior at a reference packet,
exhaustively sampled) AND a parametric former view (black-box query, a
diversity fit grid built mechanically from b, and a refuter signature).

Two deliberate stances:
  * The generator is IGNORANT of what is known. Every instance carries
    both views; the oracle decides what gets suppressed. A generator
    that pre-filters "obviously known" material re-introduces the
    author's blind spots upstream of the guardrails.
  * Dedup is EXTENSIONAL: instances whose behavior maps agree at the
    reference configs collapse to one candidate, whatever their
    descriptions say (e.g. for b=2, "cyclic pickup" and "reversed-rest
    pickup" are the same family and one is dropped).

Success metric (tasks.md item 6): the suppressed log shows exploration —
knowns suppressed across multiple families, but not everything known —
and at least one oracle-NOT_MATCHED survivor reaches ROBUST_CONJECTURE.
Running this file executes the metric as an acceptance ledger.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from deck_sim import cut, deal_into_piles, gather_position, gather_order
from novelty_oracle import Candidate as OracleCandidate
from lakatos.schedule import Axis
from engine import EngineCandidate, run_engine


# ---- op instantiations: query(N, b, a) -> landing-position map ---------------

def _invert(deck):
    pos = [0] * len(deck)
    for p, x in enumerate(deck):
        pos[x] = p
    return pos


def q_pointed(N, b, a):
    """Deal into b piles; spectator points to the tracked token's pile;
    gather with a other piles above it (the classic pointed pickup)."""
    out = [0] * N
    for x in range(N):
        piles = deal_into_piles(list(range(N)), b)
        j = next(i for i, p in enumerate(piles) if x in p)
        out[x] = gather_position(piles, j, a).index(x)
    return out


def q_cyclic(N, b, a):
    """Deal into b piles; pick up in cyclic order starting at pile a."""
    order = [(a + i) % b for i in range(b)]
    return _invert(gather_order(deal_into_piles(list(range(N)), b), order))


def q_reversed_rest(N, b, a):
    """Deal into b piles; pile a on top, the rest right-to-left."""
    order = [a] + [k for k in range(b - 1, -1, -1) if k != a]
    return _invert(gather_order(deal_into_piles(list(range(N)), b), order))


def q_cut_pointed(N, b, a):
    """Cut a cards first, then deal into b piles and put the pointed
    pile on top."""
    out = [0] * N
    for x in range(N):
        piles = deal_into_piles(cut(list(range(N)), a), b)
        j = next(i for i, p in enumerate(piles) if x in p)
        out[x] = gather_position(piles, j, 0).index(x)
    return out


def q_interleave(N, b, a):
    """Perfect interleave of the two halves; a=0 leads with the top
    half (out), a=1 with the bottom half (in)."""
    h = (N + 1) // 2
    first, second = list(range(h)), list(range(h, N))
    out = []
    take_first = (a == 0)
    while first or second:
        src = first if (take_first and first) or not second else second
        out.append(src.pop(0))
        take_first = not take_first
    return _invert(out)


def q_elimination(N, b, a):
    """Down-under elimination order: out[x] = when position x hits the
    table (survivor last). The a and b parameters are inert."""
    order = [0] * N
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


# ---- candidate assembly ------------------------------------------------------

def _fit_grid(b0):
    """Diversity grid (item-3 rule, densified): with b FIXED per
    candidate the grid must carry the cross-constraints that a varying b
    provided in item 3, so q0 spans 1..5, 7, 9, 13 and every rho appears
    at two different q0 — otherwise an exact-on-grid tree can alias off
    the grid (the refuter caught exactly that on the first run)."""
    return sorted({(b0, b0), (b0 + 1, b0), (2 * b0 + 1, b0)} |
                  {(3 * b0 + t, b0) for t in range(b0)} |
                  {(4 * b0 + t, b0) for t in range(b0)} |
                  {(5 * b0, b0), (5 * b0 + 1, b0), (7 * b0 - 1, b0),
                   (9 * b0 + 1, b0), (13 * b0 + 2, b0)})


def _oracle_indep(name, query, b0, n_ref):
    def rounds(ch):
        return [tuple(_invert(query(n_ref, b0, ch['a'])))]
    return OracleCandidate(name, n_ref, 'permutation', round_perms=rounds,
                           sample_choices=[{'a': a} for a in range(b0)],
                           sample_scope='exhaustive')


SCHEMA = [
    # (op name, query, bs, card_dependent)
    ('pointed pickup', q_pointed, (3, 4), True),
    ('cyclic pickup', q_cyclic, (2, 3), False),
    ('reversed-rest pickup', q_reversed_rest, (2, 3, 4), False),
    ('cut then pointed pickup', q_cut_pointed, (3,), True),
    ('perfect interleave', q_interleave, (2,), False),
    ('down-under elimination order', q_elimination, (2,), False),
]


def generate():
    """Instantiate the schema, dedupe extensionally, emit EngineCandidates.
    Returns (candidates, dropped) where dropped lists (name, kept_name)."""
    seen, cands, dropped = {}, [], []
    for op_name, query, bs, card_dep in SCHEMA:
        for b0 in bs:
            name = f'{op_name} (b={b0})'
            key = tuple(tuple(query(N, b0, a))
                        for N in (4 * b0, 4 * b0 + 3)
                        for a in range(b0))
            if key in seen:
                dropped.append((name, seen[key]))
                continue
            seen[key] = name
            n_ref = max(12, 2 * b0)
            if card_dep:
                oracle = (lambda nm, q, b, nr: lambda: _oracle_card_dep(
                    nm, q, b, nr))(name, query, b0, n_ref)
                cost = lambda N, b: N * N * b
                cap = int(1e6)
            else:
                oracle = (lambda nm, q, b, nr: lambda: _oracle_indep(
                    nm, q, b, nr))(name, query, b0, n_ref)
                cost = lambda N, b: N * b
                cap = 20000
            cands.append(EngineCandidate(
                name, f'generator v1, schema round-position-law, '
                      f'op {op_name}, b={b0}',
                oracle_view=oracle,
                parametric=dict(
                    query=query, fit_grid=_fit_grid(b0),
                    # N >= b: the no-empty-piles scope. The first draft
                    # claimed every N; the refuter's floor probe promptly
                    # produced a counterexample at N=2, b=3 (an empty
                    # pile changes the map), so the family is scoped to
                    # its real regime — a boundary the machine found.
                    axes=[Axis('N', lo=2), Axis('b', lo=2)],
                    valid=(lambda b0: lambda N, b: b == b0 and N >= b)(b0),
                    cost=cost, cap=cap,
                    claim=f'landing position under "{op_name}" (b={b0}) is '
                          f'affine in floor(x/{b0}) with residue case-splits, '
                          f'for every packet size N >= b')))
    return cands, dropped


def _oracle_card_dep(name, query, b0, n_ref):
    """Card-dependent op: one deck-after permutation per (card, pickup)."""
    def rounds(ch):
        # rebuild the actual round for this card: the query's tracked-card
        # map cannot give the full permutation, so re-run the op
        if query is q_pointed:
            piles = deal_into_piles(list(range(n_ref)), b0)
            j = next(i for i, p in enumerate(piles) if ch['card'] in p)
            return [tuple(gather_position(piles, j, ch['a']))]
        piles = deal_into_piles(cut(list(range(n_ref)), ch['a']), b0)
        j = next(i for i, p in enumerate(piles) if ch['card'] in p)
        return [tuple(gather_position(piles, j, 0))]
    return OracleCandidate(name, n_ref, 'permutation', round_perms=rounds,
                           sample_choices=[{'card': c, 'a': a}
                                           for c in range(n_ref)
                                           for a in range(b0)],
                           sample_scope='exhaustive')


# ---- unit checks (run at import, per project convention) ---------------------

def _unit_queries_well_formed():
    for op_name, query, bs, card_dep in SCHEMA:
        for b0 in bs:
            for N in (7, 12):
                for a in range(b0):
                    m = query(N, b0, a)
                    if card_dep:
                        # tracked-card map spans a different round per
                        # card — total and in-range, not a permutation
                        assert len(m) == N and all(0 <= v < N for v in m), \
                            (op_name, b0, N, a)
                    else:
                        assert sorted(m) == list(range(N)), \
                            (op_name, b0, N, a)


def _unit_dedup():
    cands, dropped = generate()
    names = [c.name for c in cands]
    assert len(names) == len(set(names))
    # b=2 cyclic and reversed-rest are extensionally identical: one drops
    assert ('reversed-rest pickup (b=2)', 'cyclic pickup (b=2)') in dropped
    assert 'reversed-rest pickup (b=2)' not in names
    # determinism
    cands2, dropped2 = generate()
    assert [c.name for c in cands2] == names and dropped2 == dropped


_unit_queries_well_formed()
_unit_dedup()


EXPECTED = {
    'pointed pickup (b=3)': 'SUPPRESSED',
    'pointed pickup (b=4)': 'SUPPRESSED',
    'cyclic pickup (b=2)': 'SUPPRESSED',
    'cyclic pickup (b=3)': 'SUPPRESSED',
    'reversed-rest pickup (b=3)': 'SURVIVOR',
    'reversed-rest pickup (b=4)': 'SURVIVOR',
    'cut then pointed pickup (b=3)': 'UNSTRUCTURED',
    'perfect interleave (b=2)': 'SUPPRESSED',
    'down-under elimination order (b=2)': 'SUPPRESSED',
}


if __name__ == '__main__':
    print('generator.py unit checks: PASS (well-formed queries, '
          'extensional dedup, determinism)')
    cands, dropped = generate()
    print(f'\ngenerated {len(cands)} candidates '
          f'({len(dropped)} deduped: '
          + ', '.join(f'{d} == {k}' for d, k in dropped) + ')')

    print('\n========== GENERATOR v1 -> ENGINE ==========')
    out = run_engine(cands)

    print('\n---- item 6 success metric ----')
    got = {r['name']: r['disposition'] for r in out['rows']}
    all_ok = True
    for name, want in EXPECTED.items():
        ok = got.get(name) == want
        all_ok &= ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {got.get(name)} "
              f"(expected {want})")

    drift = out['drift']
    explore_ok = (drift['total'] >= 4 and len(drift['by_family']) >= 3
                  and any(r['disposition'] != 'SUPPRESSED'
                          for r in out['rows']))
    all_ok &= explore_ok
    print(f"  {'PASS' if explore_ok else 'FAIL'}  exploration: "
          f"{drift['total']} suppressed across "
          f"{len(drift['by_family'])} families "
          f"{dict(drift['by_family'])}, and not everything was known")

    survivors = [r for r in out['rows']
                 if r['disposition'] == 'SURVIVOR'
                 and r.get('oracle') == 'NOT_MATCHED']
    metric_ok = len(survivors) >= 1
    all_ok &= metric_ok
    print(f"  {'PASS' if metric_ok else 'FAIL'}  NOT_MATCHED survivor at "
          f"ROBUST_CONJECTURE: {len(survivors)} "
          f"({', '.join(r['name'] for r in survivors)})")

    for r in survivors:
        print(f"\n  machine-fitted law for '{r['name']}':")
        print('    ' + r['model'].describe().replace('\n', '\n    '))

    print(f"\nGENERATOR v1 {'PASS' if all_ok else 'FAIL'} "
          f"({out['cases']} cases, {out['elapsed']:.1f}s)")
