"""Task 6 (INVARIANT): general radix placement-targeting law.

Claim: with N = b^r cards, r rounds of (deal into b piles, spectator points,
gather with p_i piles above the chosen pile), the card lands at 1-indexed
position n for placements derived from the base-b digits d_0..d_{r-1} of n-1:

    p_i = d_i            if (r - 1 - i) is even   (even # of deals follow)
    p_i = (b-1) - d_i    if (r - 1 - i) is odd    (odd  # of deals follow)

Verified here for (b, r) in {(2,4), (3,2), (5,2), (2,5), (7,2)} — every
(card, n) pair, N^2 cases each. t3 (3,3) and t5 (4,2) already passed.
"""
import sys
sys.path.insert(0, '..')
from deck_sim import make_deck, deal_into_piles, gather_position, verify


def law_placements(n, b, r):
    x = n - 1
    digits = []
    for _ in range(r):
        digits.append(x % b)
        x //= b
    return [d if (r - 1 - i) % 2 == 0 else (b - 1) - d
            for i, d in enumerate(digits)]


def make_trick(b, r):
    N = b ** r
    def trick(deck, choices):
        d = deck[:N]
        card = choices['card']
        for above in law_placements(choices['n'], b, r):
            piles = deal_into_piles(d, b)
            chosen = next(j for j, p in enumerate(piles) if card in p)
            d = gather_position(piles, chosen, above)
        return d
    return trick, N


if __name__ == '__main__':
    all_ok = True
    for b, r in [(2, 4), (3, 2), (5, 2), (2, 5), (7, 2)]:
        trick, N = make_trick(b, r)
        domain = [{'card': c, 'n': n}
                  for c in make_deck()[:N] for n in range(1, N + 1)]
        ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1])
        all_ok &= ok
        print(f"b={b} r={r} N={N:2d}: {'PASS' if ok else 'FAIL'} over "
              f"{len(domain)} cases" + (f"  e.g. {counter[:2]}" if not ok else ""))
    print("LAW " + ("VERIFIED across all configs" if all_ok else "REFUTED"))
