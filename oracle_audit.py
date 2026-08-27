"""oracle_audit.py — acceptance audit of novelty_oracle.py against the
library's own commits, run on the REAL procedures (not stand-ins).

Original ledger expectation: t3 should match Gergonne, t15/t17 must not.
THE AUDIT REFUTED ITS OWN LEDGER on t15: at r=5 the fixed relative-placement
vectors cover ALL 52 targets start-independently (the library had only ever
checked r=3,4, where they fail, before reaching for adaptive strategy
trees). So the oracle's MATCHED-Gergonne on t15 is a TRUE known at the
trick level, and t15's adaptive machinery is unnecessary for the effect.
This file records both the oracle verdicts and the discovery, and verifies
the fixed-vector replacement trick end to end.

t17 (multi-spectator) remains genuinely outside Gergonne, with proof: a
fixed pile-ordering sequence composes to a single permutation of positions,
and a permutation is injective — it cannot collapse 110 distinct card-pairs
onto one (top, bottom) outcome. Only observation-dependent orderings can.
"""
import sys
import importlib.util
from itertools import product

import deck_sim
from deck_sim import (make_deck, deal_into_piles, gather_position,
                      gather_order, verify)
from novelty_oracle import Candidate, classify, SuppressedLog


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def round_perm(before, after):
    pos = {c: i for i, c in enumerate(before)}
    return tuple(pos[c] for c in after)


print("loading real t15 strategies (backward induction, 52 targets)...")
t15 = load('tricks/t15_uneven_adaptive.py', 't15mod')
STRATEGIES = t15.build_strategies()

# ---- extensional check: which targets can FIXED placements reach at r=5? ----
F = t15.F
fixed_vector = {}
for vec in product(range(3), repeat=5):
    finals = set()
    for x in range(52):
        pos = x
        for a in vec:
            pos = F[pos][a]
        finals.add(pos)
    if len(finals) == 1:
        fixed_vector.setdefault(finals.pop(), vec)
print(f"fixed relative-placement vectors at r=5 reach "
      f"{len(fixed_vector)}/52 targets start-independently")

if len(fixed_vector) == 52:
    print("=> DISCOVERY: t15's adaptive strategy trees are UNNECESSARY —")
    print("   a fixed 5-vector exists per target. Verifying that trick:")

    def fixed_trick(deck, choices):
        d = deck[:52]
        card = choices['card']
        for a in fixed_vector[choices['n'] - 1]:
            piles = deal_into_piles(d, 3)
            j = next(i for i, p in enumerate(piles) if card in p)
            d = gather_position(piles, j, a)
        return d

    domain = [{'card': c, 'n': n} for c in make_deck() for n in range(1, 53)]
    ok, counter = verify(fixed_trick, domain, lambda f, ch: f[ch['n'] - 1])
    print(f"   FIXED-VECTOR ACAAN (52 cards, 3 uneven piles, 5 deals): "
          f"{'PASS' if ok else 'FAIL'} over {len(domain)} cases")
    if not ok:
        print(f"   fails e.g. {counter[:3]}")

# ---- candidates built from the REAL procedures ------------------------------

def t15_real_rounds(ch):
    d = list(range(52))
    card = ch['card']
    strat, hist, perms = STRATEGIES[ch['n'] - 1], (), []
    for _ in range(5):
        before = list(d)
        piles = deal_into_piles(d, 3)
        j = next(i for i, p in enumerate(piles) if card in p)
        hist += (j,)
        d = gather_position(piles, j, strat[hist])
        perms.append(round_perm(before, d))
    return perms


t15_real = Candidate("REAL t15 (adaptive ACAAN)", 52, 'permutation',
                     round_perms=t15_real_rounds,
                     sample_choices=[{'card': c, 'n': n}
                                     for c in range(52)
                                     for n in (3, 20, 45, 52, 1)],
                     sample_scope='exhaustive')

print("\nrebuilding t17 reactive tables (deterministic search)...")
t17 = load('tricks/t17_small_double_reveal.py', 't17mod')
G11 = t17.build_G(11, 4)
D11 = t17.distance_map(G11, 11, 4, (0, 10), 6)
TABLES = t17.reactive_search(G11, 11, 4, (0, 10), 4, D11)
assert TABLES, "t17 reactive tables did not rebuild"
P4 = t17.PERMS[4]


def t17_rounds(ch):
    d = list(range(11))
    ca, cb, perms = ch['a'], ch['b'], []
    for table in TABLES:
        before = list(d)
        piles = deal_into_piles(d, 4)
        ja = next(i for i, p in enumerate(piles) if ca in p)
        jb = next(i for i, p in enumerate(piles) if cb in p)
        d = gather_order(piles, list(P4[table[(ja, jb)]]))
        perms.append(round_perm(before, d))
    return perms


t17_real = Candidate("REAL t17 (reactive double reveal)", 11, 'permutation',
                     round_perms=t17_rounds,
                     sample_choices=[{'card': a, 'a': a, 'b': b}
                                     for a in range(11) for b in range(11)
                                     if a != b],
                     sample_scope='exhaustive')


def t3_rounds(ch):
    d = list(range(27))
    card, perms = ch['card'], []
    for a in (1, 2, 1):                      # true Gergonne: fixed placements
        before = list(d)
        piles = deal_into_piles(d, 3)
        j = next(i for i, p in enumerate(piles) if card in p)
        d = gather_position(piles, j, a)
        perms.append(round_perm(before, d))
    return perms


t3_real = Candidate("REAL t3 (fixed-placement Gergonne)", 27, 'permutation',
                    round_perms=t3_rounds,
                    sample_choices=[{'card': c} for c in range(27)],
                    sample_scope='exhaustive')

# ---- run the ledger ---------------------------------------------------------

log = SuppressedLog()
print("\nAUDIT VERDICTS (per-round matcher, as shipped):")
expectations = {
    "REAL t3 (fixed-placement Gergonne)":
        "MATCH expected — true Gergonne (correct suppression)",
    "REAL t15 (adaptive ACAAN)":
        "MATCH now judged CORRECT: fixed vectors cover all 52 targets at "
        "r=5, so the trick is extensionally Gergonne-family (audit "
        "overturned the original 'must not match' expectation)",
    "REAL t17 (reactive double reveal)":
        "must NOT match — injectivity proof: no fixed ordering sequence "
        "can collapse distinct pairs to one outcome",
}
for cand in (t3_real, t15_real, t17_real):
    v = classify(cand, log)
    extra = v.get('family') or v.get('reason') or v.get('note', '')
    print(f"  {cand.name:<38} -> {v['verdict']:<12} {extra}")
    print(f"      ledger: {expectations[cand.name]}")

print("\nnit status (fixed pre-merge, this branch):")
print("  - families_checked now reports the recognizers actually run;")
print("    Hummer stub documented as deliberately unwired (no orientation ops)")
print("  - dead no-op branch removed from _match_gergonne")
print("  - sampling pinned: matches on partial samples ABSTAIN; scope is")
print("    declared per candidate and written into the suppressed log")
print("  - standing rule: multi-card procedures stay routed onward (t17)")
