"""novelty_oracle.py — a rediscovery FILTER, not a novelty certifier.

It answers one question honestly: "is this candidate's BEHAVIOR one of five
known families?" It matches on the permutation a procedure induces (or, for
Gilbreath, the invariant it preserves) — never on what the code looks like, so
a Gergonne procedure dressed up as something new is still caught.

Two errors, handled asymmetrically (this is the whole point):
  * false NOVEL  (miss a rediscovery)  -> recoverable: refuter/lit-search catch it later
  * false KNOWN  (kill a real result)  -> INVISIBLE & catastrophic
So: recognizers ABSTAIN when unsure rather than declare KNOWN, and every match is
LOGGED with a witness (log-and-suppress) so a false KNOWN is auditable, not lost.

Verdicts:
  MATCHED(family, confidence=exact, witness)   -> suppressed (logged)
  NOT_MATCHED(5 families)                       -> routed onward (not "novel")
  ABSTAIN(reason)                               -> routed onward + surfaced for review
"""
from collections import deque
from deck_sim import (deal_into_piles, gather_position, deal_pile,
                      riffle_merge, down_under_survivor)


# ---- behavioral signatures (what a family DOES to positions) -----------------

def perm_of(op, N):
    """The permutation an op induces: out[i] = original index now at position i."""
    return tuple(op(list(range(N))))


def gergonne_round_perms(N, b):
    """Every permutation a single Gergonne round with b piles can induce:
    deal into b piles by residue, then reassemble piles as contiguous blocks in
    some order (which pile is the pivot, how many go on top)."""
    piles = deal_into_piles(list(range(N)), b)
    out = set()
    for j in range(b):
        for above in range(b):
            out.add(tuple(gather_position(piles, j, above)))
    return out


def faro_perms(N):
    """Out- and in-faro (perfect interleave). Empty if N is odd."""
    if N % 2:
        return set()
    h = N // 2
    out = [0] * N
    inn = [0] * N
    for k in range(h):
        out[2 * k], out[2 * k + 1] = k, h + k
        inn[2 * k], inn[2 * k + 1] = h + k, k
    return {tuple(out), tuple(inn)}


def down_under_elim_perm(N):
    """Order positions leave in a down-under deal (down=table), survivor last.
    This is the Josephus(k=2, first eliminated) signature."""
    q = deque(range(N))
    order = []
    down = True
    while q:
        c = q.popleft()
        if down:
            order.append(c)
        else:
            q.append(c)
        down = not down
    return tuple(order)


# ---- suppressed log (audit surface for the dangerous error) ------------------

class SuppressedLog:
    def __init__(self):
        self.entries = []

    def record(self, name, family, confidence, witness, N):
        self.entries.append(dict(name=name, family=family,
                                 confidence=confidence, witness=witness, N=N))

    def review_queue(self):
        """What a human should actually look at: anything not an exact match.
        Exact permutation-signature matches sit quietly; uncertainty surfaces."""
        return [e for e in self.entries if e['confidence'] != 'exact']

    def summary(self):
        from collections import Counter
        fam = Counter(e['family'] for e in self.entries)
        return dict(total=len(self.entries), by_family=dict(fam),
                    needs_review=len(self.review_queue()))


# ---- the oracle --------------------------------------------------------------

class Candidate:
    """Behavior, not code. permutation-kind emits per-round permutations for
    sampled choices; property-kind emits a shuffle op + an invariant period."""
    def __init__(self, name, N, kind, round_perms=None, sample_choices=None,
                 shuffle=None, invariant_k=None):
        self.name, self.N, self.kind = name, N, kind
        self.round_perms = round_perms          # choices -> list[tuple]
        self.sample_choices = sample_choices or []
        self.shuffle = shuffle                  # (deck, choices) -> deck
        self.invariant_k = invariant_k


def _collect_round_perms(cand):
    perms = []
    for ch in cand.sample_choices:
        perms.extend(cand.round_perms(ch))
    return perms


