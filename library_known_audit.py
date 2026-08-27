"""Engine item 2 acceptance audit: the library-as-known recognizer.

Ledger:
  MUST MATCH LibraryTargeting:
    - 3-pile universal-law ACAAN (t20 form)
    - 6-pile bucket ACAAN (t23 form)
    - REAL adaptive t15 (procedurally adaptive, extensionally fixed — the
      session-6 lesson, now caught automatically)
  MUST keep old verdicts:
    - t3 classic Gergonne (no named target) -> MATCHED Gergonne
    - REAL t17 double reveal (multi-card)   -> NOT_MATCHED, routed onward
    - full reversal                          -> NOT_MATCHED
"""
import sys
import importlib.util
from deck_sim import deal_into_piles, gather_position, gather_order
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


def targeting_rounds(vec_fn, N, b):
    def rounds(ch):
        d = list(range(N))
        card, perms = ch['card'], []
        for a in vec_fn(ch['n']):
            before = list(d)
            piles = deal_into_piles(d, b)
            j = next(i for i, p in enumerate(piles) if card in p)
            d = gather_position(piles, j, a)
            perms.append(round_perm(before, d))
        return perms
    return rounds


t20 = load('tricks/t20_universal_radix_law.py', 't20mod')
t23 = load('tricks/t23_six_pile_buckets.py', 't23mod')
print("loading real t15 strategies...")
t15 = load('tricks/t15_uneven_adaptive.py', 't15mod')
STRATS = t15.build_strategies()
t17 = load('tricks/t17_small_double_reveal.py', 't17mod')
G11 = t17.build_G(11, 4)
D11 = t17.distance_map(G11, 11, 4, (0, 10), 6)
TABLES = t17.reactive_search(G11, 11, 4, (0, 10), 4, D11)

TARGETS = (7, 20, 40)
cand_t20 = Candidate("3-pile universal-law ACAAN (t20)", 52, 'permutation',
                     round_perms=targeting_rounds(
                         lambda n: t20.law_vector(n, 52, 5), 52, 3),
                     sample_choices=[{'card': c, 'n': n}
                                     for c in range(52) for n in TARGETS],
                     sample_scope='exhaustive')

cand_t23 = Candidate("6-pile bucket ACAAN (t23)", 52, 'permutation',
                     round_perms=targeting_rounds(
                         lambda n: t23.bucket_vector(n), 52, 6),
                     sample_choices=[{'card': c, 'n': n}
                                     for c in range(52) for n in (15, 36, 52)],
                     sample_scope='exhaustive')


def t15_rounds(ch):
    d = list(range(52))
    card, hist, perms = ch['card'], (), []
    strat = STRATS[ch['n'] - 1]
    for _ in range(5):
        before = list(d)
        piles = deal_into_piles(d, 3)
        j = next(i for i, p in enumerate(piles) if card in p)
        hist += (j,)
        d = gather_position(piles, j, strat[hist])
        perms.append(round_perm(before, d))
    return perms


cand_t15 = Candidate("REAL t15 (adaptive ACAAN)", 52, 'permutation',
                     round_perms=t15_rounds,
                     sample_choices=[{'card': c, 'n': n}
                                     for c in range(52) for n in (20, 45)],
                     sample_scope='exhaustive')


def t3_rounds(ch):
    d = list(range(27))
    card, perms = ch['card'], []
    for a in (1, 2, 1):
        before = list(d)
        piles = deal_into_piles(d, 3)
        j = next(i for i, p in enumerate(piles) if card in p)
        d = gather_position(piles, j, a)
        perms.append(round_perm(before, d))
    return perms


cand_t3 = Candidate("t3 classic Gergonne (no named target)", 27,
                    'permutation', round_perms=t3_rounds,
                    sample_choices=[{'card': c} for c in range(27)],
                    sample_scope='exhaustive')


def t17_rounds(ch):
    d = list(range(11))
    ca, cb, perms = ch['a'], ch['b'], []
    for table in TABLES:
        before = list(d)
        piles = deal_into_piles(d, 4)
        ja = next(i for i, p in enumerate(piles) if ca in p)
        jb = next(i for i, p in enumerate(piles) if cb in p)
        d = gather_order(piles, list(t17.PERMS[4][table[(ja, jb)]]))
        perms.append(round_perm(before, d))
    return perms


cand_t17 = Candidate("REAL t17 (multi-card double reveal)", 11,
                     'permutation', round_perms=t17_rounds,
                     sample_choices=[{'card': a, 'a': a, 'b': b}
                                     for a in range(11) for b in range(11)
                                     if a != b],
                     sample_scope='exhaustive')

cand_rev = Candidate("full reversal", 52, 'permutation',
                     round_perms=lambda ch: [tuple(range(51, -1, -1))],
                     sample_choices=[{}], sample_scope='exhaustive')

EXPECT = {
    cand_t20.name: ('MATCHED', 'LibraryTargeting'),
    cand_t23.name: ('MATCHED', 'LibraryTargeting'),
    cand_t15.name: ('MATCHED', 'LibraryTargeting'),
    cand_t3.name: ('MATCHED', 'Gergonne'),
    cand_t17.name: ('NOT_MATCHED', None),
    cand_rev.name: ('NOT_MATCHED', None),
}

log = SuppressedLog()
fails = 0
for cand in (cand_t20, cand_t23, cand_t15, cand_t3, cand_t17, cand_rev):
    v = classify(cand, log)
    want_verdict, want_family = EXPECT[cand.name]
    got_family = v.get('family')
    ok = v['verdict'] == want_verdict and (want_family is None
                                           or got_family == want_family)
    fails += 0 if ok else 1
    print(f"  {cand.name:<44} -> {v['verdict']:<12} "
          f"{got_family or ''}  [{'ok' if ok else 'LEDGER FAIL'}]")
print(f"\nACCEPTANCE {'PASS' if fails == 0 else f'FAIL ({fails})'}; "
      f"suppressed log: {log.summary()}")
