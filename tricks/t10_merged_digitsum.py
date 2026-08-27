"""Task 10 (MUTATE of t4): merged targeting + digit-sum force, 27 cards.

Spectator thinks of any of 27 cards and names any number n in 10..27.
Three deal/gather rounds (radix-3 placements), then: deal n cards into a
pile, deal digitsum(n) cards off that pile, top card of the pile is theirs.

Improvement over t4: no transfer-2 adjustment step, wider n range
(10..27 vs 10..19), bigger domain (486 vs 210 cases).
Invariant: n - digitsum(n) = 9 for n in 10..19 and 18 for n in 20..27
(casting out nines: n - digitsum(n) is the largest multiple of 9 below n).
So target position 9 <- placements (2,0,0), or 18 <- (2,0,1): only the
LAST pickup differs, so n may be named any time before the third pickup.
"""
import sys
sys.path.insert(0, '..')
from deck_sim import (make_deck, deal_into_piles, gather_position,
                      deal_pile, verify)


def digitsum(n):
    return sum(int(ch) for ch in str(n))


def trick(deck, choices):
    d = deck[:27]
    card, n = choices['card'], choices['n']
    placements = (2, 0, 0) if n <= 19 else (2, 0, 1)
    for above in placements:
        piles = deal_into_piles(d, 3)
        chosen = next(j for j, p in enumerate(piles) if card in p)
        d = gather_position(piles, chosen, above)
    pile, rest = deal_pile(d, n)
    removed, pile = deal_pile(pile, digitsum(n))
    return pile


if __name__ == '__main__':
    domain = [{'card': c, 'n': n}
              for c in make_deck()[:27] for n in range(10, 28)]
    ok, counter = verify(trick, domain, lambda f, ch: f[0])
    print(f"merged digit-sum force: {'PASS' if ok else 'FAIL'} over "
          f"{len(domain)} cases (27 cards x n in 10..27)")
    if not ok:
        print(f"  {len(counter)} fails, e.g. {counter[:5]}")