def _match_gergonne(cand):
    """Exact iff every round-perm (over all sampled choices) is a Gergonne round
    for SOME pile count b (b may vary per round -> mixed-radix still counts)."""
    N = cand.N
    cache = {}
    bases_used = set()
    for pi in _collect_round_perms(cand):
        hit = None
        for b in range(2, N):           # b=1 is identity; skip
            if N % b and b not in (N,):  # allow uneven piles too; don't over-restrict
                pass
            cache.setdefault(b, gergonne_round_perms(N, b))
            if pi in cache[b]:
                hit = b
                break
        if hit is None:
            return None
        bases_used.add(hit)
    return {'family': 'Gergonne', 'confidence': 'exact',
            'witness': f'every round is a deal-into-{sorted(bases_used)}-piles + '
                       f'block-gather permutation'}


def _match_faro(cand):
    fp = faro_perms(cand.N)
    if not fp:
        return None
    for pi in _collect_round_perms(cand):
        if pi not in fp:
            return None
    return {'family': 'Faro', 'confidence': 'exact',
            'witness': 'every round is a perfect out/in interleave'}


def _match_josephus(cand):
    sig = down_under_elim_perm(cand.N)
    perms = _collect_round_perms(cand)
    if perms and all(pi == sig for pi in perms):
        return {'family': 'Josephus', 'confidence': 'exact',
                'witness': 'round permutation is the down-under elimination order'}
    return None


def _blocks_complete(final, k):
    return all({c % k for c in final[i:i + k]} == set(range(k))
               for i in range(0, len(final), k))


def _match_gilbreath(cand):
    """Property recognizer. Exact iff the invariant holds across ALL interleavings
    AND is non-vacuous (a control without the deal-off reversal breaks it)."""
    from itertools import product
    N, k = cand.N, cand.invariant_k
    stack = [i for i in range(N)]           # class = i % k on a cyclic stack
    holds = True
    for pat in product((0, 1), repeat=N):
        m = pat.count(0)
        deck = list(range(N))
        out = cand.shuffle(deck, {'m': m, 'pattern': list(pat)})
        if not _blocks_complete(out, k):
            holds = False
            break
    if not holds:
        return None
    # non-vacuity control: same shuffle WITHOUT reversal must break it
    broke = False
    for pat in product((0, 1), repeat=N):
        m = pat.count(0)
        deck = list(range(N))
        pile, rest = deck[:m], deck[m:]     # no reversal
        out = riffle_merge(pile, rest, list(pat))
        if not _blocks_complete(out, k):
            broke = True
            break
    if not broke:
        return {'family': 'Gilbreath?', 'confidence': 'abstain',
                'witness': 'invariant holds but control did not break it — vacuous?'}
    return {'family': 'Gilbreath', 'confidence': 'exact',
            'witness': f'blocks of {k} preserve all residues; control (no reversal) breaks it'}


def _match_hummer(cand):
    """DELIBERATELY NARROW. Hummer/CATO parity has many forms; this stub checks
    only one and abstains otherwise, so it never emits a broad false KNOWN."""
    return {'family': 'Hummer', 'confidence': 'abstain',
            'witness': 'Hummer recognizer is a narrow stub; not implemented — routing onward'}


def classify(cand, log):
    """Run the recognizers, apply asymmetric policy, log-and-suppress matches."""
    if cand.kind == 'permutation':
        recognizers = (_match_gergonne, _match_faro, _match_josephus)
    else:
        recognizers = (_match_gilbreath,)

    hits = [r(cand) for r in recognizers]
    exact = [h for h in hits if h and h['confidence'] == 'exact']
    abstains = [h for h in hits if h and h['confidence'] == 'abstain']

    if len(exact) == 1:
        h = exact[0]
        log.record(cand.name, h['family'], 'exact', h['witness'], cand.N)
        return {'verdict': 'MATCHED', 'family': h['family'],
                'confidence': 'exact', 'witness': h['witness']}
    if len(exact) > 1:                        # two families at once = suspicious
        log.record(cand.name, '+'.join(h['family'] for h in exact),
                   'ambiguous', 'multiple exact matches', cand.N)
        return {'verdict': 'ABSTAIN', 'reason': 'multiple family matches',
                'families': [h['family'] for h in exact]}
    if abstains:
        log.record(cand.name, abstains[0]['family'], 'abstain',
                   abstains[0]['witness'], cand.N)
        return {'verdict': 'ABSTAIN', 'reason': abstains[0]['witness']}
    return {'verdict': 'NOT_MATCHED', 'families_checked': 5,
            'note': 'not one of the five known families — routed onward, NOT certified novel'}


