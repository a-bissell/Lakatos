"""Task 21 (SYNTHESIZE, queue item 1): the FOUR-PILE analog of the
universal radix law.

Derivation (verified below): dealing N into 4 piles and gathering with
a in {0,1,2,3} other piles above the pointed pile moves the tracked card
by x' = A(j,a) - floor(x/4). The pile-dependence of A is at most one unit
and always meshes with floor(x/4) so requirement preimages stay
contiguous. Centered on the deck with the DOUBLED offset z = 2(n-1)-(N-1)
(kept integer), the law is base-(-4) with half-step digits:

    z <- -4z + (2a-3)*N + 2*delta(N mod 4, a)
    delta tables (a = 0..3):
      N≡0: (0,0,0,0)    N≡1: (0,2,1,0)
      N≡2: (0,2,2,0)    N≡3: (0,1,2,0)
    digit choice: the a minimizing |new z| (tie -> larger a);
    digits REVERSED give the pickups.

Validity conjecture: 4^(r-1) >= N. For 52 = 4x13 (≡ 0 mod 4, delta = 0):
FOUR deals cover the full deck — two fewer physical steps than the
3-pile law.
"""
import sys
sys.path.insert(0, '..')
from itertools import product
from deck_sim import make_deck, deal_into_piles, gather_position, verify

DELTA = {0: (0, 0, 0, 0), 1: (0, 2, 1, 0), 2: (0, 2, 2, 0), 3: (0, 1, 2, 0)}


def check_round_formula(N):
    """x' = S(j,a) + s_j - 1 - floor(x/4), any N, from actual pile sizes."""
    sizes = [(N - j + 3) // 4 for j in range(4)]
    markers = list(range(N))
    for x in range(N):
        j = x % 4
        others = [k for k in range(4) if k != j]
        for a in range(4):
            d = gather_position(deal_into_piles(markers, 4), j, a)
            want = sum(sizes[k] for k in others[:a]) + sizes[j] - 1 - x // 4
            assert d.index(x) == want, (N, x, a)
    return True


def law_vector(n, N, r):
    z = 2 * (n - 1) - (N - 1)
    dl = DELTA[N % 4]
    digits = []                                # last-pickup-first
    for _ in range(r):
        cands = sorted((abs(-4 * z + (2 * a - 3) * N + 2 * dl[a]), -a, a)
                       for a in range(4))
        a = cands[0][2]
        z = -4 * z + (2 * a - 3) * N + 2 * dl[a]
        digits.append(a)
    return list(reversed(digits))


def run(N, r):
    def trick(deck, choices):
        d = deck[:N]
        card = choices['card']
        for a in law_vector(choices['n'], N, r):
            piles = deal_into_piles(d, 4)
            j = next(i for i, p in enumerate(piles) if card in p)
            d = gather_position(piles, j, a)
        return d

    domain = [{'card': c, 'n': n}
              for c in make_deck()[:N] for n in range(1, N + 1)]
    return verify(trick, domain, lambda f, ch: f[ch['n'] - 1]), len(domain)


def enumerate_reachable(N, r):
    markers = list(range(N))
    perm = {}
    for a in range(4):
        for j in range(4):
            d = gather_position(deal_into_piles(markers, 4), j, a)
            for newpos, x in enumerate(d):
                if x % 4 == j:
                    perm[(x, a)] = newpos
    reach = set()
    for vec in product(range(4), repeat=r):
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
    grid = [(8, 3), (12, 3), (16, 3), (20, 4), (32, 4), (40, 4), (48, 4),
            (52, 4),                                    # N ≡ 0 (mod 4)
            (9, 3), (13, 3), (17, 4), (29, 4), (45, 4), (49, 4),   # ≡ 1
            (10, 3), (14, 3), (26, 4), (38, 4), (50, 4),           # ≡ 2
            (11, 3), (15, 3), (27, 4), (39, 4), (51, 4)]           # ≡ 3
    for N, r in grid:
        check_round_formula(N)
    print(f"round-map formula: verified for all {len(grid)} deck sizes "
          f"(every position x every placement, 4 piles)")

    total, all_ok = 0, True
    for N, r in grid:
        assert 4 ** (r - 1) >= N, (N, r)
        (ok, counter), cases = run(N, r)
        total += cases
        all_ok &= ok
        tight = " [tight]" if 4 ** (r - 1) < 2 * N else ""
        print(f"  N={N:2d} (mod 4 = {N % 4}) r={r}: "
              f"{'PASS' if ok else 'FAIL'} over {cases} cases{tight}"
              + (f"  e.g. {counter[:2]}" if not ok else ""))
    print(f"FOUR-PILE LAW {'VERIFIED' if all_ok else 'REFUTED'} "
          f"({total} cases, all residues mod 4)")

    print("\nbelow the condition (4^(r-1) < N):")
    for N, r in ((17, 3), (20, 3), (26, 3)):
        (ok, _), cases = run(N, r)
        reach = enumerate_reachable(N, r)
        print(f"  N={N} r={r}: law {'PASS' if ok else 'FAIL'}; "
              f"{len(reach)}/{N} targets reachable by ANY fixed vector")

    demo = ''.join(map(str, law_vector(15, 52, 4)))
    print(f"\nworked example: N=52, n=15 -> pickups {demo} (four deals)")
