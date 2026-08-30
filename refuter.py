"""refuter.py — card targeting instances + drift specimens for the refuter.

The adversarial refuter itself (Conjecture / confirmatory_verdict / refute —
the anti-drift core, the status ladder, the false-confidence delta) is
domain-agnostic and lives in lakatos/refuter.py (FRAMEWORK.md step 4). It is
re-exported here so existing callers (former_acceptance, refuter_battery) are
untouched.

This module supplies the card-specific pieces the refuter attacks over: radix
targeting over an abstract N-token packet (not tied to 52), and the __main__
drift specimens — the naive vs parity-corrected radix laws that demonstrate the
false-confidence delta (a confirmatory loop commits the naive law; the refuter
kills it at r >= 2).
"""
from lakatos.refuter import Conjecture, confirmatory_verdict, refute

from deck_sim import deal_into_piles, gather_position


# ---- generic targeting over an abstract N-token packet (not tied to 52) ------
# Theorems aren't about a 52-card deck, so the refuter tests abstract packets and
# can push scale past any physical deck. Tokens are ints 0..N-1 = start positions.

def radix_place(n, b, r, parity=True):
    """Placement sequence to send a card to 1-indexed position n, packet b**r,
    r deals into b piles. parity=True is the audited law; parity=False is the
    naive pre-correction (p_i = base-b digits of n-1, no reversal complement)."""
    x = n - 1
    digits = []
    for _ in range(r):
        digits.append(x % b)
        x //= b
    if not parity:
        return digits
    return [d if (r - 1 - i) % 2 == 0 else (b - 1) - d
            for i, d in enumerate(digits)]


def targeting_instance(b, r, parity):
    """Exhaustive ∀card ∀n test at one (b,r): does the placement rule land every
    card at every named position? Returns (ok, witness_or_None, n_cases)."""
    N = b ** r
    packet = list(range(N))
    for card in packet:
        for n in range(1, N + 1):
            d = list(packet)
            for a in radix_place(n, b, r, parity):
                piles = deal_into_piles(d, b)
                j = next(i for i, p in enumerate(piles) if card in p)
                d = gather_position(piles, j, a)
            if d[n - 1] != card:
                return False, {'b': b, 'r': r, 'card': card, 'named_n': n,
                               'got_pos': d.index(card) + 1, 'want_pos': n}, N * N
    return True, None, N * N


if __name__ == '__main__':
    # C1 — the drift specimen: the NAIVE radix law (no parity complement).
    # It coincides with the true law at r=1, so a loop that "noticed" it on
    # single-round configs would commit it. It is false for r>=2.
    c1 = Conjecture(
        name="C1  naive radix law (p_i = base-b digits of n-1)",
        claim="placements = base-b digits of n-1 send any card to position n",
        instance_test=lambda b, r: targeting_instance(b, r, parity=False),
        scale=lambda b, r: b ** r,
        inspiring=[(2, 1), (3, 1), (4, 1), (5, 1), (6, 1)],
        boundary=[(2, 2), (7, 1)],
        beyond=[(3, 2), (2, 3), (4, 2), (3, 3)],
        random_draw=[(5, 2)],
    )

    # C2 — the audited law WITH parity complement. Should survive the battery
    # but must still stop at ROBUST_CONJECTURE (this module can't prove it).
    c2 = Conjecture(
        name="C2  parity-corrected radix law",
        claim="p_i = d_i if an even # of deals follow round i, else (b-1)-d_i",
        instance_test=lambda b, r: targeting_instance(b, r, parity=True),
        scale=lambda b, r: b ** r,
        inspiring=[(3, 3), (4, 2)],                 # where the project found it
        boundary=[(2, 8), (2, 9), (10, 2)],         # deep reversal / wide base
        beyond=[(2, 4), (2, 5), (2, 6), (3, 4), (5, 3), (7, 2)],
        random_draw=[(3, 5), (4, 3), (6, 2)],
    )

    for c in (c1, c2):
        # show the lazy loop's verdict first, then the adversarial one
        committed, cc = confirmatory_verdict(c)
        print(f"\n=== {c.name.split()[0]} ===")
        print(f"   confirmatory loop (inspiring only, {cc} cases): "
              f"{'COMMIT as law' if committed else 'reject'}")
        res = refute(c)
        print(f"   FINAL STATUS: {res['status']}")
