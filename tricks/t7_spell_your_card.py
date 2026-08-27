"""Task 7 (SYNTHESIZE, invariant-first): spectator spells their OWN card.

16-card packet, stacked. Spectator thinks of any of the 16 cards. Two deals
into 4 piles (spectator points to their pile each time, performer gathers).
Then the spectator silently spells their card's name, dealing one card per
letter: the card on the LAST letter is theirs. Performer never knows the card.

Invariant chain:
  * stack: positions == 0,1 (mod 4) hold 11-letter cards, positions == 2,3
    (mod 4) hold 12-letter cards  ->  the first pile-pointing (j1 = start
    mod 4) publicly reveals the card's spell-length class without revealing
    the card.
  * radix-4 targeting (verified t5): placements (1,2) -> position 11,
    (0,2) -> position 12. Only the FIRST pickup differs, and it is chosen
    after j1 is known. Second pickup is constant (2 piles above).
  * so every card lands exactly at its own spell length. Spectator spells,
    last letter = their card.
"""
import sys
sys.path.insert(0, '..')
from deck_sim import (make_deck, deal_into_piles, gather_position,
                      spell_name, verify)


def spell_len(card):
    return len(spell_name(card))


def build_packet():
    """8 eleven-letter and 8 twelve-letter cards, interleaved 11,11,12,12."""
    deck = make_deck()
    len11 = [c for c in deck if spell_len(c) == 11][:8]
    len12 = [c for c in deck if spell_len(c) == 12][:8]
    packet = []
    for _ in range(4):
        packet += [len11.pop(0), len11.pop(0), len12.pop(0), len12.pop(0)]
    assert len(packet) == 16
    assert all(spell_len(c) == (11 if i % 4 < 2 else 12)
               for i, c in enumerate(packet))
    return packet


def trick(deck, choices):
    d = build_packet()
    card = choices['card']
    piles = deal_into_piles(d, 4)
    j1 = next(j for j, p in enumerate(piles) if card in p)
    p0 = 1 if j1 in (0, 1) else 0        # 11-letter class -> pos 11, else 12
    d = gather_position(piles, j1, p0)
    piles = deal_into_piles(d, 4)
    j2 = next(j for j, p in enumerate(piles) if card in p)
    d = gather_position(piles, j2, 2)    # constant second pickup
    return d


def reveal_spell(final, choices):
    """Spectator deals one card per letter; card on the last letter."""
    return final[spell_len(choices['card']) - 1]


if __name__ == '__main__':
    domain = [{'card': c} for c in build_packet()]
    ok, counter = verify(trick, domain, reveal_spell)
    print(f"spell-your-own-card: {'PASS' if ok else 'FAIL'} over "
          f"{len(domain)} cases")
    if not ok:
        for ch, got, want in counter:
            print(f"  card {want} (len {spell_len(want)}): got {got}")
