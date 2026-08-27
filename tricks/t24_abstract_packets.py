"""Task 24 (ENGINE item 1): abstract packets — the harness past 52 cards.

verify()/verify_prop() now take a deck_factory (default: the 52-card deck,
so every existing proof script runs unchanged). This script demonstrates
the unblock: the [[general-b-radix-law]] grid extended BEYOND physical
deck sizes — including the tight fits that session 10 had to skip because
make_deck() capped N at 52.
"""
import sys
sys.path.insert(0, '..')
import importlib.util
from deck_sim import (make_packet, deal_into_piles, gather_position, verify)

spec = importlib.util.spec_from_file_location('t22', 't22_general_b_law.py')
t22 = importlib.util.module_from_spec(spec)
sys.modules['t22'] = t22
spec.loader.exec_module(t22)


def run(N, b, r):
    def trick(deck, choices):
        d = list(deck)
        card = choices['card']
        for a in t22.law_vector(choices['n'], N, b, r):
            piles = deal_into_piles(d, b)
            j = next(i for i, p in enumerate(piles) if card in p)
            d = gather_position(piles, j, a)
        return d

    domain = [{'card': c, 'n': n}
              for c in range(N) for n in range(1, N + 1)]
    return verify(trick, domain, lambda f, ch: f[ch['n'] - 1],
                  deck_factory=lambda: make_packet(N)), len(domain)


if __name__ == '__main__':
    grid = [(64, 8, 3),    # the config session 10 could not test (tight)
            (81, 9, 3),    # tight: 9^2 = 81
            (81, 3, 5),    # tight: 3^4 = 81 — deepest base-3 packet
            (100, 10, 3),  # tight: 10^2 = 100
            (144, 12, 3)]  # tight: 12^2 = 144
    total, all_ok = 0, True
    for N, b, r in grid:
        assert b ** (r - 1) >= N
        t22.check_round_formula(N, b)
        (ok, counter), cases = run(N, b, r)
        total += cases
        all_ok &= ok
        print(f"  N={N:3d} b={b:2d} r={r}: {'PASS' if ok else 'FAIL'} over "
              f"{cases} cases [tight]"
              + (f"  e.g. {counter[:2]}" if not ok else ""))
    print(f"ABSTRACT-PACKET EXTENSION "
          f"{'VERIFIED' if all_ok else 'REFUTED'} ({total} cases, "
          f"N up to 144 — beyond any physical deck)")
