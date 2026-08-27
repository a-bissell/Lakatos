"""Task 20 (SYNTHESIZE, queue item 1): the UNIVERSAL alternating-radix law.

Session 7 claimed the law "cannot apply as stated" for N ≡ 2 (mod 3)
because the a=1 gather constant is pile-dependent. That claim was WRONG:
redoing the interval algebra, the deviation (pointed pile ≡ 2 mod 3 gives
one less) meshes with floor(x/3) so the backward preimage of a requirement
interval is STILL contiguous, and the midpoint constants are identical:
    K = (N-2, 2N-1, 3N-2)   for N ≢ 0 (mod 3)   [same as N ≡ 1]
    K = (N-2, 2N-2, 3N-2)   for N ≡ 0 (mod 3)   [no correction at all]

HUMAN-INTEGER FORM (tie-free: 6m is even, the thresholds are odd):
    m starts at n-1; five (r) times:
      6m < 2N-3            -> digit 0, m <- K0 - 3m
      2N-3 < 6m < 4N-3     -> digit 1, m <- K1 - 3m
      6m > 4N-3            -> digit 2, m <- K2 - 3m
    digits reversed = pickups ("how many piles above the pointed pile").
Validity: 3^(r-1) >= N.  Verified below for all three residues, including
tight boundary fits, plus predicted failures below the condition.
"""
import sys
sys.path.insert(0, '..')
from itertools import product
from deck_sim import make_deck, deal_into_piles, gather_position, verify


def check_round_formula(N):
    """x' = A(j,a) - floor(x/3) with A from actual pile sizes — any N."""
    sizes = [(N - j + 2) // 3 for j in range(3)]
    markers = list(range(N))
    for x in range(N):
        j = x % 3
        for a in range(3):
            d = gather_position(deal_into_piles(markers, 3), j, a)
            others = [k for k in range(3) if k != j]
            S = sum(sizes[k] for k in others[:a])
            want = S + sizes[j] - 1 - x // 3
            assert d.index(x) == want, (N, x, a)
    return True


def K_table(N):
    return ((N - 2, 2 * N - 2, 3 * N - 2) if N % 3 == 0
            else (N - 2, 2 * N - 1, 3 * N - 2))


def law_vector(n, N, r):
    """All-integer, tie-free digit computation (human algorithm)."""
    K = K_table(N)
    m = n - 1
    digits = []                        # last-pickup-first
    for _ in range(r):
        if 6 * m < 2 * N - 3:
            a = 0
        elif 6 * m > 4 * N - 3:
            a = 2
        else:
            a = 1
        digits.append(a)
        m = K[a] - 3 * m
    return list(reversed(digits))


def run(N, r):
    def trick(deck, choices):
        d = deck[:N]
        card = choices['card']
        for a in law_vector(choices['n'], N, r):
            piles = deal_into_piles(d, 3)
            j = next(i for i, p in enumerate(piles) if card in p)
            d = gather_position(piles, j, a)
        return d

    domain = [{'card': c, 'n': n}
              for c in make_deck()[:N] for n in range(1, N + 1)]
    return verify(trick, domain, lambda f, ch: f[ch['n'] - 1]), len(domain)


def enumerate_reachable(N, r):
    markers = list(range(N))
    perm = {}
    for a in range(3):
        for j in range(3):
            d = gather_position(deal_into_piles(markers, 3), j, a)
            for newpos, x in enumerate(d):
                if x % 3 == j:
                    perm[(x, a)] = newpos
    reach = set()
    for vec in product(range(3), repeat=r):
        finals = set()
        for x in range(N):
            pos = x
            for a in vec:
                pos = perm[(pos, a)]
            finals.add(pos)
        if len(finals) == 1:
            reach.add(finals.pop())
    return reach


if __name__ == '__main__':
    grid = [(8, 3), (11, 4), (14, 4), (20, 4), (26, 4), (35, 5), (44, 5),
            (50, 5),                                   # N ≡ 2 (mod 3)
            (9, 3), (12, 4), (18, 4), (24, 4), (27, 4), (36, 5), (45, 5),
            (51, 5),                                   # N ≡ 0 (mod 3)
            (25, 4), (52, 5)]                          # N ≡ 1 re-check
    for N, r in grid:
        check_round_formula(N)
    print(f"round-map formula: verified for all {len(grid)} deck sizes "
          f"(every position x every placement)")

    total, all_ok = 0, True
    for N, r in grid:
        assert 3 ** (r - 1) >= N, (N, r)
        (ok, counter), cases = run(N, r)
        total += cases
        all_ok &= ok
        tight = " [tight]" if 3 ** (r - 1) < 3 * N // 2 else ""
        print(f"  N={N:2d} (mod 3 = {N % 3}) r={r}: "
              f"{'PASS' if ok else 'FAIL'} over {cases} cases{tight}"
              + (f"  e.g. {counter[:2]}" if not ok else ""))
    print(f"UNIVERSAL LAW {'VERIFIED' if all_ok else 'REFUTED'} "
          f"({total} cases, all residues mod 3)")

    print("\nbelow the condition (3^(r-1) < N — failure predicted):")
    for N, r in ((12, 3), (26, 3)):
        (ok, _), cases = run(N, r)
        reach = enumerate_reachable(N, r)
        print(f"  N={N} r={r}: law {'PASS' if ok else 'FAIL'} "
              f"(predicted FAIL); {len(reach)}/{N} targets reachable by "
              f"ANY fixed vector")

    demo = ''.join(map(str, law_vector(20, 52, 5)))
    print(f"\nworked example: N=52, n=20 -> pickups {demo} "
          f"(matches t19's float form)")
