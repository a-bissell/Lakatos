# Capstone — the engine track, items 1–8

*Sessions 12–15 (2026-08-27 / 2026-08-28). Status: queue complete.*

## What was built

Sessions 1–11 of this project ran a manual loop: rediscover a known
card principle, mutate it, compose it, notice structure, extract a
closed form, escalate the domain, map the frontier. Every result was
gated by one rule — nothing counts as working unless `verify()` in
[deck_sim.py](deck_sim.py) passes over the entire free-choice domain.
That loop produced the radix-placement family (t3–t14), the uneven-pile
work (t15–t19), and the universal laws (t20–t23), ending in a closed
form for any-card-any-position targeting with any pile count.

The engine track automated the loop. Eight items, four sessions, each
item exercised against real library content before the next was
allowed to depend on it. The result is a pipeline —

    generator -> novelty oracle -> conjecture former -> refuter

— in which candidates are invented mechanically, known material is
recognized and suppressed, closed forms are fitted from black-box
behavior alone, and every surviving claim is attacked by schedules
derived from its own parameter signature. Two layers sit alongside the
pipeline: a provenance ledger that makes "likely new" as auditable as
a verify() count, and a proof layer that promoted the capstone law
from robust conjecture to theorem.

## The eight items

**1. Abstract packets** (commit `06cfb8b`). The harness had been
hardwired to a 52-card deck, and grids had silently shrunk to fit.
`verify()`/`verify_prop()` gained a `deck_factory` parameter and a
`make_packet(N)` primitive; t24 then verified the general-b law at
tight fits up to N=144, b=12 — 47,954 cases beyond any physical deck.

**2. Library-as-known** (commit `5948104`). Recognizers are generated
from committed laws, so the generator cannot re-derive t18–t23 and
have it count as novel. The extensional `LibraryTargeting` recognizer
reproduces a candidate's whole (card, target) map with fixed vectors;
acceptance included catching the genuinely adaptive t15 as
library-known. Sampling is pinned: a partial-sample match abstains and
surfaces for review rather than suppressing.

**3. Conjecture former** (commit `62cac8c`). [former.py](former.py)
fits exact closed forms from raw behavior — rational RREF with early
inconsistency exit, model trees split on atom comparisons, refusal as
a first-class outcome — and imports nothing from the project. The
acceptance ledger enforces the no-hints boundary by scanning the
source for simulator vocabulary. Result: the general-b round law
re-derived unaided as a 5-leaf tree, extensionally identical to the
corr algebra; 240 law vectors cross-certified; 4,353 verify() cases
planned from the fitted model alone. The first fit attempt was refuted
by its own battery (an overfit q0-sparse pocket, killed at N=11, b=6)
and repaired with two-pass extraction and a grid-diversity rule.

**4. Refuter automation** (commit `3e77484`). Attack schedules are
derived from a conjecture's parameter signature — floor probes
bisected against validity, escalation walks beyond every inspiring
maximum from multiple anchors, envelope-edge bisection, deterministic
draws — with a no-silent-caps report per axis. `refute()` now grades:
CANDIDATE, CONJECTURE, ROBUST_CONJECTURE, REFUTED, each with an
envelope. The whole-library battery ([refuter_battery.py](refuter_battery.py))
runs 7/7 at ~3.7M cases in ~100s and extended every envelope
(general-b to b=52/N=104/r=202; Josephus to n=6,656; conservation
generalized past b=3 to b=2 and b=4). The laundering demo is kept as a
specimen: a 10,844-case curated adversary stamps a false conjecture
ROBUST; the derived schedule kills it at the floor probe (2,2,5).

**5. Integration loop** (commit `a56e541`). [engine.py](engine.py)
chains the pipeline under candidate-atomic budgets (candidates, cases,
seconds — every skip named), with eight dispositions and the
suppressed log as a live drift metric. The dry run doubles as the
acceptance ledger (9/9). First fully-autonomous product: the Mongean
position law, oracle-cleared, machine-fitted, ROBUST_CONJECTURE at
envelope N=1500 — later reclassified by item 7 (see below).

**6. Generator v1** (commit `ecad9f0`). [generator.py](generator.py)
instantiates one question schema (the round-position-law question)
over the existing op vocabulary, deliberately ignorant of what is
known — both an oracle view and a former view are attached, and the
guardrails decide. Metric met 11/11: six of nine candidates suppressed
across three families (the drift metric working), one honest refusal
(cut-then-deal needs a grammar the former does not have), and two
oracle-NOT_MATCHED survivors at ROBUST_CONJECTURE: the reversed-rest
pickup laws for b=3 and b=4, envelopes past N=5,000. The item also
hardened the machinery: claims scoped to N ≥ b after a refuter floor
kill, a bounded repair loop (a refutation witness joins the fit grid
and the former refits), and residue-breaking probes in the scheduler
after a unit test exposed that pure doubling walks preserve N mod b.

