"""Task 27 (generator schema v2 proof): invariant search re-derives the
two-card agreement theorem (theorem #2) blind, and the machine finds the
theorem's load-bearing hypothesis by refuting the same claim without it.

The full acceptance ledger (no-hints guard, extensional retrodiction,
corollary, regime break, library-as-known) lives in
invariants_acceptance.py at the repo root. This script is the tricks/
convention runnable proof: enumerate the grammar, run the pilot, hand the
survivor to the refuter through the Decider, print the law the search
found in its own words, and re-verify it at named configurations.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..'))
import invariants as inv


GROUND_TRUTH = [(3, 3, 2), (4, 2, 1), (2, 4, 2), (2, 5, 1), (5, 2, 2)]  # (m, b, rounds)


if __name__ == '__main__':
    kept, prep = inv.pilot()
    print(f'grammar: {prep["enumerated"]} claims; pilot dropped '
          f'{prep["failed"]} failed, {prep["duplicate"]} duplicate, '
          f'{len(prep["implied"])} implied; {prep["kept"]} survived')
    for q, t in kept:
        print(f'  survivor: {q.name} | {t}')
    for weak, strong in prep['implied']:
        print(f'  corollary: {weak}   (implied by {strong})')

    out, _, _ = inv.search(blind=True, verbose=False)
    for r in out['rows']:
        print(f'  {r["disposition"]:<9} {r["name"]}')
        print(f'            {r["detail"][:140]}')

    print('\nthe law, in the search\'s own words: for N = b^m, one round of '
          'deal-into-b + gather in ANY order sends the per-digit '
          '"equal" vector of two tracked cards to its cycle-left by one '
          'place; the count of equal digits is therefore invariant.')

    total, all_ok = 0, True
    q, t = kept[0]
    test = inv._spec_family(q, t, even=True)
    for m, b, r in GROUND_TRUTH:
        ok, w, n = test(m, b, r)
        total += n
        all_ok &= ok
        print(f'  N={b ** m} b={b} rounds={r}: {"PASS" if ok else "FAIL"} '
              f'over {n} (order-sequence, ordered-pair) cases'
              + ('' if ok else f'  witness {w}'))
    print(f't27 {"PASS" if all_ok else "FAIL"}: invariant search, '
          f'{total} verified cases')
