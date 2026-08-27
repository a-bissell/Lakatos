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
3. CONJECTURE FORMER: mechanize the productive middle step — enumerate a
   candidate's behavior map, fit affine-in-floor(x/b) forms with residue
   case-splits, emit a parameterized closed-form conjecture + auto
   verification grid, hand survivors to the refuter. Acceptance: it must
   re-derive the general-b law from raw round maps without hints.
4. REFUTER: automation. Derive attack schedules from a conjecture's
   parameter signature (monotone escalation on every axis, no curated
   lists); generate Conjecture objects from LIBRARY entries; re-run the
   ladder over the whole library as a regression battery.
5. INTEGRATION LOOP: generator -> oracle -> conjecture-former -> refuter
   with per-run budgets and the suppressed log as the live drift metric.
   Ship as a single runnable (engine.py) with a dry-run mode.
6. GENERATOR v1: question schemas over the existing op vocabulary
   (targets, constraints, multi-card state, shuffle classes,
   impossibility probes) — NOT new primitives. Success metric: suppressed
   log shows exploration, and at least one NOT_MATCHED survivor reaches
   ROBUST_CONJECTURE.
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
