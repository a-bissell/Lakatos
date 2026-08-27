"""Task 18 (REFINE, discovered by the session-6 oracle audit): FIXED-VECTOR
ACAAN on the full deck with 3 uneven piles — t15 without the machinery.

t14 proved fixed relative placements fail at 3 rounds (0/27 vectors
start-independent) and cover only 30/52 targets at 4; t15 then reached for
observation-adaptive strategy trees at 5 rounds WITHOUT checking fixed
vectors at 5. The audit checked: at r=5 they cover ALL 52 targets.

The trick: spectator thinks of any card, names any position 1..52. Five
times: deal 52 cards into 3 piles (18/17/17), spectator points, performer
gathers with a fixed number of piles above the pointed pile — the 5-vector
depends only on the named position. Card lands at position n. 10 steps,
memorizable per target from a 52-row crib (closed form: open, queued).
"""
import sys
sys.path.insert(0, '..')
import importlib.util
from itertools import product
from deck_sim import make_deck, deal_into_piles, gather_position, verify

spec = importlib.util.spec_from_file_location('t15mod',
                                              't15_uneven_adaptive.py')
t15 = importlib.util.module_from_spec(spec)
sys.modules['t15mod'] = t15
spec.loader.exec_module(t15)


def fixed_vectors():
    """One start-independent 5-vector per reachable target index."""
    out = {}
    for vec in product(range(3), repeat=5):
        finals = set()
        for x in range(52):
            pos = x
            for a in vec:
                pos = t15.F[pos][a]
            finals.add(pos)
        if len(finals) == 1:
            out.setdefault(finals.pop(), vec)
    return out


if __name__ == '__main__':
    vectors = fixed_vectors()
    print(f"start-independent fixed 5-vectors reach {len(vectors)}/52 targets")

    def trick(deck, choices):
        d = deck[:52]
        card = choices['card']
        for a in vectors[choices['n'] - 1]:
            piles = deal_into_piles(d, 3)
            j = next(i for i, p in enumerate(piles) if card in p)
            d = gather_position(piles, j, a)
        return d

    domain = [{'card': c, 'n': n} for c in make_deck() for n in range(1, 53)]
    ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1])
    print(f"FIXED-VECTOR ACAAN: {'PASS' if ok else 'FAIL'} over "
          f"{len(domain)} cases (52 cards x 52 positions, 5 deals)")
    if not ok:
        print(f"  fails e.g. {counter[:3]}")
    else:
        print("crib (position n -> 5-vector of piles-above):")
        for idx in sorted(vectors):
            print(f"  n={idx + 1:2d}: {''.join(map(str, vectors[idx]))}",
                  end='\n' if idx % 4 == 3 else '   ')
        print()
