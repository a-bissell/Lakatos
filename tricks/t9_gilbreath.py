"""Task 9 (COMPOSE, new op class): the Gilbreath principle — the spectator
RIFFLE-SHUFFLES and the effect still works.

Procedure under test: deck stacked cyclically with period k. Spectator deals
off any m cards into a pile (dealing reverses them), then riffles that pile
into the rest ANY way they like. Claimed invariant: every successive block
of k cards from the top contains one card of each of the k classes.

Free-choice domain (exhaustive): every deal-off size m in 0..N AND every
possible interleaving pattern — sum over m of C(N, m) = 2^N cases.
  * 1st Gilbreath: k=2 (alternating red/black), N=12 -> 4096 cases
  * 2nd Gilbreath: k=4 (repeating suit cycle),  N=12 -> 4096 cases
  * size probe at N=16 for both -> 65536 cases each
Verified with verify_prop (property harness, unit-checked in deck_sim).
"""
import sys
sys.path.insert(0, '..')
from itertools import product
from deck_sim import deal_pile, riffle_merge, verify_prop, SUITS


def cyclic_stack(n, k):
    """n-card deck cycling through k classes; card = (class, serial)."""
    return [(i % k, i) for i in range(n)]


def gilbreath_shuffle(deck, choices):
    pile, rest = deal_pile(deck, choices['m'])   # dealing reverses the pile
    return riffle_merge(pile, rest, choices['pattern'])


def blocks_complete(final, k):
    for i in range(0, len(final), k):
        if {c[0] for c in final[i:i + k]} != set(range(k)):
            return False
    return True


def run(n, k):
    domain = [{'m': pattern.count(0), 'pattern': list(pattern)}
              for pattern in product((0, 1), repeat=n)]
    # pattern zeros pull from the dealt pile of size m: enumerate all
    # (m, interleaving) pairs at once as all 0/1 strings of length n.
    def trick(deck, choices):
        return gilbreath_shuffle(cyclic_stack(n, k), choices)

    ok, counter = verify_prop(trick, domain,
                              lambda f, ch: blocks_complete(f, k))
    return ok, counter, len(domain)


if __name__ == '__main__':
    all_ok = True
    for n, k, label in [(12, 2, '1st Gilbreath (red/black pairs)'),
                        (12, 4, '2nd Gilbreath (suit quartets)'),
                        (16, 2, '1st Gilbreath, size probe'),
                        (16, 4, '2nd Gilbreath, size probe')]:
        ok, counter, cases = run(n, k)
        all_ok &= ok
        print(f"{label}: N={n} k={k}: {'PASS' if ok else 'FAIL'} over "
              f"{cases} cases (all deal-off sizes x all riffles)")
        if not ok:
            ch, f = counter[0]
            print(f"  e.g. m={ch['m']} pattern={ch['pattern']} -> {f}")
    print("GILBREATH " + ("VERIFIED" if all_ok else "REFUTED"))
