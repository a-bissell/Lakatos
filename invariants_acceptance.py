"""invariants_acceptance.py — acceptance ledger for generator schema v2
(invariant search), with theorem #2 as the BLIND retrodiction test.

The bar (session 19): "mechanise invariant-first search, and let the test
be whether it re-derives the two-card agreement conservation theorem
unaided, the way t25 re-derived the general-b law." The ledger, in order:

  0 NO-HINTS GUARD   invariants.py's source names no committed invariant,
                     theorem, proof, or rotation — the boundary is
                     enforced by scanning, not promised.
  1 GRAMMAR + PILOT  the schema enumerates its claims and the pilot
                     filters them: counts of constants / failures /
                     duplicates / implied, and exactly what survived.
  2 BLIND RUN        oracle OFF. Every survivor must be a SURVIVOR at
                     ROBUST_CONJECTURE with scope exhaustive (its instance
                     tests were built through the Decider).
  3 RETRODICTION     the survivor is EXTENSIONALLY theorem #2: its quantity
                     induces the same partition of ordered pairs as the
                     base-b agreement set A(p, q) at the reference config,
                     and its transport is the theorem's one-step rotation.
                     THIS file may know the theorem; invariants.py may not.
  4 COROLLARY        the cardinality invariant |A| was derived by the search
                     as an implied claim (a function of the survivor with
                     commuting transport), not merely absent.
  5 REGIME BREAK     the probe with the N = b^m hypothesis dropped is
                     REFUTED by the derived schedule at a non-power N, with
                     a witness — the machine locating the theorem's
                     load-bearing hypothesis (cf. proof_conservation D7).
  6 NEGATIVE SPACE   every claim under a fixed lens (2, 3, 4, 5) failed the
                     pilot: nothing that is not the op's own radix survived.
  7 LIBRARY-AS-KNOWN oracle ON. The survivor is SUPPRESSED as
                     LibraryInvariant with an exact, exhaustive-scope
                     witness — so a future run cannot count the
                     rediscovery as novel. The probe still dies in the
                     refuter.

Every check prints PASS/FAIL; the exit summary is the ledger verdict.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import invariants as inv


# ---- the answer, implemented independently (this file may know it) ----------

def agreement_set(p, q, b, m):
    return frozenset(i for i in range(m)
                     if (p // b ** i) % b == (q // b ** i) % b)


def rot(A, m):
    return frozenset((i - 1) % m for i in A)


REF = (3, 3)           # (m, b): N = 27, the config t16 measured by hand


# ---- checks -------------------------------------------------------------------

def check_no_hints():
    src = open(os.path.join(ROOT, 'invariants.py')).read()
    banned = ('agree', 'conserv', 'theorem', 't16', 'proof', 'rot',
              'PROOF', 'impossib')
    found = [w for w in banned if w in src]
    return not found, found


def partition(values):
    ids, key = {}, []
    for v in values:
        key.append(ids.setdefault(v, len(ids)))
    return tuple(key)


def check_retrodiction(q, t):
    m, b = REF
    N = b ** m
    c = inv.context(N, b, q)
    pairs = inv.tracked(N, 2)
    ours = [agreement_set(p, r, b, m) for p, r in pairs]
    theirs = [q.fn(ps, c) for ps in pairs]
    same_partition = partition(ours) == partition(theirs)
    # transport: the survivor's T must act on its values as rot acts on A
    f = dict(zip(ours, theirs))
    T = inv.TRANSPORTS[t]
    commutes = all(T(f[A]) == f[rot(A, m)] for A in set(ours))
    return same_partition and commutes, dict(
        N=N, pairs=len(pairs), classes=len(set(ours)),
        same_partition=same_partition, transport_commutes=commutes)


def check_corollary(report, survivor_label):
    """|A| must appear among the implied claims, tracing back to the
    survivor (directly or through another implied claim)."""
    implied = dict(report['implied'])            # weak -> strong
    m, b = REF
    N = b ** m
    pairs = inv.tracked(N, 2)
    ours = partition([len(agreement_set(p, r, b, m)) for p, r in pairs])
    for weak, strong in implied.items():
        qname, tname = weak.rsplit(' | ', 1)
        q = next(x for x in inv.quantities() if x.name == qname)
        c = inv.context(N, b, q)
        if q.arity == 2 and partition([q.fn(ps, c) for ps in pairs]) == ours:
            # walk the implication chain to the survivor
            s = strong
            while s in implied:
                s = implied[s]
            return s == survivor_label, weak
    return False, None


def is_power(N, b):
    while N > 1 and N % b == 0:
        N //= b
    return N == 1


def blind_and_oracle_runs():
    blind, prep, kept = inv.search(blind=True, verbose=False)
    oracle, _, _ = inv.search(blind=False, verbose=False)
    return blind, oracle, prep, kept


if __name__ == '__main__':
    ledger = []

    ok, found = check_no_hints()
    ledger.append(('0 no-hints guard', ok))
    print(f"[0] no-hints guard: {'PASS' if ok else 'FAIL ' + str(found)} "
          f"(invariants.py names no committed invariant / theorem / proof)")

    kept, prep = inv.pilot()
    ok = prep['kept'] >= 1 and prep['enumerated'] >= 150
    ledger.append(('1 grammar + pilot', ok))
    print(f"[1] grammar + pilot: {'PASS' if ok else 'FAIL'} — "
          f"{prep['enumerated']} claims enumerated; pilot dropped "
          f"{prep['constant']} constant, {prep['failed']} failed, "
          f"{prep['duplicate']} duplicate, {len(prep['implied'])} implied; "
          f"{prep['kept']} survived")
    for q, t in kept:
        print(f"    survivor: {q.name} | {t}")
    for weak, strong in prep['implied']:
        print(f"    implied:  {weak}  <=  {strong}")

    blind, oracle, _, _ = blind_and_oracle_runs()
    surv = [r for r in blind['rows'] if r['disposition'] == 'SURVIVOR']
    even_rows = [r for r in blind['rows'] if r['name'].endswith('[N = b^m]')]
    ok = (len(surv) == len(even_rows) == len(kept) >= 1
          and all(r['status'] == 'ROBUST_CONJECTURE'
                  and r['scope'] == 'exhaustive' for r in surv))
    ledger.append(('2 blind run', ok))
    print(f"[2] blind run (oracle off): {'PASS' if ok else 'FAIL'} — "
          f"{len(surv)}/{len(even_rows)} even-pile claims at "
          f"ROBUST_CONJECTURE, scope exhaustive; {blind['cases']} cases, "
          f"{blind['elapsed']:.1f}s")
    for r in surv:
        print(f"    {r['name']}: {r['detail'].split(';')[0]}")

    q, t = kept[0]
    ok, info = check_retrodiction(q, t)
    ledger.append(('3 retrodiction', ok))
    print(f"[3] retrodiction: {'PASS' if ok else 'FAIL'} — survivor "
          f"'{q.name} | {t}' is extensionally the base-b agreement set "
          f"with the one-step rotation: same partition of {info['pairs']} "
          f"ordered pairs into {info['classes']} classes at N={info['N']} "
          f"= {info['same_partition']}, transport commutes with rot = "
          f"{info['transport_commutes']}")

    ok, weak = check_corollary(prep, f'{q.name} | {t}')
    ledger.append(('4 corollary', ok))
    print(f"[4] corollary: {'PASS' if ok else 'FAIL'} — the cardinality "
          f"invariant |A| was derived as an implied claim"
          + (f" ('{weak}')" if weak else ' (NOT FOUND)'))

    probes = [r for r in blind['rows'] if r['name'].endswith('[any N]')]
    ok = bool(probes) and all(
        r['disposition'] == 'REFUTED' and r.get('detail')
        and not is_power(*_k[:2]) for r in probes
        for _k in [eval(r['detail'].split('killed at ')[1].split(',')[0]
                        + ',' + r['detail'].split('killed at ')[1]
                        .split(',')[1] + ')')])
    ledger.append(('5 regime break', ok))
    print(f"[5] regime break: {'PASS' if ok else 'FAIL'} — the probe with "
          f"N = b^m dropped was refuted at a non-power N:")
    for r in probes:
        print(f"    {r['detail'][:150]}")

    fixed_lens = [(q_, t_) for q_, t_ in kept if q_.lens != 'radix']
    ok = not fixed_lens
    ledger.append(('6 negative space', ok))
    print(f"[6] negative space: {'PASS' if ok else 'FAIL'} — no claim under "
          f"a fixed lens (2, 3, 4, 5) survived the pilot; only the op's own "
          f"radix carries an invariant")

    sup = [r for r in oracle['rows'] if r['disposition'] == 'SUPPRESSED']
    ok = (len(sup) == len(kept) and
          all('LibraryInvariant' in r['detail'] and
              'exhaustive' in r['detail'] for r in sup)
          and oracle['drift']['needs_review'] == 0
          and all(r['disposition'] == 'REFUTED' for r in oracle['rows']
                  if r['name'].endswith('[any N]')))
    ledger.append(('7 library-as-known', ok))
    print(f"[7] library-as-known (oracle on): {'PASS' if ok else 'FAIL'} — "
          f"{len(sup)} suppressed as LibraryInvariant, review queue "
          f"{oracle['drift']['needs_review']}; the regime probe still "
          f"REFUTED")
    for r in sup:
        print(f"    {r['detail'][:160]}")

    verdict = all(ok for _, ok in ledger)
    print(f"\nINVARIANT SEARCH ACCEPTANCE {'PASS' if verdict else 'FAIL'} "
          f"({sum(ok for _, ok in ledger)}/{len(ledger)}; "
          f"{blind['cases'] + oracle['cases']} decider cases) — the schema "
          f"{'re-derived theorem #2 unaided' if verdict else 'did NOT meet the bar'}")
    sys.exit(0 if verdict else 1)
