"""Task 3 (SYNTHESIZE, invariant-first): 27 cards, spectator freely chooses a
card AND a number n in 1..27. Three deal/gather rounds; card ends at
position n from the top.

Invariant-first design:
  Claim: after each deal-into-3 round, the placement choice (how many piles go
  on top of the chosen pile) fully determines the card's final position,
  independent of its start position, once 3 rounds have run.
SUB-SEARCH step: for each placement triple (p0,p1,p2) in {0,1,2}^3, check the
final position is constant over all 27 starts, and record the map
triple -> final index. Then invert it to get the performer's rule for n.
"""
import sys
sys.path.insert(0, '..')
from itertools import product
from deck_sim import make_deck, deal_into_piles, gather_position, verify


def run_rounds(deck27, card, placements):
    d = list(deck27)
    for above in placements:
        piles = deal_into_piles(d, 3)
        chosen_pile = next(j for j, p in enumerate(piles) if card in p)
        d = gather_position(piles, chosen_pile, above)
    return d


def sub_search_map():
    """Map each placement triple to its (constant) final index, or None."""
    deck27 = make_deck()[:27]
    mapping = {}
    for triple in product(range(3), repeat=3):
        finals = set()
        for card in deck27:
            final = run_rounds(deck27, card, triple)
            finals.add(final.index(card))
        mapping[triple] = finals.pop() if len(finals) == 1 else None
    return mapping


if __name__ == '__main__':
    mapping = sub_search_map()
    non_constant = [t for t, v in mapping.items() if v is None]
    print(f"sub-search: {27 - len(non_constant)}/27 triples give a "
          f"start-independent final position; non-constant: {non_constant}")
    # Look for structure: final index as a function of the digits.
    for triple, idx in sorted(mapping.items(), key=lambda kv: kv[1]):
        p0, p1, p2 = triple
        print(f"  placements {triple} -> final index {idx:2d} "
              f"(p0+3*p1+9*p2 = {p0 + 3 * p1 + 9 * p2})")

    # Invert: rule for spectator's n (position n from top = index n-1).
    inverse = {idx: t for t, idx in mapping.items() if idx is not None}
    if len(inverse) == 27:
        print("bijection confirmed: every final index 0..26 reachable")

        def trick(deck, choices):
            n = choices['n']
            placements = inverse[n - 1]
            return run_rounds(deck[:27], choices['card'], placements)

        domain = [{'card': c, 'n': n}
                  for c in make_deck()[:27] for n in range(1, 28)]
        ok, counter = verify(trick, domain, lambda final, ch: final[ch['n'] - 1])
        print(f"FULL VERIFY: {'PASS' if ok else 'FAIL'} over {len(domain)} cases "
              f"(27 cards x 27 numbers)")
        if not ok:
            print(f"  {len(counter)} fails, e.g. {counter[:3]}")
