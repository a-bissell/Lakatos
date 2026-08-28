"""refuter.py — the adversarial promotion path for conjectures about card procedures.

Design stance (this is the anti-drift core):
  * The refuter's JOB is to kill conjectures. It is built to want them dead.
  * A conjecture NEVER earns THEOREM from testing alone. Empirical non-refutation
    is not a proof. The top status this module can award is ROBUST_CONJECTURE.
  * The refuter reports the FALSE-CONFIDENCE DELTA: the gap between what a
    confirmatory loop (test only the inspiring scales) would commit, and what
    survives adversarial attack. That delta is the drift being measured.

Status ladder (load-bearing labels):
  NOT_A_CANDIDATE    fails even at the scales that inspired it
  CANDIDATE          holds at inspiring scales; not yet attacked
  CONJECTURE         survived some attack beyond inspiring scales
  ROBUST_CONJECTURE  survived the full adversarial battery; still no proof
  THEOREM            has a proof  <-- UNREACHABLE HERE, BY DESIGN
  REFUTED            counterexample found (witness recorded)
"""
from itertools import product
from dataclasses import dataclass, field
from typing import Callable, Any, Optional

from deck_sim import deal_into_piles, gather_position


# ---- generic targeting over an abstract N-token packet (not tied to 52) ------
# Theorems aren't about a 52-card deck, so the refuter tests abstract packets and
# can push scale past any physical deck. Tokens are ints 0..N-1 = start positions.

def radix_place(n, b, r, parity=True):
    """Placement sequence to send a card to 1-indexed position n, packet b**r,
    r deals into b piles. parity=True is the audited law; parity=False is the
    naive pre-correction (p_i = base-b digits of n-1, no reversal complement)."""
    x = n - 1
    digits = []
    for _ in range(r):
        digits.append(x % b)
        x //= b
    if not parity:
        return digits
    return [d if (r - 1 - i) % 2 == 0 else (b - 1) - d
            for i, d in enumerate(digits)]


def targeting_instance(b, r, parity):
    """Exhaustive ∀card ∀n test at one (b,r): does the placement rule land every
    card at every named position? Returns (ok, witness_or_None, n_cases)."""
    N = b ** r
    packet = list(range(N))
    for card in packet:
        for n in range(1, N + 1):
            d = list(packet)
            for a in radix_place(n, b, r, parity):
                piles = deal_into_piles(d, b)
                j = next(i for i, p in enumerate(piles) if card in p)
                d = gather_position(piles, j, a)
            if d[n - 1] != card:
                return False, {'b': b, 'r': r, 'card': card, 'named_n': n,
                               'got_pos': d.index(card) + 1, 'want_pos': n}, N * N
    return True, None, N * N


# ---- conjecture object + adversarial refuter --------------------------------

@dataclass
class Conjecture:
    name: str
    claim: str
    instance_test: Callable[..., tuple]   # param -> (ok, witness, n_cases)
    scale: Callable[..., int]             # param -> difficulty (bigger = harder)
    inspiring: list                       # params that suggested the pattern
    beyond: list = field(default_factory=list)     # params of larger scale
    boundary: list = field(default_factory=list)   # extreme params
    random_draw: list = field(default_factory=list)
    param_names: tuple = None             # optional, for envelope reporting


def confirmatory_verdict(conj):
    """The LAZY loop this project keeps drifting into: test only the inspiring
    scales; if they pass, commit. Returns (committed, cases)."""
    cases = 0
    for p in conj.inspiring:
        ok, _, nc = conj.instance_test(*p); cases += nc
        if not ok:
            return False, cases
    return True, cases


