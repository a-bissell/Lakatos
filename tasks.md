# Task queue — Self-Working Trick Deriver

Popped tasks move to LIBRARY.md's session log. Seeded per curriculum order.

## Next up

1. SYNTHESIZE: the GENERAL-b radix law — conjecture (from b=3 t20 and
   b=4 t21): for any pile count b, z <- -bz + (2a-(b-1))N + correction,
   digit = argmin |new z|, validity b^(r-1) >= N. Derive the correction
   table for general (b, N mod b), verify a b=5 grid (5^2=25 covers 25,
   5^3 covers 125 — full deck in THREE deals with 5 piles?), and if it
   holds, commit the one-law-for-all-(b,N) form. Also map the exact
   NECESSARY r-frontier (both b=3 and b=4 have passes below the
   sufficient bound and fundamental failures near it).
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
