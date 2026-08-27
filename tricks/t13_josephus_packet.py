"""Task 13 (COMPOSE, invariant-first): any card, any packet size, down-under
finale.

Part A (invariant): survivor position of a down-under deal on n cards.
Closed-form claim: write n = 2^m + L with 0 <= L < 2^m; the survivor sits at
1-indexed position 2L (or position n when L = 0). Checked against the
simulator for every n in 1..52.

Part B (trick): full 52-card deck. Spectator thinks of ANY card and names
ANY packet size n in 1..52. Performer:
  1. targets the card to position t = n + 1 - J(n) via the verified (4,13)
     mixed-radix two-deal engine (dealing off n cards will REVERSE the top
     n, carrying position t to packet position n + 1 - t = J(n)),
  2. deals off the top n cards into a packet,
  3. hands the packet over for a down-under deal: the survivor is the card.
"""
import sys
sys.path.insert(0, '..')
from deck_sim import (make_deck, deal_into_piles, gather_position, deal_pile,
                      down_under_survivor, verify)


def J(n):
    """Simulator-measured survivor position (1-indexed) for n cards."""
    return down_under_survivor(list(range(1, n + 1)))


def J_closed(n):
    m = 1
    while m * 2 <= n:
        m *= 2
    L = n - m
    return 2 * L if L > 0 else n


def target_placements(n_target):
    d0, d1 = (n_target - 1) % 4, (n_target - 1) // 4
    return (3 - d0, d1)          # verified (4,13) law


def trick(deck, choices):
    card, n = choices['card'], choices['n']
    t = n + 1 - J(n)
    d = list(deck)
    for b, above in zip((4, 13), target_placements(t)):
        piles = deal_into_piles(d, b)
        chosen = next(j for j, p in enumerate(piles) if card in p)
        d = gather_position(piles, chosen, above)
    packet, rest = deal_pile(d, n)
    return [down_under_survivor(packet)]


if __name__ == '__main__':
    # Part A: invariant
    mismatches = [n for n in range(1, 53) if J(n) != J_closed(n)]
    print(f"Part A: J(n) closed form vs simulator, n=1..52: "
          f"{'PASS' if not mismatches else f'FAIL at {mismatches}'}")

    # Part B: full composition
    domain = [{'card': c, 'n': n} for c in make_deck() for n in range(1, 53)]
    ok, counter = verify(trick, domain, lambda f, ch: f[0])
    print(f"Part B: any card x any packet size: "
          f"{'PASS' if ok else 'FAIL'} over {len(domain)} cases "
          f"(52 cards x n in 1..52)")
    if not ok:
        print(f"  {len(counter)} fails, e.g. {counter[:3]}")
