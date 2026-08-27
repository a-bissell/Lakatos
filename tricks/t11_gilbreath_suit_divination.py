"""Task 11 (COMPOSE): Gilbreath suit divination — a reveal built on the
verified [[gilbreath-principle]].

Packet stacked cycling C,D,H,S. Spectator: deals off ANY m cards (reversing),
riffles them back in ANY way, takes ANY quartet (block of 4 off the top
structure), secretly removes ANY one of its 4 cards. Performer glances at
the remaining 3 and names the suit of the removed card (the one suit
missing from the quartet).

Domains (exhaustive):
  N=12: every pattern x every quartet x every removal = 4096*3*4 = 49,152
        explicit cases via verify_prop.
  N=16: every pattern (65,536), with all 4x4 quartet/removal choices
        checked inside the predicate (universally quantified there) —
        same total coverage, cached shuffle per pattern.
"""
import sys
sys.path.insert(0, '..')
from itertools import product
from deck_sim import RANKS, SUITS, deal_pile, riffle_merge, verify_prop


def suit_cycle_stack(n):
    assert n % 4 == 0
    return [(RANKS[i // 4], SUITS[i % 4]) for i in range(n)]


def shuffle(n, pattern):
    deck = suit_cycle_stack(n)
    pile, rest = deal_pile(deck, pattern.count(0))
    return riffle_merge(pile, rest, pattern)


def missing_suit(three_cards):
    return (set(SUITS) - {s for _, s in three_cards}).pop()


def divination_ok(final, q, i):
    quartet = final[4 * q: 4 * q + 4]
    removed = quartet[i]
    rest3 = quartet[:i] + quartet[i + 1:]
    named = missing_suit(rest3) if len({s for _, s in rest3}) == 3 else None
    return named == removed[1]


if __name__ == '__main__':
    # N=12: fully explicit domain
    n = 12
    domain = [{'pattern': list(p), 'q': q, 'i': i}
              for p in product((0, 1), repeat=n)
              for q in range(3) for i in range(4)]
    ok, counter = verify_prop(lambda deck, ch: shuffle(n, ch['pattern']),
                              domain,
                              lambda f, ch: divination_ok(f, ch['q'], ch['i']))
    print(f"N=12 explicit: {'PASS' if ok else 'FAIL'} over {len(domain)} cases")
    if not ok:
        print(f"  e.g. {counter[0][0]}")

    # N=16: quartet/removal universally quantified inside the predicate
    n = 16
    domain16 = [{'pattern': list(p)} for p in product((0, 1), repeat=n)]
    ok16, counter16 = verify_prop(
        lambda deck, ch: shuffle(n, ch['pattern']), domain16,
        lambda f, ch: all(divination_ok(f, q, i)
                          for q in range(4) for i in range(4)))
    total = len(domain16) * 16
    print(f"N=16 folded:  {'PASS' if ok16 else 'FAIL'} over {len(domain16)} "
          f"patterns x 16 quartet/removal choices = {total} cases")
    if not ok16:
        print(f"  e.g. {counter16[0][0]}")