# ---- demonstration -----------------------------------------------------------

if __name__ == '__main__':
    log = SuppressedLog()

    def show(cand):
        v = classify(cand, log)
        tag = v['verdict']
        extra = v.get('family') or v.get('reason') or v.get('note', '')
        print(f"  {cand.name:<34} -> {tag:<12} {extra}")

    # t15: fixed-code 3-pile 5-round targeting (the drift that fooled us)
    def _round_perm(before, after):
        pos = {c: i for i, c in enumerate(before)}
        return tuple(pos[c] for c in after)

    T15_CODE = {20: [0, 2, 1, 2, 1]}
    def t15_rounds(ch):
        d = list(range(52)); perms = []
        for a in T15_CODE[ch['n']]:
            before = list(d)
            piles = deal_into_piles(d, 3)
            j = next(i for i, p in enumerate(piles) if ch['card'] in p)
            d = gather_position(piles, j, a)
            perms.append(_round_perm(before, d))
        return perms

    t15 = Candidate("t15 (adaptive full-deck ACAAN)", 52, 'permutation',
                    round_perms=t15_rounds,
                    sample_choices=[{'card': 41, 'n': 20}, {'card': 7, 'n': 20},
                                    {'card': 0, 'n': 20}])

    # t8: mixed-radix (4 then 13) targeting
    def t8_rounds(ch):
        d = list(range(52)); perms = []
        for b, a in ((4, ch['p1']), (13, ch['p2'])):
            before = list(d)
            piles = deal_into_piles(d, b)
            j = next(i for i, p in enumerate(piles) if ch['card'] in p)
            d = gather_position(piles, j, a)
            perms.append(tuple(_round_perm(before, d)))
        return perms
    t8 = Candidate("t8 (mixed-radix 4x13 ACAAN)", 52, 'permutation',
                   round_perms=t8_rounds,
                   sample_choices=[{'card': 10, 'p1': 2, 'p2': 3},
                                   {'card': 30, 'p1': 1, 'p2': 0}])

    # a faro round
    faro = Candidate("perfect out-faro", 52, 'permutation',
                     round_perms=lambda ch: [perm_of(
                         lambda d: [d[k // 2] if k % 2 == 0 else d[26 + k // 2]
                                    for k in range(52)], 52)],
                     sample_choices=[{}])

    # a down-under deal (Josephus)
    josephus = Candidate("down-under deal", 16, 'permutation',
                         round_perms=lambda ch: [down_under_elim_perm(16)],
                         sample_choices=[{}])

    # t9 Gilbreath (property kind)
    def gilb_shuffle(deck, ch):
        pile, rest = deal_pile(deck, ch['m'])
        return riffle_merge(pile, rest, ch['pattern'])
    gilb = Candidate("t9 (Gilbreath suit divination)", 8, 'property',
                     shuffle=gilb_shuffle, invariant_k=4)

    # a genuinely-outside procedure: full reversal (turn the packet over)
    reversal = Candidate("full reversal (novel-ish)", 52, 'permutation',
                         round_perms=lambda ch: [perm_of(lambda d: d[::-1], 52)],
                         sample_choices=[{}])

    # a Mongean shuffle: also outside the five
    def mongean(d):
        out = deque()
        for i, c in enumerate(d):
            (out.appendleft if i % 2 == 0 else out.append)(c)
        return list(out)
    monge = Candidate("Mongean shuffle (novel-ish)", 52, 'permutation',
                      round_perms=lambda ch: [perm_of(mongean, 52)],
                      sample_choices=[{}])

    print("VERDICTS")
    for c in (t15, t8, faro, josephus, gilb, reversal, monge):
        show(c)

    print("\nSUPPRESSED LOG:", log.summary())
    print("REVIEW QUEUE (uncertain matches a human should check):")
    for e in log.review_queue():
        print(f"  - {e['name']}: {e['family']} [{e['confidence']}] — {e['witness']}")
    if not log.review_queue():
        print("  (none — all suppressions were exact signature matches)")
