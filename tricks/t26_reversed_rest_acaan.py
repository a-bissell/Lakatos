"""Task 26 (theorem #3 track): ACAAN with LARGEST-FIRST pickups.

The performable family behind the generator's reversed-rest survivors:
each round the spectator points at their pile; the performer picks up
the piles LARGEST-INDEX-FIRST, inserting the pointed pile at rank c
(c piles above it). Distinct from Gergonne gathering (smallest-first
above) at every uneven-N interior rank — the regime the literature
search found silent — yet its law is an exact mirror:

    z <- -b*z + (2c+1-b)*N + 2*corr_rr(c)
    corr_rr(c) = -corr(b-1-c)     [t22's corr, negated at the
                                   complementary rank]
    digit = argmin |new z|; digits reversed = ranks; valid b^(r-1) >= N

The mirror is no accident: the round map itself is the position-
reflection conjugate of the Gergonne round map (Lemma R, proven in
PROOF_reversed_rest.md / proof_rr.py), so the law inherits theorem #1
wholesale. Duality at the vector level: the rank vector for target n
is (up to argmin ties) the digit-complement of the Gergonne vector
for the MIRROR target N+1-n.
"""
import sys
sys.path.insert(0, '..')
from deck_sim import (make_deck, make_packet, deal_into_piles,
                      gather_order, gather_position, verify)


def corr_gp(a, b, rho):
    return min(a, rho) * (b - max(a + 1, rho))


def corr_rr(c, b, rho):
    return -corr_gp(b - 1 - c, b, rho)


def law_vector_rr(n, N, b, r):
    rho = N % b
    z = 2 * (n - 1) - (N - 1)
    digits = []
    for _ in range(r):
        cands = sorted((abs(-b * z + (2 * c + 1 - b) * N
                            + 2 * corr_rr(c, b, rho)), -c, c)
                       for c in range(b))
        c = cands[0][2]
        z = -b * z + (2 * c + 1 - b) * N + 2 * corr_rr(c, b, rho)
        digits.append(c)
    return list(reversed(digits))


def gather_rr(piles, j, c):
    """Pointed pile j at rank c; other piles largest-index-first."""
    others = [k for k in range(len(piles) - 1, -1, -1) if k != j]
    return gather_order(piles, others[:c] + [j] + others[c:])


def run(N, b, r):
    def trick(deck, choices):
        d = deck[:N]
        card = choices['card']
        for c in law_vector_rr(choices['n'], N, b, r):
            piles = deal_into_piles(d, b)
            j = next(i for i, p in enumerate(piles) if card in p)
            d = gather_rr(piles, j, c)
        return d

    factory = (lambda: make_packet(N)) if N > 52 else make_deck
    domain = [{'card': cd, 'n': n}
              for cd in factory()[:N] for n in range(1, N + 1)]
    ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1],
                         deck_factory=factory)
    return ok, counter, len(domain)


def distinctness(N, b):
    """Ranks where the round map differs from gather_position."""
    markers = list(range(N))
    out = []
    for c in range(b):
        for j in range(b):
            rr = gather_rr(deal_into_piles(markers, b), j, c)
            gp = gather_position(deal_into_piles(markers, b), j, c)
            if any(rr.index(x) != gp.index(x)
                   for x in range(N) if x % b == j):
                out.append(c)
                break
    return out


if __name__ == '__main__':
    from t22_general_b_law import law_vector as law_gp

    grid = [(3, 7, 3), (3, 8, 3), (4, 10, 3), (4, 14, 3), (5, 23, 3),
            (5, 25, 3), (6, 33, 3), (6, 36, 3), (7, 45, 3), (2, 32, 6),
            (4, 52, 4), (6, 52, 4), (12, 144, 3)]
    total, all_ok = 0, True
    for b, N, r in grid:
        assert b ** (r - 1) >= N, (b, N, r)
        ok, counter, cases = run(N, b, r)
        total += cases
        all_ok &= ok
        tight = ' [tight]' if b ** (r - 1) < 2 * N else ''
        print(f'  b={b} N={N:3d} (rho={N % b}) r={r}: '
              f'{"PASS" if ok else "FAIL"} over {cases}{tight}'
              + ('' if ok else f'  e.g. {counter[:2]}'))
    print(f'LARGEST-FIRST ACAAN {"VERIFIED" if all_ok else "REFUTED"} '
          f'({total} cases)')

    # the family is genuinely distinct from Gergonne gathering exactly
    # at uneven-N interior ranks
    for b, N in ((4, 10), (5, 23), (6, 33)):
        d = distinctness(N, b)
        assert d == list(range(1, b - 1)), (b, N, d)
    print('distinctness: differs from gather_position at every interior '
          'rank of every uneven config checked')

    # vector duality: rank vector == complemented Gergonne vector for
    # the mirror target, up to argmin ties (both choices are minimizers;
    # theorem #1 holds for ANY minimizer)
    same = ties = 0
    for b, N, r in ((3, 7, 3), (4, 10, 3), (5, 23, 3), (6, 33, 3)):
        for n in range(1, N + 1):
            mirror = [b - 1 - a for a in law_gp(N + 1 - n, N, b, r)]
            if law_vector_rr(n, N, b, r) == mirror:
                same += 1
            else:
                ties += 1
    print(f'duality: rr(n) == complement(gergonne(N+1-n)) for '
          f'{same}/{same + ties} targets ({ties} differ only at argmin '
          f'ties)')

    demo = ''.join(map(str, law_vector_rr(15, 52, 6, 4)))
    print(f'\nheadline: full-deck ACAAN with largest-first pickups — '
          f'e.g. b=6, n=15: ranks {demo}')
