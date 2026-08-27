# Task queue — Self-Working Trick Deriver

Popped tasks move to LIBRARY.md's session log. Seeded per curriculum order.

## Next up

1. INVARIANT: the exact necessary (b, N, r) frontier for
   [[general-b-radix-law]]. Data so far at r=3, N=52: b=4 caps at 16
   (= b^2) reachable, b=5 at 50 (= 2b^2), b=6 full — conjecture:
   reachable-target count ~ min(N, k*b^2) with k depending on rho/drift.
   Sweep (b, N, r) systematically via the cheap enumerate_reachable and
   fit the frontier; a closed-form necessary condition would finish the
   family. Also: can the law's GREEDY ever fail where fixed vectors
   exist below the bound? (No case seen yet — find one or explain why.)
2. SYNTHESIZE: cut-invariant opener. Cyclic stacks survive straight cuts
   (rotation). Prefix verified tricks with "spectator cuts as many times as
   they like": verify [[gilbreath-suit-divination]] with all 52 pre-cut
   offsets added to the domain, and check which targeting tricks tolerate a
   pre-cut with a compensating placement adjustment.
3. REFINE: (a) reactive strategy for the 13-card double reveal ("think of
   any spade") — smarter search than distance-pruned greedy (SAT/CP
   encoding, or simulated annealing over table space), or prove no
   reactive table exists at rounds 4-5; (b) exploit
   [[two-card-agreement-conservation]] positively: an even-pile double
   trick whose TARGETS adapt to the observed agreement pattern ("your
   cards will meet at positions I'll now announce"); (c) pattern-mine the
   47-entry N=11 crib ([[double-reveal-performable]]) for a human rule.
4. MUTATE: [[any-card-any-packet-size]] with an under-down deal (first card
   UNDER) and with k=3 elimination ("down, down, under") — re-derive J
   variants, re-verify, commit the family.
5. INVARIANT: partial-deck Gilbreath — after the riffle, does the block
   property survive dealing off the top half and down-under-ing it? Probe
   what structure elimination deals preserve from cyclic stacks.

## Budgets

- Per task: ≤ 8 verify() runs, hard cap 12 procedure steps.
- Global per session: stop at 3 novel commits or 3 consecutive dry tasks.
