"""Task 23 (REFINE): exact BUCKET RULE for the six-pile, three-deal
full-deck ACAAN (b=6, N=52, r=3 instance of [[general-b-radix-law]]).

The argmin digit choice compares six candidates -6z + t_a with
t = (-260, -152, -44, +64, +164, +260) (offsets (2a-5)*52 + 2*corr,
corr = (0,2,4,6,4,0)). Since t is increasing, digit boundaries sit at
6z = (t_a + t_{a+1})/2 = (-206, -98, 10, 114, 212). Only 114 is divisible
by 6, so z = 19 is the ONE possible tie; the law's tie-break (larger
digit) assigns it digit 4. Exact integer bucket rule:

    z <= -35 -> 0 | -34..-17 -> 1 | -16..1 -> 2 | 2..18 -> 3 |
    19..35 -> 4 | z >= 36 -> 5,     then z <- -6z + t_digit
(the first draft of THRESH below was off by one at the two lowest
boundaries; the argmin-equivalence assert caught it)

Verified three ways below: threshold derivation, bucket == tie-broken
argmin for every integer z in a generous range, and the full trick over
all 2,704 (card, n) cases using ONLY the bucket rule.
"""
import sys
sys.path.insert(0, '..')
from deck_sim import make_deck, deal_into_piles, gather_position, verify

T = (-260, -152, -44, 64, 164, 260)          # candidate offsets, b=6 N=52
THRESH = (-34, -16, 2, 19, 36)               # first z of each bucket 1..5


def argmin_digit(z):
    return sorted((abs(-6 * z + T[a]), -a, a) for a in range(6))[0][2]


def bucket_digit(z):
    a = 0
    for th in THRESH:
        if z >= th:
            a += 1
    return a


def bucket_vector(n, r=3):
    z = 2 * n - 53
    digits = []
    for _ in range(r):
        a = bucket_digit(z)
        digits.append(a)
        z = -6 * z + T[a]
    return list(reversed(digits))


if __name__ == '__main__':
    # 1. thresholds follow from the midpoints
    mids = [(T[a] + T[a + 1]) / 2 for a in range(5)]
    assert mids == [-206, -98, 10, 114, 212]
    ties = [m for m in mids if (m / 6) == int(m / 6)]
    assert ties == [114], ties
    print(f"midpoints {mids}; only 6z = 114 (z = 19) can tie -> digit 4 "
          f"by the law's tie-break")

    # 2. bucket rule == tie-broken argmin on every integer in range
    bad = [z for z in range(-400, 401) if bucket_digit(z) != argmin_digit(z)]
    assert not bad, bad[:5]
    print("bucket rule == argmin for every integer z in [-400, 400]")

    # 3. the tie point in practice
    hit = []
    for n in range(1, 53):
        z = 2 * n - 53
        for _ in range(3):
            if z == 19:
                hit.append(n)
            z = -6 * z + T[bucket_digit(z)]
    print(f"z = 19 occurs during the traces for n = {hit if hit else 'none'}")

    # 4. end-to-end verification using ONLY the bucket rule
    def trick(deck, choices):
        d = deck[:52]
        card = choices['card']
        for a in bucket_vector(choices['n']):
            piles = deal_into_piles(d, 6)
            j = next(i for i, p in enumerate(piles) if card in p)
            d = gather_position(piles, j, a)
        return d

    domain = [{'card': c, 'n': n} for c in make_deck() for n in range(1, 53)]
    ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1])
    print(f"FULL VERIFY (bucket rule only): {'PASS' if ok else 'FAIL'} "
          f"over {len(domain)} cases")
    if not ok:
        print(f"  e.g. {counter[:3]}")
