# Task queue — Self-Working Trick Deriver

Popped tasks move to LIBRARY.md's session log. Seeded per curriculum order.

## Next up

1. REFINE: compress the [[uneven-pile-adaptive-targeting]] strategy trees
   into a human-performable rule (pattern-mine the 52 trees for structure:
   is the placement a function of (round, observed pile, target digit)?),
   or prove no closed form exists within the op set. Success upgrades its
   simplicity score from 1; failure bounds the mechanism honestly.
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
