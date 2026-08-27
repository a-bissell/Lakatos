"""Task 8 (SYNTHESIZE): any card, any number 1..52, FULL 52-card deck.

52 is not b^r, but 52 = 4 x 13. Hypothesis: the radix placement law extends
to mixed radix — deal into b1 piles then b2 piles, with n-1 = d0 + b1*d1
(d0 in 0..b1-1, d1 in 0..b2-1) and the same parity rule (digit complemented
when an odd number of deals follow its round):
    p0 = (b1 - 1) - d0      (one deal follows round 0)
    p1 = d1                 (no deals follow round 1)
Sub-search validates start-independence and the map; then the closed form is
checked against the map; then the full trick verifies over all 52 x 52.
Both orders (4 then 13, and 13 then 4) are tested.
"""
import sys
sys.path.insert(0, '..')
from itertools import product
from deck_sim import make_deck, deal_into_piles, gather_position, verify


def run_rounds(deck, card, pile_counts, placements):
    d = list(deck)
    for b, above in zip(pile_counts, placements):
        piles = deal_into_piles(d, b)
        chosen = next(j for j, p in enumerate(piles) if card in p)
        d = gather_position(piles, chosen, above)
    return d


def sub_search(b1, b2):
    deck = make_deck()
    mapping = {}
    for pair in product(range(b1), range(b2)):
        finals = {run_rounds(deck, card, (b1, b2), pair).index(card)
                  for card in deck}
        mapping[pair] = finals.pop() if len(finals) == 1 else None
    return mapping


def law_pair(n, b1, b2):
    d0, d1 = (n - 1) % b1, (n - 1) // b1
    return ((b1 - 1) - d0, d1)


if __name__ == '__main__':
    for b1, b2 in [(4, 13), (13, 4)]:
        mapping = sub_search(b1, b2)
        bad = [p for p, v in mapping.items() if v is None]
        distinct = len({v for v in mapping.values() if v is not None})
        print(f"b1={b1} b2={b2}: {52 - len(bad)}/52 pairs start-independent, "
              f"{distinct}/52 positions reachable, non-constant: {bad}")
        law_hits = sum(mapping.get(law_pair(n, b1, b2)) == n - 1
                       for n in range(1, 53))
        print(f"  closed form matches map on {law_hits}/52 targets")

        def trick(deck, choices, b1=b1, b2=b2):
            return run_rounds(deck, choices['card'], (b1, b2),
                              law_pair(choices['n'], b1, b2))

        domain = [{'card': c, 'n': n}
                  for c in make_deck() for n in range(1, 53)]
        ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1])
        print(f"  FULL VERIFY: {'PASS' if ok else 'FAIL'} over "
              f"{len(domain)} cases (52 cards x 52 numbers)")
        if not ok:
            print(f"    {len(counter)} fails, e.g. {counter[:3]}")
