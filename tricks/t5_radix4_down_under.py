"""Task 5 (COMPOSE): 16-card packet, two effects from one engine.

Part A (parametric variant of t3's radix invariant): deal into 4 piles of 4,
spectator indicates the pile, performer gathers with a chosen number of piles
above; TWO rounds send the card to any target position 1..16.
Sub-search finds the placement-pair -> final-index map, checks it is
start-independent, and inverts it.

Part B (novel composition): target the card to the down-under survivor
position, then eliminate with a down-under deal. Survivor IS the chosen card.
Spectator's only actions: think of a card, point at piles. |D| = 16.
"""
import sys
sys.path.insert(0, '..')
from itertools import product
from deck_sim import (make_deck, deal_into_piles, gather_position,
                      down_under_survivor, verify)


def run_rounds(deck16, card, placements):
    d = list(deck16)
    for above in placements:
        piles = deal_into_piles(d, 4)
        chosen_pile = next(j for j, p in enumerate(piles) if card in p)
        d = gather_position(piles, chosen_pile, above)
    return d


def sub_search_map():
    deck16 = make_deck()[:16]
    mapping = {}
    for pair in product(range(4), repeat=2):
        finals = {run_rounds(deck16, card, pair).index(card)
                  for card in deck16}
        mapping[pair] = finals.pop() if len(finals) == 1 else None
    return mapping


if __name__ == '__main__':
    mapping = sub_search_map()
    bad = [p for p, v in mapping.items() if v is None]
    print(f"sub-search: {16 - len(bad)}/16 placement pairs start-independent; "
          f"non-constant: {bad}")
    inverse = {idx: p for p, idx in mapping.items() if idx is not None}
    print(f"reachable positions: {len(inverse)}/16")
    for idx in sorted(inverse):
        p0, p1 = inverse[idx]
        print(f"  index {idx:2d} <- placements ({p0},{p1})   "
              f"[base4 digits of idx: d0={idx % 4} d1={idx // 4}]")

    # Part A verify: any card to any named position 1..16
    def target_trick(deck, choices):
        return run_rounds(deck[:16], choices['card'], inverse[choices['n'] - 1])

    domain_a = [{'card': c, 'n': n}
                for c in make_deck()[:16] for n in range(1, 17)]
    ok_a, ca = verify(target_trick, domain_a, lambda f, ch: f[ch['n'] - 1])
    print(f"Part A (radix-4 targeting): {'PASS' if ok_a else 'FAIL'} over "
          f"{len(domain_a)} cases")
    if not ok_a:
        print(f"  fails e.g. {ca[:3]}")

    # Part B: survivor position of a 16-card down-under, then compose
    marker = list(range(16))
    surv_idx = down_under_survivor(marker)
    print(f"down-under survivor of 16 cards = index {surv_idx} "
          f"(position {surv_idx + 1})")

    def compose_trick(deck, choices):
        d = run_rounds(deck[:16], choices['card'], inverse[surv_idx])
        return [down_under_survivor(d)]

    domain_b = [{'card': c} for c in make_deck()[:16]]
    ok_b, cb = verify(compose_trick, domain_b, lambda f, ch: f[0])
    print(f"Part B (targeting + down-under reveal): "
          f"{'PASS' if ok_b else 'FAIL'} over {len(domain_b)} cases")
    if not ok_b:
        print(f"  fails e.g. {cb[:3]}")
