# Audit of the engine drop (novelty_oracle.py + refuter.py)

Run 2026-08-27 on branch `oracle` against the REAL library procedures
(`oracle_audit.py`; the shipped demo uses a fixed-vector stand-in for t15).

## Reproduction of shipped demos
- `novelty_oracle.py`: all seven demo verdicts reproduce (5 MATCHED with
  empty review queue, reversal + Mongean NOT_MATCHED).
- `refuter.py`: C1 (naive radix law) killed at boundary (2,2) after the
  confirmatory loop would have committed it; C2 (the library's
  parity-corrected radix law) survived all 12 adversarial params up to
  scale 512 — this extends the law's empirical envelope well beyond
  anything the library had run (max was b=7, r=2 = 49) -> the t6 entry's
  envelope can cite (2,9)=512, 262,144 cases.

## Acceptance ledger, with a self-correction
| candidate | oracle verdict | judgment |
|---|---|---|
| REAL t3 (fixed Gergonne, 27) | MATCHED Gergonne | correct suppression |
| REAL t15 (adaptive ACAAN, 52) | MATCHED Gergonne | **correct — auditor's original expectation overturned** |
| REAL t17 (reactive double reveal, 11) | NOT_MATCHED | correct routing |

The auditor (deriver agent) had claimed t15 "must not match" because no
fixed-placement instance reproduces it — asserted as decidable but never
decided. Running the decision procedure refuted the auditor: at r=5, fixed
relative-placement vectors are start-independent onto **52/52** targets
(the library had only tested r=3,4, where they fail, then reached for
adaptive machinery). Consequences:
- The oracle's headline ("catches t15 as Gergonne") STANDS at the trick
  level; the per-round matcher produced a TRUE known here, not a false one.
- A new verified result fell out: FIXED-VECTOR ACAAN — 52 cards, 3 uneven
  piles, 5 deals, one fixed 5-vector per named position — verify() PASS
  over 2,704 cases. Supersedes t15's strategy trees for the effect
  (committed to `main` as t18); t15's r<=4 impossibility results and the
  strategy-search METHOD remain valid contributions.
- The residual above-round-level concern is real but narrower than claimed:
  it applies to MULTI-CARD procedures. Proof for t17: a fixed ordering
  sequence composes to one position-permutation, which is injective and so
  cannot collapse 110 distinct pairs onto a single (top, bottom) outcome —
  only observation-dependent orderings can. The shipped oracle happens to
  route t17 onward (gather_order vocabulary is outside the union); keep it
  that way if the union is ever extended.

## Residual nits (pre-merge)
1. `NOT_MATCHED` reports `families_checked: 5`; permutation kind runs 3
   recognizers, property kind 1, and `_match_hummer` is never invoked.
2. Dead no-op branch in `_match_gergonne` (the `N % b` check).
3. Pin recognizers to exhaustive card sampling (the drop's own top
   recommendation) before any live-generator use.

## Verdict
Merge-ready after the nits; the asymmetric-error design behaved as
specified on every case tested, including the one where it corrected the
auditor.

## Addendum: nits fixed (2026-08-27, pre-merge)
1. `families_checked` now reports the recognizer names actually run
   (permutation kind: Gergonne/Faro/Josephus; property kind: Gilbreath);
   the NOT_MATCHED note discloses that Hummer is declared but unimplemented.
   `_match_hummer` is a documented, deliberately-unwired stub returning
   None (wiring an always-abstain recognizer would convert every
   NOT_MATCHED into ABSTAIN and poison the review queue; and the op
   vocabulary has no orientation primitives for it to inspect).
2. Dead no-op branch removed from `_match_gergonne`.
3. Sampling pinned: `Candidate` carries a declared `sample_scope`; a
   signature match on a partial sample ABSTAINS (surfaced for review,
   logged with confidence 'sampled') instead of suppressing, and the scope
   is written into every match witness. Demo and audit candidates now
   declare exhaustive card coverage.
Post-fix reruns: the oracle demo preserves all seven verdicts with the
honest NOT_MATCHED wording, and the acceptance ledger reproduces —
t3 MATCHED, t15 MATCHED (true known), t17 NOT_MATCHED — with the
fixed-vector ACAAN re-verified at PASS 2704 along the way.
