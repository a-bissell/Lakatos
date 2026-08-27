"""Task 4 (COMPOSE): 21-card packet. Spectator mentally chooses any card AND
freely names any number n in 10..19.

Procedure:
  1. Three rounds: deal into 3 piles of 7, spectator points to the pile
     holding their card, gather with that pile in the middle.
     (Verified invariant: card is now at index 10, position 11.)
  2. Move 2 cards singly from top to bottom. (Card now position 9.)
  3. Spectator names n (10..19). Deal n cards into a pile (deal reverses).
  4. Deal digitsum(n) cards off that pile back onto the talon.
  5. Reveal: top card of the pile is the chosen card.
Invariant carried: after step 3 the card sits at 1-indexed position
n - 9 + 1 from the top of the dealt pile... concretely, top of pile after
removing digitsum(n) is original position n - digitsum(n) = 9 for all
n in 10..19 (digit-sum reversal force).
"""
import sys
sys.path.insert(0, '..')
from deck_sim import (make_deck, deal_into_piles, gather_middle,
                      transfer_top_to_bottom, deal_pile, verify)


def digitsum(n):
    return sum(int(ch) for ch in str(n))


def trick(deck, choices):
    d = deck[:21]
    card = choices['card']
    for _ in range(3):
        piles = deal_into_piles(d, 3)
        chosen_pile = next(j for j, p in enumerate(piles) if card in p)
        d = gather_middle(piles, chosen_pile)
    d = transfer_top_to_bottom(d, 2)          # position 11 -> position 9
    n = choices['n']
    pile, rest = deal_pile(d, n)              # dealing reverses top n
    removed, pile = deal_pile(pile, digitsum(n))
    return pile


def reveal_top(final, choices):
    return final[0]


if __name__ == '__main__':
    domain = [{'card': c, 'n': n}
              for c in make_deck()[:21] for n in range(10, 20)]
    ok, counter = verify(trick, domain, reveal_top)
    print(f"center + digit-sum force: {'PASS' if ok else 'FAIL'} over "
          f"{len(domain)} cases (21 cards x numbers 10..19)")
    if not ok:
        print(f"  {len(counter)} fails, e.g. {counter[:5]}")
