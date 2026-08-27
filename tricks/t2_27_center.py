"""Task 2 (MUTATE): 21-card trick -> 27 cards, 3 piles of 9, 3 middle-gathers.
Hypothesis: card converges to dead center (index 13 of 27) for every start.
Also probe the failure boundary: same procedure at other packet sizes."""
import sys
sys.path.insert(0, '..')
from deck_sim import make_deck, deal_into_piles, gather_middle, verify


def middle_gather_trick(n, rounds):
    def trick(deck, choices):
        d = deck[:n]
        card = choices['card']
        for _ in range(rounds):
            piles = deal_into_piles(d, 3)
            chosen_pile = next(j for j, p in enumerate(piles) if card in p)
            d = gather_middle(piles, chosen_pile)
        return d
    return trick


def run(n, rounds):
    domain = [{'card': c} for c in make_deck()[:n]]
    center = (n - 1) // 2
    ok, counter = verify(middle_gather_trick(n, rounds), domain,
                         lambda final, ch: final[center])
    return ok, counter, len(domain), center


if __name__ == '__main__':
    ok, counter, cases, center = run(27, 3)
    print(f"27 cards, 3 rounds -> center idx {center}: "
          f"{'PASS' if ok else 'FAIL'} over {cases} cases")
    if not ok:
        print(f"  {len(counter)} fails, e.g. {counter[:3]}")
    # failure boundary probe: which (n, rounds) combos converge to center?
    for n in (9, 15, 21, 27, 33, 39, 45, 51):
        for r in (2, 3, 4):
            okk, cc, _, _ = run(n, r)
            if okk:
                print(f"  boundary: n={n} rounds={r} -> center PASS")
                break
        else:
            print(f"  boundary: n={n} -> no center convergence by 4 rounds "
                  f"({len(cc)} fails at r=4)")
