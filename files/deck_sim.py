"""
deck_sim.py — a deterministic verifier for self-working card tricks.

Design contract:
  * Every stack (deck, pile) is a Python list with index 0 = TOP card.
  * Every operation is pure/deterministic given its inputs.
  * A "trick" is a function(deck, choices) -> final_state.
  * verify() brute-forces the ENTIRE free-choice domain. A trick is only
    "found" when verify() returns ok=True. The harness decides, not the model.

This file is meant to be handed to an agent as its ground-truth oracle and
extended with more primitives. It ships with one validated known trick
(the 21-card trick) so you can confirm the harness itself is correct.
"""
from itertools import product

RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SUITS = ['C', 'D', 'H', 'S']
SUIT_WORD = {'C': 'clubs', 'D': 'diamonds', 'H': 'hearts', 'S': 'spades'}
RANK_WORD = {'A': 'ace', '2': 'two', '3': 'three', '4': 'four', '5': 'five',
             '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine', '10': 'ten',
             'J': 'jack', 'Q': 'queen', 'K': 'king'}


def make_deck():
    """52 cards, arbitrary fixed order. index 0 = top."""
    return [(r, s) for s in SUITS for r in RANKS]


def spell_name(card):
    r, s = card
    return (RANK_WORD[r] + 'of' + SUIT_WORD[s])  # letters only


# ---- core primitives (all: index 0 = top, pure) --------------------------

def cut(deck, k):
    """Move top k cards to the bottom (a straight cut)."""
    k %= len(deck)
    return deck[k:] + deck[:k]


def deal_pile(deck, k):
    """Deal k cards one by one into a face-down pile, return (pile, rest).
    Dealing reverses order: last dealt is on top of the pile."""
    dealt = deck[:k]
    pile = list(reversed(dealt))       # last dealt ends on top
    return pile, deck[k:]


def spell_deal(deck, word):
    """Deal one card per letter of `word` into a pile; return (pile, rest)."""
    return deal_pile(deck, len(word))


def transfer_top_to_bottom(deck, k):
    """Move top k cards to the bottom, one at a time (reverses those k)."""
    moved = list(reversed(deck[:k]))
    return deck[k:] + moved


def down_under_deal(deck):
    """Classic elimination: deal top card to table ('down'), next to bottom
    ('under'), repeat until one card remains on the table. Return survivor
    plus the tabled order isn't tracked here; we return the single survivor."""
    d = list(deck)
    table = []
    down = True
    while len(d) > 1 or (len(d) == 1 and down):
        if not d:
            break
        c = d.pop(0)
        if down:
            table.append(c)
        else:
            d.append(c)
        down = not down
    # survivor is the last card left in hand path; reconstruct properly:
    return d, table


def deal_into_piles(deck, num_piles):
    """Round-robin deal into num_piles piles. i-th card from top goes to
    pile (i % num_piles), placed on TOP of that pile (last dealt = top)."""
    piles = [[] for _ in range(num_piles)]
    for i, card in enumerate(deck):
        piles[i % num_piles].insert(0, card)
    return piles


def gather_middle(piles, chosen_idx):
    """Reassemble piles with the chosen pile sandwiched in the middle.
    Returns a single stack, index 0 = top."""
    others = [p for j, p in enumerate(piles) if j != chosen_idx]
    return others[0] + piles[chosen_idx] + others[1]


# ---- verification harness ------------------------------------------------

def verify(trick, domain, reveal):
    """trick: fn(deck, choices)->final_state (list, top=0)
       domain: iterable of `choices`
       reveal: fn(final_state, choices)->card  (the card the procedure points at)
    Returns (ok, counterexamples) where a counterexample is (choices, got, want)."""
    counter = []
    for choices in domain:
        deck = make_deck()
        final = trick(deck, choices)
        got = reveal(final, choices)
        want = choices['card']
        if got != want:
            counter.append((choices, got, want))
    return (len(counter) == 0, counter)


# ---- validation trick: the 21-card trick ---------------------------------
# 21 cards, 3 piles of 7, spectator names which pile holds their card,
# gather with chosen pile in the middle, repeat 3x. Card lands dead center
# (index 10 of 21) regardless of its start position. Fully self-working.

def twenty_one_card_trick(deck, choices):
    d = deck[:21]
    card = choices['card']
    for _ in range(3):
        piles = deal_into_piles(d, 3)
        # spectator "sees" their card and names its pile:
        chosen_pile = next(j for j, p in enumerate(piles) if card in p)
        d = gather_middle(piles, chosen_pile)
    return d


def _reveal_center(final, choices):
    return final[10]  # 11th card, center of 21


def _validate_21():
    # domain: the chosen card can start at any of the 21 positions.
    # We model that by letting 'card' range over the 21 cards in play.
    top21 = make_deck()[:21]
    domain = [{'card': c} for c in top21]
    ok, counter = verify(twenty_one_card_trick, domain, _reveal_center)
    return ok, counter, len(domain)


if __name__ == '__main__':
    ok, counter, n = _validate_21()
    print(f"21-card trick: verified over {n} start positions -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"  {len(counter)} counterexamples, e.g. {counter[0]}")
    else:
        print("  Card lands at center (index 10) for every starting position.")
