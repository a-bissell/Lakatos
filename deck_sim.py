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


def make_packet(n):
    """Abstract packet of n distinct tokens (0..n-1), index 0 = top.
    Theorems aren't about a 52-card deck: use this (with verify's
    deck_factory parameter) to test procedures past physical deck sizes."""
    return list(range(n))


def _unit_make_packet():
    assert make_packet(5) == [0, 1, 2, 3, 4]
    assert len(set(make_packet(100))) == 100


_unit_make_packet()


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


def down_under_survivor(deck):
    """Down-under elimination: top card to the table ('down'), next to the
    bottom of the packet ('under'), repeated until ONE card remains in hand.
    Returns that survivor. (Cleaner than down_under_deal above, whose
    survivor path is ambiguous; this is the canonical elimination.)"""
    d = list(deck)
    down = True
    while len(d) > 1:
        c = d.pop(0)
        if not down:
            d.append(c)
        down = not down
    return d[0]


def _unit_down_under_survivor():
    # hand-derived: [1] -> 1; [1,2] -> 2 (1 down, 2 stays);
    # [1,2,3] -> 2 (1 down, 2 under, 3 down); [1,2,3,4] -> 4
    assert down_under_survivor([1]) == 1
    assert down_under_survivor([1, 2]) == 2
    assert down_under_survivor([1, 2, 3]) == 2
    assert down_under_survivor([1, 2, 3, 4]) == 4


_unit_down_under_survivor()


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


def gather_position(piles, chosen_idx, above):
    """Reassemble piles so that exactly `above` of the other piles sit ON TOP
    of the chosen pile (remaining others go below). Relative order of the
    other piles is preserved. Returns a single stack, index 0 = top.
    Generalizes gather_middle: gather_middle == gather_position(above=1)
    when there are 3 piles."""
    others = [p for j, p in enumerate(piles) if j != chosen_idx]
    top = [c for p in others[:above] for c in p]
    bottom = [c for p in others[above:] for c in p]
    return top + piles[chosen_idx] + bottom


def gather_order(piles, order):
    """Reassemble piles stacked in the given order (first pile in `order`
    ends on top). The fully general pickup: gather_position is the special
    case where the non-chosen piles keep their relative order."""
    out = []
    for j in order:
        out.extend(piles[j])
    return out


def _unit_gather_order():
    piles = [['a'], ['b'], ['c']]
    assert gather_order(piles, [2, 0, 1]) == ['c', 'a', 'b']
    for chosen in range(3):
        for above in range(3):
            others = [j for j in range(3) if j != chosen]
            order = others[:above] + [chosen] + others[above:]
            assert gather_order(piles, order) == \
                gather_position(piles, chosen, above)


def _unit_gather_position():
    piles = [['a1', 'a2'], ['b1', 'b2'], ['c1', 'c2']]
    assert gather_position(piles, 1, 0) == ['b1', 'b2', 'a1', 'a2', 'c1', 'c2']
    assert gather_position(piles, 1, 1) == ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']
    assert gather_position(piles, 1, 2) == ['a1', 'a2', 'c1', 'c2', 'b1', 'b2']
    assert gather_position(piles, 0, 1) == gather_middle(piles, 0)
    assert gather_position(piles, 1, 1) == gather_middle(piles, 1)
    assert gather_position(piles, 2, 1) == gather_middle(piles, 2)


_unit_gather_position()
_unit_gather_order()


def riffle_merge(a, b, pattern):
    """Riffle-shuffle two packets: pattern is a sequence of 0/1 flags, one
    per output card — 0 takes the next card from packet a, 1 from packet b.
    Models EVERY possible spectator riffle when quantified over all patterns.
    Pure; requires pattern to consume both packets exactly."""
    assert pattern.count(0) == len(a) and pattern.count(1) == len(b)
    ia = ib = 0
    out = []
    for flag in pattern:
        if flag == 0:
            out.append(a[ia]); ia += 1
        else:
            out.append(b[ib]); ib += 1
    return out


def _unit_riffle_merge():
    assert riffle_merge([1, 2], [3, 4], [0, 1, 0, 1]) == [1, 3, 2, 4]
    assert riffle_merge([1, 2], [3, 4], [1, 1, 0, 0]) == [3, 4, 1, 2]
    assert riffle_merge([], [3], [1]) == [3]
    assert riffle_merge([1], [], [0]) == [1]


_unit_riffle_merge()


# ---- verification harness ------------------------------------------------

def verify(trick, domain, reveal, deck_factory=make_deck):
    """trick: fn(deck, choices)->final_state (list, top=0)
       domain: iterable of `choices`
       reveal: fn(final_state, choices)->card  (the card the procedure points at)
       deck_factory: fn()->deck built fresh per case (default: the 52-card
         deck; pass e.g. lambda: make_packet(81) for abstract packets)
    Returns (ok, counterexamples) where a counterexample is (choices, got, want)."""
    counter = []
    for choices in domain:
        deck = deck_factory()
        final = trick(deck, choices)
        got = reveal(final, choices)
        want = choices['card']
        if got != want:
            counter.append((choices, got, want))
    return (len(counter) == 0, counter)


def _unit_verify_factory():
    ok, c = verify(lambda deck, ch: deck, [{'card': 6}],
                   lambda f, ch: f[6], deck_factory=lambda: make_packet(9))
    assert ok and c == []
    ok, c = verify(lambda deck, ch: deck, [{'card': 0}],
                   lambda f, ch: f[1], deck_factory=lambda: make_packet(9))
    assert not ok and len(c) == 1


def verify_prop(trick, domain, predicate, deck_factory=make_deck):
    """Property variant of verify() for effects whose guarantee is a
    structural property of the final state (e.g. Gilbreath) rather than
    'reveal equals the chosen card'.
       predicate: fn(final_state, choices) -> bool
       deck_factory: as in verify()
    Returns (ok, counterexamples) where a counterexample is (choices, final)."""
    counter = []
    for choices in domain:
        deck = deck_factory()
        final = trick(deck, choices)
        if not predicate(final, choices):
            counter.append((choices, final))
    return (len(counter) == 0, counter)


def _unit_verify_prop():
    _unit_verify_factory()
    ok, c = verify_prop(lambda deck, ch: deck, [{'x': 1}],
                        lambda f, ch: len(f) == 7,
                        deck_factory=lambda: make_packet(7))
    assert ok and c == []
    ok, c = verify_prop(lambda deck, ch: deck, [{'x': 1}],
                        lambda f, ch: len(f) == 52)
    assert ok and c == []
    ok, c = verify_prop(lambda deck, ch: deck, [{'x': 1}],
                        lambda f, ch: len(f) == 51)
    assert not ok and len(c) == 1


_unit_verify_prop()


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
