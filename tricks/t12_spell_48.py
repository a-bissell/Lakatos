"""Task 12 (MUTATE/extension of t7): spell-your-own-card at near-full-deck
scale — 48 of 52 cards, using the (13,4) mixed-radix engine from t8.

Stack: full 52 cards, position s holds a card whose spell length is
L[s mod 13]. Class lengths: r0=10, r1-r3=11, r4-r6=12, r7-r9=13, r10=14,
r11=15, r12=filler (the 4 leftover mixed-length cards; excluded from the
domain — the census {10:4, 11:13, 12:14, 13:12, 14:5, 15:4} caps uniform
quadruple classes at 12, so 48 is the maximum for this design).

Procedure: deal into 13 piles (spectator points -> j1 = s mod 13, publicly
revealing the length class), gather with p0(j1) piles above; deal into 4
piles (point, gather with p1(j1) above). Spectator spells their card,
one card per letter — last letter is their card.
Placements from the verified (13,4) law for target n = L:
  d0 = (L-1) % 13, d1 = (L-1) // 13, p0 = 12 - d0, p1 = d1.
"""
import sys
sys.path.insert(0, '..')
from deck_sim import (make_deck, deal_into_piles, gather_position,
                      spell_name, verify)


def spell_len(card):
    return len(spell_name(card))


CLASS_LEN = [10, 11, 11, 11, 12, 12, 12, 13, 13, 13, 14, 15, None]


def build_stack():
    by_len = {}
    for c in make_deck():
        by_len.setdefault(spell_len(c), []).append(c)
    classes = []
    for L in CLASS_LEN[:-1]:
        classes.append([by_len[L].pop(0) for _ in range(4)])
    filler = [c for cards in by_len.values() for c in cards]
    assert len(filler) == 4
    classes.append(filler)
    stack = [classes[s % 13][s // 13] for s in range(52)]
    assert len(set(stack)) == 52
    return stack, [c for cl in classes[:-1] for c in cl]


def placements(j1):
    L = CLASS_LEN[j1]
    if L is None:
        return 0, 0                      # filler class, out of domain
    d0, d1 = (L - 1) % 13, (L - 1) // 13
    return 12 - d0, d1


def trick(deck, choices):
    d, _ = build_stack()
    card = choices['card']
    piles = deal_into_piles(d, 13)
    j1 = next(j for j, p in enumerate(piles) if card in p)
    p0, p1 = placements(j1)
    d = gather_position(piles, j1, p0)
    piles = deal_into_piles(d, 4)
    j2 = next(j for j, p in enumerate(piles) if card in p)
    d = gather_position(piles, j2, p1)
    return d


if __name__ == '__main__':
    _, in_domain = build_stack()
    domain = [{'card': c} for c in in_domain]
    ok, counter = verify(trick, domain,
                         lambda f, ch: f[spell_len(ch['card']) - 1])
    print(f"48-card spell-your-own-card: {'PASS' if ok else 'FAIL'} over "
          f"{len(domain)} cases")
    if not ok:
        for ch, got, want in counter[:6]:
            print(f"  {want} (len {spell_len(want)}): got {got}")
