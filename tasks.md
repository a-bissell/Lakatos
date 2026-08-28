# Task queue — ENGINE TRACK (novel-finding engine)

Goal: automate the loop that sessions 5-11 executed by hand
(rediscover -> mutate -> compose -> synthesize -> notice structure ->
closed form -> escalate -> frontier), with the guardrails live. Ordered so
every piece is exercised against real library content before the
generator runs.

## Engine queue

1. HARNESS: abstract packets. verify()/verify_prop() are hardwired to
   make_deck() (52 cards) — we hit the wall at b=8/N=64 and silently
   shrank the grid. Add a deck_factory parameter (default make_deck,
   fully backward compatible) + make_packet(N) primitive + unit checks;
   demonstrate by extending the general-b law grid past 52 (tight fits
   (8,64,3), (9,81,3)).
2. ORACLE: library-as-known. Generate recognizers FROM committed laws —
   extensional match "is this candidate's (card, n) -> outcome map an
   instance of [[general-b-radix-law]] (any b, any fixed/bucketed
   digits)?" — so a generator cannot re-derive t18-t23 and have it count
   as novel. Wire into novelty_oracle with the same log-and-suppress +
   abstain policy; acceptance test: t18/t19/t20/t21/t22/t23 all MATCH,
   t16/t17 (multi-card) still route onward.
3. ~~CONJECTURE FORMER~~ DONE (session 13, former.py +
   former_acceptance.py + t25): black-box map extraction, exact
   rational fits, model trees over atom comparisons, auto battery,
   model-based planner. Acceptance 6/6 — general-b law re-derived
   unaided (no-hints guard enforced mechanically); first attempt
   REFUTED by own battery (q0-pocket overfit), fixed via two-pass
   extraction + grid diversity.
4. ~~REFUTER: automation~~ DONE (session 14, refuter_auto.py +
   refuter_battery.py + refute() grading upgrade): schedules derived
   from parameter signatures (floor probes, multi-anchor walks,
   envelope-edge bisection, no-silent-caps reports); 6 library entries
   -> Conjecture objects; whole-library ladder 7/7, 3.67M cases, 101s,
   all envelopes extended. Laundering demo: curated adversary stamps a
   false ROBUST, derived schedule refutes at a floor probe.
5. ~~INTEGRATION LOOP~~ DONE (session 14, engine.py): pipeline chained
   with candidate-atomic budgets (every skip named), suppressed-log
   drift metric, 8 dispositions, dry-run-as-acceptance 9/9. First
   autonomous product: Mongean position law (SURVIVOR, envelope
   N=1500). Generator slot is an interface awaiting item 6.
6. ~~GENERATOR v1~~ DONE (session 14, generator.py): round-position-law
   schema over existing ops, oracle-ignorant emission, extensional
   dedup; metric met 11/11 — 6/9 suppressed across 3 families, 2
   NOT_MATCHED survivors at ROBUST (reversed-rest pickup laws b=3/4,
   envelopes N>5,000), cut-then-deal honestly refused. Engine gained
   the bounded repair loop; derive_schedule gained residue probes.
   v2 backlog: more schemas (targets, multi-card, shuffle classes,
   impossibility probes); grammar v2 for floor((x-k)/b) families
   (cut compositions).
7. PROVENANCE: per-entry literature log (queries run, sources checked,
   date) so "likely new" claims are auditable like verify() counts.
8. PROOF STEP: formalize the general-b law derivation (pile-size algebra
   -> preimage contiguity -> midpoint recursion) at least semi-formally;
   first THEOREM-status entry, validating the ladder's top rung.

## Mathematics backlog (paused, unblocked as engine items land)

- Exact necessary (b, N, r) frontier (unblocked by item 1; conjecture
  reachable ~ min(N, k*b^2) at r=3).
- 13-card reactive double reveal: SAT/annealing or impossibility proof.
- Even-pile double trick with adaptively announced targets
  ([[two-card-agreement-conservation]] used positively).
- Cut-invariant openers; Gilbreath x elimination interaction;
  under-down / k=3 Josephus family.

## Budgets

- Per task: <= 8 verify() runs, hard cap 12 procedure steps for tricks.
- Global per session: stop at 3 commits or 3 consecutive dry tasks.
