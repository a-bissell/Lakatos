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
7. ~~PROVENANCE~~ DONE (session 15, PROVENANCE.md +
   provenance_audit.py): 9 dated records (12 queries, 4 fetches, 21
   sources) covering 17 entries; audit enforces coverage, verdict
   vocabulary (KNOWN / KNOWN-FAMILY / NOT-FOUND), KNOWN-acknowledgment,
   and no stale tags — mechanically, with unit checks for 7 failure
   modes. Headline: Mongean law is a REDISCOVERY (Monge 1773) — entry
   corrected; uneven-radix family (t19-t23) and reversed-rest laws
   scoped KNOWN-FAMILY (even-N slice charted, uneven-N forms not
   found); two-card shared-gather NOT-FOUND (strongest candidates).
   Known limit: web search only; magic-literature databases and
   paywalled journals not consulted.
8. ~~PROOF STEP~~ DONE (session 15, PROOF.md + proof.py): general-b
   law proven over the whole hypothesis region (b >= 2, N >= b,
   b^(r-1) >= N) — envelope |z_k| <= N + (b-2)b^(k-1) makes H3 the
   EXACT zero-slack coverage condition. Machine checks C1-C10 (Farkas
   certificates + exact polynomial identities, simulator grounding,
   27,700 fresh verify() cases at boundary-tight configs incl.
   b^(r-1) = N); prose steps P1-P3 documented. First THEOREM-status
   entry; refuter grading intentionally still tops at
   ROBUST_CONJECTURE (only a proof artifact promotes).

ENGINE QUEUE COMPLETE (items 1-8, sessions 12-15).

## Post-queue theorems

- ~~Two-card agreement conservation~~ THEOREM #2 (session 16,
  PROOF_conservation.md + proof_conservation.py): proven for all
  b >= 2, N = b^m, every round count, every strategy — strengthened
  to exact one-step pattern rotation per round; evenness shown
  necessary by a concrete uneven violation. First impossibility
  theorem.
- Candidate theorem #3: reversed-rest pickups. GATE CHECK DONE
  (session 16, scratchpad rr_contiguity.py, 30 configs b=3..7 all
  residues): two families distinguished. (A) The generator survivors'
  literal family (pile-IDENTITY a on top, card-independent) is a
  bijection family — single-target preimages trivial, interval
  preimages scatter (excess spread up to 22), so no fixed-vector
  targeting exists there; proving the survivors' round law needs only
  item-8 Lemma-2 concatenation algebra, no contiguity. (B) The
  rank-parameterized card-dependent sibling (pointed pile inserted at
  rank c, others largest-first) has ALL single-target preimages = b
  consecutive positions and adjacent targets tile (425 preimages, 0
  failures; control gather_position also clean) — the full item-8
  playbook (midpoint recursion, corr-analog, envelope) applies.
  Family B == gather_position at even N and edge ranks, differs at
  EVERY uneven-N interior-rank pair (74/74 in grid): the new content
  is exactly the uneven regime the literature search found silent.
  Next session: derive corr_rr(c), state theorem #3 (targeting law
  for largest-first pickups), run the playbook.

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
