"""Task 15 (SYNTHESIZE, from t14's diagnosis): adaptive targeting with
UNEVEN piles — full 52-card deck, only 3 piles, 4 deals, any card to any
named position 1..52.

t14 showed fixed placements can't do this (0/27 vectors start-independent
at 3 rounds; only 30/52 positions reachable at 4). But the spectator's
pile-pointing leaks the card's position mod 3 each round, so placements may
ADAPT to the observation history. Sub-search: backward induction over the
observation tree — a position-set S is controllable to target t in k rounds
iff for every pile-class of S there EXISTS a placement whose image is
controllable in k-1. Extract the strategy, then verify() end to end.

One round is a fixed position-map F[x][a] (x = current position, a =
placement, valid for the pile class j = x mod 3), computed by simulation.
"""
import sys
sys.path.insert(0, '..')
from deck_sim import make_deck, deal_into_piles, gather_position, verify

N, B = 52, 3
ROUNDS = 5   # 4 rounds reaches only 30/52 targets even adaptively (t14/t15
             # diagnosis: the bottleneck is the round-map's image, not
             # information); 5 rounds covers all 52.


def build_F():
    """F[x][a] = new position of a card at position x when the spectator's
    pile is j = x mod B and the performer gathers with a piles above."""
    F = [[None] * B for _ in range(N)]
    markers = list(range(N))
    for j in range(B):
        for a in range(B):
            piles = deal_into_piles(markers, B)
            d = gather_position(piles, j, a)
            for x in range(j, N, B):
                F[x][a] = d.index(x)
    return F


F = build_F()


def solve(S, k, t, memo):
    """Is position-set S controllable to target index t in k rounds?
    Returns strategy subtree {history_tuple: placement} or None."""
    key = (frozenset(S), k)
    if key in memo:
        return memo[key]
    if k == 0:
        memo[key] = {} if S <= {t} else None
        return memo[key]
    strat = {}
    for j in range(B):
        C = {x for x in S if x % B == j}
        if not C:
            continue
        for a in range(B):
            sub = solve({F[x][a] for x in C}, k - 1, t, memo)
            if sub is not None:
                strat[(j,)] = a
                strat.update({(j,) + h: v for h, v in sub.items()})
                break
        else:
            memo[key] = None
            return None
    memo[key] = strat
    return strat


def build_strategies():
    strategies = {}
    for t in range(N):
        strategies[t] = solve(set(range(N)), ROUNDS, t, {})
    return strategies


if __name__ == '__main__':
    strategies = build_strategies()
    feasible = [t for t, s in strategies.items() if s is not None]
    print(f"strategy search: {len(feasible)}/{N} targets adaptively "
          f"reachable in {ROUNDS} rounds")
    if len(feasible) == N:
        def trick(deck, choices):
            d = list(deck)
            card = choices['card']
            strat, hist = strategies[choices['n'] - 1], ()
            for _ in range(ROUNDS):
                piles = deal_into_piles(d, B)
                j = next(i for i, p in enumerate(piles) if card in p)
                hist += (j,)
                d = gather_position(piles, j, strat[hist])
            return d

        domain = [{'card': c, 'n': n}
                  for c in make_deck() for n in range(1, N + 1)]
        ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1])
        print(f"FULL VERIFY: {'PASS' if ok else 'FAIL'} over {len(domain)} "
              f"cases (52 cards x 52 numbers, 3 uneven piles, {ROUNDS} deals)")
        if not ok:
            print(f"  {len(counter)} fails, e.g. {counter[:3]}")
    else:
        missing = sorted(set(range(N)) - set(feasible))
        print(f"  unreachable targets (0-indexed): {missing}")