def refute(conj, verbose=True):
    """Adversarial promotion path. Attacks in cost order, stops at first kill."""
    log = []
    def line(s):
        log.append(s)
        if verbose: print(s)

    line(f"── {conj.name} ──")
    line(f"   claim: {conj.claim}")

    # 0. must hold where it was seen, or it was never even a candidate
    max_insp, cases = 0, 0
    for p in conj.inspiring:
        ok, w, nc = conj.instance_test(*p)
        max_insp = max(max_insp, conj.scale(*p))
        cases += nc
        if not ok:
            line(f"   [inspiring {p}] FAILS -> NOT_A_CANDIDATE  witness={w}")
            return {'status': 'NOT_A_CANDIDATE', 'witness': w, 'cases': cases,
                    'log': log}
    line(f"   inspiring scales hold (max scale {max_insp}); "
         f"a confirmatory loop would COMMIT this now.")

    # 1. adversarial battery: boundary + beyond + random, cheapest first
    attack = []
    for tag, params in (('boundary', conj.boundary),
                        ('beyond', conj.beyond),
                        ('random', conj.random_draw)):
        for p in params:
            attack.append((conj.scale(*p), tag, p))
    attack.sort()  # cheap first so a kill costs little

    tested = 0
    for sc, tag, p in attack:
        ok, w, nc = conj.instance_test(*p)
        tested += 1
        cases += nc
        beyond_flag = " (scale>inspiring)" if sc > max_insp else ""
        if not ok:
            line(f"   [{tag} {p}]{beyond_flag} COUNTEREXAMPLE -> REFUTED")
            line(f"      witness: {w}")
            line(f"      false-confidence delta: confirmatory loop COMMITS; "
                 f"refuter KILLS at scale {sc}.")
            return {'status': 'REFUTED', 'witness': w, 'killed_at': p,
                    'attacks_before_kill': tested, 'cases': cases, 'log': log}
        else:
            line(f"   [{tag} {p}]{beyond_flag} holds ({nc} cases)")

    # graded verdict — 'robust' is earned by scale BEYOND inspiring, not by
    # merely having a list of attacks. An empty or too-timid battery must
    # not launder a CANDIDATE into a robust stamp.
    envelope = None
    if conj.param_names:
        allp = list(conj.inspiring) + [p for _, _, p in attack]
        envelope = {nm: max(p[i] for p in allp)
                    for i, nm in enumerate(conj.param_names)}
    span = [sc for sc, _, _ in attack]
    if tested == 0:
        line("   NO attacks scheduled -> CANDIDATE (holds where seen; "
             "not yet attacked).")
        return {'status': 'CANDIDATE', 'witness': None, 'attacks_survived': 0,
                'max_scale': max_insp, 'cases': cases, 'envelope': envelope,
                'log': log}
    if all(sc <= max_insp for sc in span):
        line(f"   survived {tested} attacks, but none exceeded inspiring "
             f"scale {max_insp} -> CONJECTURE (never attacked beyond).")
        return {'status': 'CONJECTURE', 'witness': None,
                'attacks_survived': tested, 'max_scale': max(span),
                'cases': cases, 'envelope': envelope, 'log': log}
    line(f"   survived {tested} adversarial params, scale up to {max(span)} "
         f"(inspiring max {max_insp}).")
    if envelope:
        line(f"   envelope: {envelope}")
    line(f"   -> ROBUST_CONJECTURE (empirical). NOT a theorem: no proof exists.")
    return {'status': 'ROBUST_CONJECTURE', 'witness': None,
            'attacks_survived': tested, 'max_scale': max(span),
            'cases': cases, 'envelope': envelope, 'log': log}


if __name__ == '__main__':
    # C1 — the drift specimen: the NAIVE radix law (no parity complement).
    # It coincides with the true law at r=1, so a loop that "noticed" it on
    # single-round configs would commit it. It is false for r>=2.
    c1 = Conjecture(
        name="C1  naive radix law (p_i = base-b digits of n-1)",
        claim="placements = base-b digits of n-1 send any card to position n",
        instance_test=lambda b, r: targeting_instance(b, r, parity=False),
        scale=lambda b, r: b ** r,
        inspiring=[(2, 1), (3, 1), (4, 1), (5, 1), (6, 1)],
        boundary=[(2, 2), (7, 1)],
        beyond=[(3, 2), (2, 3), (4, 2), (3, 3)],
        random_draw=[(5, 2)],
    )

    # C2 — the audited law WITH parity complement. Should survive the battery
    # but must still stop at ROBUST_CONJECTURE (this module can't prove it).
    c2 = Conjecture(
        name="C2  parity-corrected radix law",
        claim="p_i = d_i if an even # of deals follow round i, else (b-1)-d_i",
        instance_test=lambda b, r: targeting_instance(b, r, parity=True),
        scale=lambda b, r: b ** r,
        inspiring=[(3, 3), (4, 2)],                 # where the project found it
        boundary=[(2, 8), (2, 9), (10, 2)],         # deep reversal / wide base
        beyond=[(2, 4), (2, 5), (2, 6), (3, 4), (5, 3), (7, 2)],
        random_draw=[(3, 5), (4, 3), (6, 2)],
    )

    for c in (c1, c2):
        # show the lazy loop's verdict first, then the adversarial one
        committed, cc = confirmatory_verdict(c)
        print(f"\n=== {c.name.split()[0]} ===")
        print(f"   confirmatory loop (inspiring only, {cc} cases): "
              f"{'COMMIT as law' if committed else 'reject'}")
        res = refute(c)
        print(f"   FINAL STATUS: {res['status']}")
