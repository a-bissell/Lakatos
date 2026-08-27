"""Task 19 (REFINE, queue item 1): CLOSED FORM for the fixed-vector ACAAN
crib — and its generalization to every deck size N ≡ 1 (mod 3).

Derivation (verified below, never trusted):
  One round "deal N into 3 piles, gather with a piles above the pointed
  pile" acts on a card's position x as
      x' = A(a, x mod 3) - floor(x/3)
  and for N ≡ 1 (mod 3), with s = (N-1)/3 (the small pile size):
      a=0:  A = s   if x ≡ 0 (mod 3), else s-1
      a=1:  A = 2s          (SAME for every pile — the N≡1 coincidence)
      a=2:  A = N-1         (same for every pile)
  Propagating the requirement interval backwards through r rounds tracks
  only its midpoint m:  m <- K_a - 3m,  K = (N-2, 2N-1, 3N-2).
  Centered on the deck, y = m - (N-1)/2, this is the ALTERNATING-RADIX law:
      y <- -3y + a'*N + [a'=0],   a' = a-1 in {-1,0,+1}
  Digit rule (no ties possible when N ≡ 1 mod 3): a' = round(3y/N).
  Digits come out last-pickup-first; reverse for performance order.
  Rounds needed: 3^(r-1) >= ceil(N/3).

The 52-card crib in t18 is this law's output; here the law itself is
verified end-to-end at N = 10, 13, 22, 40, 52.
"""
import sys
sys.path.insert(0, '..')
from deck_sim import make_deck, deal_into_piles, gather_position, verify


def check_round_formula(N):
    """Verify the one-round position map formula against the simulator."""
    s = (N - 1) // 3
    markers = list(range(N))
    for x in range(N):
        j = x % 3
        for a in range(3):
            d = gather_position(deal_into_piles(markers, 3), j, a)
            got = d.index(x)
            if a == 0:
                A = s if j == 0 else s - 1
            elif a == 1:
                A = 2 * s
            else:
                A = N - 1
            want = A - x // 3
            assert got == want, (N, x, a, got, want)
    return True


def law_vector(n, N, r):
    """Pickup vector (performance order) sending every card to position n."""
    y = (n - 1) - (N - 1) / 2
    digits = []                          # computed last-pickup-first
    for _ in range(r):
        ap = round(3 * y / N)
        ap = max(-1, min(1, ap))
        y = -3 * y + ap * N + (1 if ap == 0 else 0)
        digits.append(ap + 1)
    return list(reversed(digits))


def run(N, r):
    def trick(deck, choices):
        d = deck[:N]
        card = choices['card']
        for a in law_vector(choices['n'], N, r):
            piles = deal_into_piles(d, 3)
            j = next(i for i, p in enumerate(piles) if card in p)
            d = gather_position(piles, j, a)
        return d

    domain = [{'card': c, 'n': n}
              for c in make_deck()[:N] for n in range(1, N + 1)]
    return verify(trick, domain, lambda f, ch: f[ch['n'] - 1]), len(domain)


def enumerate_reachable(N, r):
    """Targets reachable by ANY start-independent fixed vector at (N, r)."""
    from itertools import product
    markers = list(range(N))
    perm = {}
    for a in range(3):
        for j in range(3):
            d = gather_position(deal_into_piles(markers, 3), j, a)
            for newpos, x in enumerate(d):
                if x % 3 == j:
                    perm[(x, a)] = newpos
    reach = set()
    for vec in product(range(3), repeat=r):
        finals = set()
        for x in range(N):
            pos = x
            for a in vec:
                pos = perm[(pos, a)]
            finals.add(pos)
        if len(finals) == 1:
            reach.add(finals.pop())
    return reach


if __name__ == '__main__':
    Ns = (7, 10, 13, 16, 22, 25, 31, 40, 49, 52)
    for N in Ns:
        assert N % 3 == 1
        check_round_formula(N)
    print(f"round-map formula: verified against simulator for N in {Ns} "
          f"(every position x every placement)")

    # validity condition for the greedy law: 3^(r-1) >= N.
    # Configs below the line are PREDICTED to fail (greedy drift can
    # exceed the slack); configs above it must all pass.
    print("\nwithin validity condition 3^(r-1) >= N:")
    all_ok = True
    for N, r in ((7, 3), (10, 4), (13, 4), (16, 4), (22, 4), (25, 4),
                 (31, 5), (40, 5), (49, 5), (52, 5)):
        assert 3 ** (r - 1) >= N
        (ok, counter), cases = run(N, r)
        all_ok &= ok
        print(f"  N={N:2d} r={r}: {'PASS' if ok else 'FAIL'} over "
              f"{cases} cases" + (f"  e.g. {counter[:2]}" if not ok else ""))
    print("ALTERNATING-RADIX LAW " +
          ("VERIFIED across all in-condition configs" if all_ok
           else "REFUTED"))

    print("\noutside the condition (3^(r-1) < N — failure predicted):")
    for N, r in ((10, 3), (13, 3)):
        (ok, counter), cases = run(N, r)
        reach = enumerate_reachable(N, r)
        print(f"  N={N:2d} r={r}: greedy law {'PASS' if ok else 'FAIL'} "
              f"(predicted FAIL); exhaustive search: {len(reach)}/{N} "
              f"targets reachable by ANY fixed vector")

    v20 = ''.join(map(str, law_vector(20, 52, 5)))
    print(f"\nexample: n=20 on 52 cards -> vector {v20}")
