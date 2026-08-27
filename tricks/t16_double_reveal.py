"""Task 16 (SYNTHESIZE): DOUBLE REVEAL — two spectators each think of a
card; each round both point at the pile holding theirs; the performer
gathers with one pile ordering that must serve both. Goal: both cards to
known positions (A's on top, B's on bottom).

Part A (obstruction, even piles, N=27, b=3): hypothesis — two cards in one
pile are forced to EQUAL new digits, cards in different piles to DISTINCT
ones (pile levels are a bijection), so the number of base-3 digit positions
where the two cards' positions agree is CONSERVED by every strategy.
Test: full-information backward reachability over the 702-pair product
space, for ALL 702 ordered target pairs, at 3..5 rounds.

Part B (uneven piles, N=52, b=3, piles 18/17/17): does unevenness dissolve
the obstruction? Backward reachability for target (top, bottom), minimum
rounds for universal reachability, then an OBSERVATION-CONSTRAINED adaptive
strategy (t15's backward induction lifted to the pair space), then full
end-to-end verify() over every ordered pair of distinct cards.
"""
import sys
sys.path.insert(0, '..')
from itertools import permutations
from deck_sim import make_deck, deal_into_piles, gather_order, verify

PERMS = list(permutations(range(3)))


def build_G(n):
    """G[x][s] = new position of the card at position x when the 3 piles
    are gathered in ordering PERMS[s]."""
    markers = list(range(n))
    G = [[None] * len(PERMS) for _ in range(n)]
    for s, order in enumerate(PERMS):
        d = gather_order(deal_into_piles(markers, 3), list(order))
        for new_pos, x in enumerate(d):
            G[x][s] = new_pos
    return G


def back_reach(G, n, target, rounds):
    """Pairs that can reach `target` (ordered pair) in `rounds` rounds under
    FULL information (per-pair free choice of ordering each round)."""
    B = {target}
    for _ in range(rounds):
        B = {(x, y)
             for x in range(n) for y in range(n) if x != y
             if any((G[x][s], G[y][s]) in B for s in range(len(PERMS)))}
    return B


def digits3(x):
    return (x % 3, (x // 3) % 3, x // 9)


def agree_pattern(x, y):
    return tuple(a == b for a, b in zip(digits3(x), digits3(y)))


def solve(S, k, t, G, memo):
    """Observation-constrained strategy: S controllable to pair t in k
    rounds iff every (pileA, pileB) class of S has an ordering whose image
    is controllable in k-1. Returns {history: ordering_index} or None."""
    key = (frozenset(S), k)
    if key in memo:
        return memo[key]
    if k == 0:
        memo[key] = {} if S <= {t} else None
        return memo[key]
    strat = {}
    for ja in range(3):
        for jb in range(3):
            C = {(x, y) for (x, y) in S if x % 3 == ja and y % 3 == jb}
            if not C:
                continue
            for s in range(len(PERMS)):
                sub = solve({(G[x][s], G[y][s]) for (x, y) in C},
                            k - 1, t, G, memo)
                if sub is not None:
                    strat[((ja, jb),)] = s
                    strat.update({((ja, jb),) + h: v
                                  for h, v in sub.items()})
                    break
            else:
                memo[key] = None
                return None
    memo[key] = strat
    return strat


def part_a():
    n = 27
    G = build_G(n)
    all_pairs = {(x, y) for x in range(n) for y in range(n) if x != y}
    print(f"Part A: even piles, N={n}: testing conservation over all "
          f"{n * (n - 1)} ordered target pairs")
    for rounds in (3, 4, 5):
        exact_pattern = 0
        count_conserved = 0
        violations = 0
        for tx in range(n):
            for ty in range(n):
                if tx == ty:
                    continue
                B = back_reach(G, n, (tx, ty), rounds)
                t_count = sum(agree_pattern(tx, ty))
                counts_ok = all(sum(agree_pattern(x, y)) == t_count
                                for x, y in B)
                patterns = {agree_pattern(x, y) for x, y in B}
                if counts_ok and len(patterns) == 1:
                    exact_pattern += 1
                elif counts_ok:
                    count_conserved += 1
                else:
                    violations += 1
        print(f"  rounds={rounds}: of {n * (n - 1)} targets — "
              f"{exact_pattern} reachable from exactly one agreement "
              f"pattern, {count_conserved} from same-count patterns only, "
              f"{violations} CONSERVATION VIOLATIONS")
    return G


def part_b():
    n = 52
    G = build_G(n)
    target = (0, n - 1)                      # A's card top, B's bottom
    all_pairs = {(x, y) for x in range(n) for y in range(n) if x != y}
    print(f"Part B: uneven piles, N={n} (18/17/17), target = top & bottom")
    min_r = None
    for rounds in range(1, 9):
        B = back_reach(G, n, target, rounds)
        print(f"  rounds={rounds}: {len(B)}/{len(all_pairs)} start pairs "
              f"can reach the target (full information)")
        if B == all_pairs:
            min_r = rounds
            break
    if min_r is None:
        print("  not universally reachable within 8 rounds — stopping")
        return
    for rounds in range(min_r, min_r + 3):
        strat = solve(all_pairs, rounds, target, G, {})
        print(f"  adaptive strategy at rounds={rounds}: "
              f"{'FOUND' if strat is not None else 'none (info-limited)'}")
        if strat is None:
            continue

        def trick(deck, choices, strat=strat, rounds=rounds):
            d = list(deck)
            ca, cb = choices['a'], choices['b']
            hist = ()
            for _ in range(rounds):
                piles = deal_into_piles(d, 3)
                ja = next(i for i, p in enumerate(piles) if ca in p)
                jb = next(i for i, p in enumerate(piles) if cb in p)
                hist += ((ja, jb),)
                d = gather_order(piles, list(PERMS[strat[hist]]))
            return d

        deck = make_deck()
        pairs = [(a, b) for a in deck for b in deck if a != b]
        dom_a = [{'card': a, 'a': a, 'b': b} for a, b in pairs]
        dom_b = [{'card': b, 'a': a, 'b': b} for a, b in pairs]
        ok_a, ca_ = verify(trick, dom_a, lambda f, ch: f[0])
        ok_b, cb_ = verify(trick, dom_b, lambda f, ch: f[-1])
        print(f"  FULL VERIFY (A on top):    "
              f"{'PASS' if ok_a else 'FAIL'} over {len(dom_a)} pairs")
        print(f"  FULL VERIFY (B on bottom): "
              f"{'PASS' if ok_b else 'FAIL'} over {len(dom_b)} pairs")
        if not ok_a:
            print(f"    e.g. {ca_[:2]}")
        if not ok_b:
            print(f"    e.g. {cb_[:2]}")
        break


if __name__ == '__main__':
    part_a()
    part_b()
