"""Task 17 (REFINE double-reveal-uneven): a PERFORMABLE small-deck double
reveal. Two spectators think of cards from an N-card packet; each round the
packet is dealt into b piles, both spectators point at their pile, the
performer stacks the piles; after r rounds A's card is on TOP and B's on
the BOTTOM.

Performability targets: 2r <= 12 steps, and a REACTIVE strategy — the
pickup order depends only on (round, pile A points at, pile B points at),
never on history — so the performer needs one small lookup table.

Pipeline:
  1. sweep uneven (N, b) configs for the minimum rounds at which the
     top/bottom target is universally reachable with full information;
  2. on shortlisted configs, find the minimum ADAPTIVE (history-tree)
     rounds — the info-constrained floor;
  3. search for a reactive strategy at that floor (and +1): greedy per
     observation class, choosing actions that keep every image pair within
     the full-info distance budget (admissible prune), randomized restarts;
  4. full end-to-end verify() (both reveals) of the reactive trick.
"""
import sys

sys.path.insert(0, '..')
from itertools import permutations
from deck_sim import make_deck, deal_into_piles, gather_order, verify

PERMS = {b: list(permutations(range(b))) for b in (2, 3, 4)}


def build_G(n, b):
    markers = list(range(n))
    G = [[None] * len(PERMS[b]) for _ in range(n)]
    for s, order in enumerate(PERMS[b]):
        d = gather_order(deal_into_piles(markers, b), list(order))
        for new_pos, x in enumerate(d):
            G[x][s] = new_pos
    return G


def all_pairs(n):
    return {(x, y) for x in range(n) for y in range(n) if x != y}


def distance_map(G, n, b, target, cap):
    """D[(x,y)] = min rounds to reach target with full information."""
    D = {target: 0}
    for r in range(1, cap + 1):
        frontier = {(x, y) for (x, y) in all_pairs(n) if (x, y) not in D
                    and any((G[x][s], G[y][s]) in D
                            for s in range(len(PERMS[b])))}
        for p in frontier:
            D[p] = r
        if not frontier:
            break
    return D


def solve(S, k, t, G, b, memo):
    key = (frozenset(S), k)
    if key in memo:
        return memo[key]
    if k == 0:
        memo[key] = {} if S <= {t} else None
        return memo[key]
    strat = {}
    for ja in range(b):
        for jb in range(b):
            C = {(x, y) for (x, y) in S if x % b == ja and y % b == jb}
            if not C:
                continue
            for s in range(len(PERMS[b])):
                sub = solve({(G[x][s], G[y][s]) for (x, y) in C},
                            k - 1, t, G, b, memo)
                if sub is not None:
                    strat[((ja, jb),)] = s
                    strat.update({((ja, jb),) + h: v for h, v in sub.items()})
                    break
            else:
                memo[key] = None
                return None
    memo[key] = strat
    return strat


class LCG:
    """Tiny deterministic PRNG (avoids stdlib random; reproducible runs)."""

    def __init__(self, seed):
        self.state = seed & 0xFFFFFFFF

    def random(self):
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state / 0x80000000


def reactive_search(G, n, b, target, rounds, D, tries=3000, seed=1):
    """Find per-round tables f[r][(ja,jb)] -> ordering index such that ALL
    pairs reach target. Greedy with admissible prune + random restarts."""
    rng = LCG(seed)
    acts = list(range(len(PERMS[b])))
    for _ in range(tries):
        S = all_pairs(n)
        tables = []
        ok = True
        for r in range(rounds):
            remaining = rounds - r - 1
            table = {}
            classes = {}
            for (x, y) in S:
                classes.setdefault((x % b, y % b), set()).add((x, y))
            nxt = set()
            for obs, C in classes.items():
                candidates = []
                for s in acts:
                    img = {(G[x][s], G[y][s]) for (x, y) in C}
                    if all(D.get(p, 99) <= remaining for p in img):
                        candidates.append((sum(D[p] for p in img),
                                           len(img), rng.random(), s, img))
                if not candidates:
                    ok = False
                    break
                candidates.sort()
                _, _, _, s, img = candidates[0]
                table[obs] = s
                nxt |= img
            if not ok:
                break
            tables.append(table)
            S = nxt
        if ok and S == {target}:
            return tables
    return None


def sweep():
    print("Sweep: min FULL-INFO rounds to make top/bottom universally "
          "reachable (cap 6; '-' = not within cap; only uneven N)")
    results = {}
    for b in (2, 3, 4):
        for n in range(8, 22):
            if n % b == 0:
                continue
            G = build_G(n, b)
            target = (0, n - 1)
            D = distance_map(G, n, b, target, 6)
            r = max(D.values()) if len(D) == n * (n - 1) else None
            results[(n, b)] = (r, G, D)
        line = ', '.join(f"N={n}:{results[(n, b)][0] or '-'}"
                         for n in range(8, 22) if n % b != 0)
        print(f"  b={b}: {line}")
    return results


if __name__ == '__main__':
    results = sweep()
    ranked = sorted(((r, b, n) for (n, b), (r, _, _) in results.items()
                     if r is not None), key=lambda t: (t[0], t[1], t[2]))
    print("\nShortlist (rounds, piles, N):", ranked[:6])
    for r_full, b, n in ranked[:6]:
        _, G, D = results[(n, b)]
        target = (0, n - 1)
        for rounds in (r_full, r_full + 1):
            if 2 * rounds > 12:
                continue
            adaptive = solve(all_pairs(n), rounds, target, G, b, {})
            tag = f"N={n} b={b} rounds={rounds} ({2 * rounds} steps)"
            if adaptive is None:
                print(f"  {tag}: adaptive tree impossible (info-limited)")
                continue
            react = reactive_search(G, n, b, target, rounds, D)
            print(f"  {tag}: adaptive tree EXISTS "
                  f"({len(adaptive)} nodes); reactive table "
                  f"{'FOUND' if react else 'not found'}")
            if react:
                def trick(deck, choices, react=react, n=n, b=b):
                    d = deck[:n]
                    ca, cb = choices['a'], choices['b']
                    for table in react:
                        piles = deal_into_piles(d, b)
                        ja = next(i for i, p in enumerate(piles) if ca in p)
                        jb = next(i for i, p in enumerate(piles) if cb in p)
                        d = gather_order(piles, list(PERMS[b][table[(ja, jb)]]))
                    return d

                deck_n = make_deck()[:n]
                pairs = [(a_, b_) for a_ in deck_n for b_ in deck_n
                         if a_ != b_]
                dom_a = [{'card': a_, 'a': a_, 'b': b_} for a_, b_ in pairs]
                dom_b = [{'card': b_, 'a': a_, 'b': b_} for a_, b_ in pairs]
                ok_a, _ = verify(trick, dom_a, lambda f, ch: f[0])
                ok_b, _ = verify(trick, dom_b, lambda f, ch: f[-1])
                print(f"    FULL VERIFY: A-top {'PASS' if ok_a else 'FAIL'}"
                      f", B-bottom {'PASS' if ok_b else 'FAIL'} over "
                      f"{len(pairs)} ordered pairs")
                print("    reactive tables (round: (pileA,pileB)->ordering):")
                for ri, table in enumerate(react):
                    rows = ', '.join(
                        f"{obs}->{''.join(map(str, PERMS[b][s]))}"
                        for obs, s in sorted(table.items()))
                    print(f"      round {ri + 1}: {rows}")
                sys.exit(0)
    print("no reactive config found in shortlist")