**7. Provenance** (commit `f35fced`). [PROVENANCE.md](PROVENANCE.md)
holds a dated record — queries, sources, a controlled verdict — for
every library entry that claims novelty, and
[provenance_audit.py](provenance_audit.py) enforces the link: a
flagged entry without a record fails the audit, and a KNOWN verdict
requires the entry itself to acknowledge the literature. Headline
verdicts: the Mongean law is a rediscovery (Monge 1773; the oracle
cleared it only because no Monge recognizer exists, a coverage gap now
on record); the uneven-radix family is KNOWN-FAMILY (the floor-map
dynamics are charted, the uneven-N targeting laws were not found); the
two-card shared-gather results are NOT-FOUND under the logged queries
and remain the strongest new-result candidates.

**8. Proof step** (commit `fefb352`). [PROOF.md](PROOF.md) +
[proof.py](proof.py) prove the general-b law's sufficiency condition
b^(r-1) ≥ N over the entire hypothesis region. The chain: pile-size
algebra, the round-map closed form, preimage contiguity (every
target's preimage is b consecutive positions), an exact endpoint
recursion whose doubled center is the law's z-recursion, offset gap
bounds, and the envelope |z_k| ≤ N + (b-2)·b^(k-1). Coverage after r
rounds requires |z_r| ≤ b^r − N, and the margin computes to
2·b^(r-1) − 2N: the sufficient condition is the coverage condition
with zero slack, which also explains why it is not necessary. Every
identity and inequality is machine-checked (Farkas certificates plus
exact polynomial expansion); three prose steps are named explicitly.
The general-b law is the library's first THEOREM-status entry.

## The self-correction ledger

The design bet of the whole track was that guardrails should catch the
author's and the machine's drift, and the record shows them doing it,
repeatedly, at every layer:

- Session 6: the oracle audit overturned the deriver's own claim —
  t15 is extensionally Gergonne-family; fixed vectors cover all 52
  targets. The mislabeled mechanism was replaced (t18).
- Session 8: session 7's "law cannot apply at N ≡ 2" was wrong; the
  universal form (t20) covers every residue.
- Item 3: the former's first fit was refuted by its own auto-derived
  battery; fixed by two-pass extraction and grid diversity.
- Item 4: the laundering demo showed a curated adversary awarding a
  false ROBUST stamp that the derived schedule kills at a floor probe.
- Item 6, three layers deep: a refuter floor probe scoped an
  overbroad claim; a densified grid plus the repair loop fixed
  off-grid tree aliasing; and the repair loop's unit test exposed the
  scheduler's residue blindness.
- Item 7: the audit's first two catches were itself — the mechanism
  entry self-flagged, and the last library entry's body swallowed the
  session log until bodies were cut at the rule.
- Item 8: the proof kernel refused a certificate (residual −1) and
  forced the missing a = b−1 empty-run case into the analysis.

## Where things stand

- 35 library entries; 24 runnable proof files in `tricks/`; 21
  commits on `main` through the queue's completion; every acceptance
  ledger green.
- One THEOREM: the general-b radix law, proven and separately
  verified at ~76k cases across b = 2..8 plus abstract packets.
- The performable headlines: a full-deck any-card-any-number effect
  in six physical steps (b=6, r=3, bucket rule t23), and the
  four-deal quarter-bucket version (t21). [HOWTO.md](HOWTO.md) has
  the performance protocols.
- Strongest new-result candidates (per the provenance ledger): the
  two-card agreement conservation law and the uneven-pile double
  reveals (t16/t17), with no trace found under the logged queries.
- Machine products with honest labels: the Mongean position law
  (rediscovery, pipeline validation) and the reversed-rest pickup
  laws (likely new for N not divisible by b; the divisible slice is
  charted territory).
- The status ladder is fully populated: REFUTED specimens with
  witnesses, graded conjectures with envelopes, and one theorem. The
  refuter still cannot promote anything to THEOREM; only a proof
  artifact can.

## Known limits and open work

Provenance is web-search only; magic-literature databases and
paywalled journals were not consulted, and the records say so. The
proof is semi-formal: three prose steps (discrete intermediate value,
the round induction, the backward/forward duality) would become kernel
steps in a proof-assistant port. The generator knows one question
schema; the backlog (tasks.md) lists schema v2 (targets, multi-card
state, shuffle classes, impossibility probes) and grammar v2 for cut
compositions. The paused mathematics queue — the exact (b, N, r)
frontier, the 13-card reactive double reveal, the even-pile
adaptive-target double trick — is unblocked and waiting.
