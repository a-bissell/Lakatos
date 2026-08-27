"""Task 14 (INVARIANT): which configurations admit placement targeting?

Part A: mixed-radix law on more factorizations — (5,10), (6,8), (7,7),
(2,26), (26,2), and 51 = (3,17): full any-card-any-number verify each.

Part B: UNEVEN piles — 52 cards into 3 piles (18/17/17), 3 and 4 rounds.
Sub-search start-independence per placement vector: how many vectors give a
start-independent final position, which positions are reachable, and how
large is the spread when independence fails.
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


def law_pair(n, b1):
    d0, d1 = (n - 1) % b1, (n - 1) // b1
    return ((b1 - 1) - d0, d1)


if __name__ == '__main__':
    print("Part A: mixed-radix law across factorizations")
    for b1, b2 in [(5, 10), (6, 8), (7, 7), (2, 26), (26, 2), (3, 17)]:
        N = b1 * b2

        def trick(deck, choices, b1=b1, b2=b2):
            return run_rounds(deck[:b1 * b2], choices['card'], (b1, b2),
                              law_pair(choices['n'], b1))

        domain = [{'card': c, 'n': n}
                  for c in make_deck()[:N] for n in range(1, N + 1)]
        ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1])
        print(f"  ({b1:2d},{b2:2d}) N={N}: {'PASS' if ok else 'FAIL'} over "
              f"{len(domain)} cases"
              + (f" — e.g. {counter[:2]}" if not ok else ""))

    print("Part B: uneven piles — 52 cards, 3 piles (18/17/17)")
    deck = make_deck()
    for rounds in (3, 4):
        constant, reachable, max_spread = 0, set(), 0
        for placements in product(range(3), repeat=rounds):
            finals = {run_rounds(deck, card, (3,) * rounds,
                                 placements).index(card) for card in deck}
            if len(finals) == 1:
                constant += 1
                reachable.add(finals.pop())
            else:
                max_spread = max(max_spread, len(finals))
        print(f"  rounds={rounds}: {constant}/{3 ** rounds} placement vectors "
              f"start-independent; reachable positions: {sorted(reachable)}; "
              f"worst spread {max_spread} distinct finals")
