# LIBRARY — verified primitives, invariants, and tricks

All entries verified by `verify()` in [deck_sim.py](deck_sim.py) on 2026-08-27.
Runnable proofs live in `tricks/`. Nothing enters this file without a passing
verify() run recorded below.

---

### gather_position
kind: primitive
domain |D|: n/a (deterministic op)
invariant: n/a
procedure: `deck_sim.gather_position(piles, chosen_idx, above)` — reassemble
  with exactly `above` other piles on top of the chosen pile, relative order
  of others preserved. Generalizes `gather_middle` (== above=1 with 3 piles).
scores: n/a (primitive)
verified: 2026-08-27, `_unit_gather_position()` (6 asserts incl. equivalence
  with gather_middle), runs at import time
canonical_form: gather(above=k)
notes: the placement knob that drives all radix targeting below.

### down-under-survivor
kind: primitive
domain |D|: n/a (deterministic op)
invariant: n/a
procedure: `deck_sim.down_under_survivor(deck)` — top card down (table), next
  under (bottom), until one remains in hand; returns it.
scores: n/a (primitive)
verified: 2026-08-27, `_unit_down_under_survivor()` (4 hand-derived asserts),
  runs at import time
canonical_form: josephus(k=2, first=down)
notes: shipped `down_under_deal` has an ambiguous survivor path (with one
  card left and down=True it deals the survivor to the table and returns an
  empty hand) — left untouched; use this primitive instead. Survivor of a
  16-card packet = position 16 (bottom card).

### middle-gather-center-convergence
kind: invariant (also the classic 21/27-card trick family)
domain |D|: any of the n cards in play (n = 21: 21 cases; n = 27: 27 cases)
invariant: repeated (deal into 3 piles, gather chosen pile in middle) is a
  contraction toward the packet center, index (n-1)/2
procedure: [tricks/t2_27_center.py](tricks/t2_27_center.py)
scores: freedom=2, opacity=3, simplicity=4, elegance=4
verified: 2026-08-27, verify() ok over 27 cases (n=27, 3 rounds); boundary
  sweep: PASS for n = 9(r2), 15(r3), 21(r3), 27(r3), 33(r4), 39(r4), 45(r4),
  51(r4)
canonical_form: contraction(deal3-middle)^r -> center
notes: rounds needed ≈ ceil(log3 n). Every 3·odd packet size up to 51
  converges — no failure boundary found in range. Rediscovery of the known
  21-card trick (harness confirmation) plus its size generalization.

### radix-placement-law
kind: invariant
domain |D|: (b,r) configs × all (card, n) pairs — 7 configs, 5,616 total cases
invariant: with N = b^r cards and r rounds of deal-into-b + gather with p_i
  piles above the spectator's pile, final 1-indexed position is n where
  n-1 has base-b digits d_i and
      p_i = d_i           if an EVEN number of deals follow round i
      p_i = (b-1) - d_i   if an ODD  number of deals follow round i
  (each deal reverses pile order; reversals after round i compose to parity)
procedure: [tricks/t6_radix_law.py](tricks/t6_radix_law.py) `law_placements`
scores: n/a (invariant)
verified: 2026-08-27, verify() ok for (b,r) = (2,4) 256, (3,2) 81, (5,2) 625,
  (2,5) 1024, (7,2) 2401 cases; plus (3,3) 729 in t3 and (4,2) 256 in t5
canonical_form: radix-placement(b, r)
notes: derived by sub-search inversion in t3/t5, then generalized and
  verified. This single law generates every targeting trick below.

### gergonne-any-card-any-number
kind: trick
domain |D|: 729 — any of 27 cards AND any position n in 1..27
invariant: [[radix-placement-law]] with b=3, r=3 (p = d0, 2-d1, d2)
procedure: [tricks/t3_gergonne_any_number.py](tricks/t3_gergonne_any_number.py)
scores: freedom=5, opacity=4, simplicity=3, elegance=5
verified: 2026-08-27, verify() ok over 729 cases
canonical_form: radix-placement(3, 3)
notes: rediscovery of Gergonne's pile problem in full generality. Spectator
  only thinks of a card and names n; performer does 3 deals and 3 pickups.
  Performer memory load: base-3 digits of n-1 with middle digit flipped.

### center-then-digit-sum-force
kind: trick
domain |D|: 210 — any of 21 cards AND any number n in 10..19
invariant: center convergence pins card at position 11; transfer-2 shifts to
  position 9; n - digitsum(n) = 9 for all n in 10..19 (casting out nines)
procedure: [tricks/t4_center_digitsum_force.py](tricks/t4_center_digitsum_force.py)
scores: freedom=4, opacity=4, simplicity=4, elegance=4
verified: 2026-08-27, verify() ok over 210 cases
canonical_form: contraction(deal3-middle)^3 ∘ shift(2) ∘ nines-force
notes: composition of [[middle-gather-center-convergence]] with the classic
  10-20 digit-sum force. The number feels free but any n in 10..19 works;
  the "count off n, then count off its digit sum" patter hides the mod-9
  invariant well. NOVEL COMMIT #2 (new canonical composition for library).

### radix4-targeting-two-deals
kind: trick (parametric variant, committed for its economy)
domain |D|: 256 — any of 16 cards AND any position n in 1..16
invariant: [[radix-placement-law]] with b=4, r=2 (p = 3-d0, d1)
procedure: [tricks/t5_radix4_down_under.py](tricks/t5_radix4_down_under.py) Part A
scores: freedom=5, opacity=4, simplicity=4, elegance=4
verified: 2026-08-27, verify() ok over 256 cases
canonical_form: radix-placement(4, 2)
notes: isomorph of [[gergonne-any-card-any-number]] under the law's canonical
  family — logged as a MUTATE, not counted as novel. Its value: only TWO
  deals for full any-card-any-number freedom.

### radix-target-down-under-reveal
kind: trick
domain |D|: 16 — any of 16 cards (no other choice; the reveal is the hook)
invariant: [[radix-placement-law]] (4,2) targets the card to position 16 =
  the [[down-under-survivor]] position of a 16-card packet
procedure: [tricks/t5_radix4_down_under.py](tricks/t5_radix4_down_under.py) Part B
scores: freedom=2, opacity=5, simplicity=4, elegance=5
verified: 2026-08-27, verify() ok over 16 cases
canonical_form: radix-placement(4,2) ∘ josephus(k=2)
notes: spectator only thinks of a card and twice points at a pile; performer
  never counts visibly — two deals, two pickups, then the down-under deal
  "randomly" eliminates everything but their card. NOVEL COMMIT #3 (new
  canonical composition: targeting ∘ elimination).

### riffle-merge
kind: primitive
domain |D|: n/a (deterministic op; quantifying over all patterns models every
  possible spectator riffle)
invariant: n/a
procedure: `deck_sim.riffle_merge(a, b, pattern)` — interleave two packets
  per a 0/1 pattern (0 pulls from a, 1 from b)
scores: n/a (primitive)
verified: 2026-08-27 session 2, `_unit_riffle_merge()` (4 asserts), import time
canonical_form: riffle(pattern)
notes: first op class where the SPECTATOR mixes the deck. Companion harness
  extension `verify_prop()` (unit-checked) verifies structural-property
  effects that verify() (reveal == chosen card) cannot express.

### spell-your-own-card
kind: trick
domain |D|: 16 — any of 16 stacked cards
invariant: stack encodes spell length in position mod 4 (positions 0,1 mod 4
  hold 11-letter names, 2,3 mod 4 hold 12-letter names); the first
  pile-pointing reveals start mod 4, so an ADAPTIVE first pickup (1 pile
  above for the 11-class, 0 for the 12-class; second pickup constant 2)
  drops every card at a position equal to its own name's length, via
  [[radix-placement-law]] (4,2)
procedure: [tricks/t7_spell_your_card.py](tricks/t7_spell_your_card.py)
scores: freedom=3, opacity=5, simplicity=4, elegance=5
verified: 2026-08-27 session 2, verify() ok over 16 cases
canonical_form: stack-encoded-target ∘ adaptive-radix-placement(4,2) ∘ spell
canonical note: NOVEL COMMIT (session 2, #1): adaptivity + stack encoding is
  a new mechanism class in this library — the procedure branches on the
  spectator's public pile answer, never on the card.
notes: spell-length census of the full deck: {10:4, 11:13, 12:14, 13:12,
  14:5, 15:4} — only the 11/12 pair has two classes with >= 8 members, so
  this 16-card design is essentially forced. Uniform 3-round 27-card
  versions are IMPOSSIBLE for the 11/12 pair: p0 would need to split 13/14
  cards across residue classes mod 3 of size 9 each.

### mixed-radix-full-deck-targeting
kind: trick + invariant extension
domain |D|: 2704 — any of 52 cards AND any position n in 1..52, full deck
invariant: [[radix-placement-law]] extends to mixed radix: 52 = 4 x 13,
  n-1 = d0 + 4*d1; deal into 4 piles then 13 piles (or 13 then 4), with the
  parity rule applied per round in that round's own base:
  p0 = (b1-1) - d0 (a deal follows), p1 = d1 (none follows)
procedure: [tricks/t8_mixed_radix_52.py](tricks/t8_mixed_radix_52.py)
scores: freedom=5, opacity=4, simplicity=3, elegance=5
verified: 2026-08-27 session 2, verify() ok over 2704 cases for (4,13) AND
  2704 for (13,4); closed form matched sub-search map 52/52 in both orders
canonical_form: radix-placement(mixed: b1 x b2)
canonical note: NOVEL COMMIT (session 2, #2). Largest |D| in the library;
  subsumes queue item "any card, any number 1..20 from 52 in <= 3 deals".
notes: TWO deals suffice for the full deck. Performability cost: one round
  needs 13 piles (or 4 piles of 13). Spectator thinks of a card and names
  any n in 1..52; performer's memory load: n-1 = d0 + 4*d1, complement d0.

### gilbreath-principle
kind: invariant + property trick
domain |D|: exhaustive 2^N per config: all deal-off sizes m in 0..N x all
  riffle interleavings; N=12 and N=16, k=2 and k=4 (139,264 total cases)
invariant: deck cyclic with period k; spectator deals off ANY m (dealing
  reverses) and riffles ANYHOW into the rest; every successive block of k
  from the top still contains one card of each of the k classes
procedure: [tricks/t9_gilbreath.py](tricks/t9_gilbreath.py)
scores: freedom=5, opacity=5, simplicity=5, elegance=5
verified: 2026-08-27 session 2, verify_prop() ok: N=12 k=2 (4096), N=12 k=4
  (4096), N=16 k=2 (65536), N=16 k=4 (65536)
canonical_form: cyclic-stack(k) ∘ deal-off-reverse ∘ riffle -> k-blocks
canonical note: NOVEL COMMIT (session 2, #3): first spectator-shuffle
  invariant in the library; needed verify_prop, a new harness capability.
notes: verified exhaustively only at N=12,16 — the library records exactly
  what was brute-forced; literature says size-independent (Gilbreath 1958,
  1966), but no entry here may claim beyond its verified domain. Performance
  form: suit-cycle stack, spectator deals ~half and riffles, performer deals
  quartets and each holds all four suits.

### merged-digitsum-force
kind: trick (MUTATE of center-then-digit-sum-force; supersedes it)
domain |D|: 486 — any of 27 cards AND any number n in 10..27
invariant: n - digitsum(n) is the largest multiple of 9 below n — constant
  per decade (9 for 10..19, 18 for 20..27) — so [[radix-placement-law]]
  placements (2,0,0) / (2,0,1), differing only in the LAST pickup, absorb
  t4's transfer-2 adjustment entirely
procedure: [tricks/t10_merged_digitsum.py](tricks/t10_merged_digitsum.py)
scores: freedom=4, opacity=4, simplicity=4, elegance=5
verified: 2026-08-27 session 3, verify() ok over 486 cases
canonical_form: radix-placement(3,3) ∘ nines-force
notes: strictly dominates t4 (210 -> 486 cases, one fewer step); n may be
  named any time before the third pickup. Mutate commit, not novel.

### gilbreath-suit-divination
kind: trick
domain |D|: exhaustive — N=12: 49,152 (pattern x quartet x removal);
  N=16: 65,536 patterns x all 16 quartet/removal choices = 1,048,576
invariant: [[gilbreath-principle]] — every post-riffle quartet holds all
  four suits, so the suit missing from any 3 names the removed card's suit
procedure: [tricks/t11_gilbreath_suit_divination.py](tricks/t11_gilbreath_suit_divination.py)
scores: freedom=5, opacity=5, simplicity=5, elegance=5
verified: 2026-08-27 session 3, verify_prop() ok over both domains
canonical_form: cyclic-stack(4) ∘ riffle ∘ remove-one -> suit-reveal
canonical note: NOVEL COMMIT (session 3, #1): first spectator-shuffle trick
  with a reveal (t9 committed only the bare invariant).
notes: spectator shuffles, chooses the quartet AND the removed card;
  performer computes nothing but "which suit is missing".

### spell-48
kind: trick (extension of spell-your-own-card; same canonical family)
domain |D|: 48 — any of 48 stacked cards (4 mixed-length fillers excluded)
invariant: (13,4) mixed-radix targeting with the stack encoding spell length
  in position mod 13; 13 classes of 4, both pickups determined by the first
  pile pointed at
procedure: [tricks/t12_spell_48.py](tricks/t12_spell_48.py)
scores: freedom=4, opacity=5, simplicity=2, elegance=4
verified: 2026-08-27 session 3, verify() ok over 48 cases
canonical_form: stack-encoded-target ∘ adaptive-radix-placement(13,4) ∘ spell
notes: 48 is the census ceiling for this design ({10:4, 11:13, 12:14,
  13:12, 14:5, 15:4} fills only 12 uniform quadruple classes). Not novel —
  isomorph of [[spell-your-own-card]] at scale. Simplicity cost: dealing 13
  piles and a 6-row pickup table.

### down-under-survivor-position
kind: invariant
domain |D|: n in 1..52 (all packet sizes)
invariant: survivor of a down-under deal on n cards sits at 1-indexed
  position 2L where n = 2^m + L, 0 < L < 2^m (position n when L = 0)
procedure: [tricks/t13_josephus_packet.py](tricks/t13_josephus_packet.py) Part A
scores: n/a (invariant)
verified: 2026-08-27 session 3, closed form == simulator for all n in 1..52
canonical_form: josephus(k=2, first=down) closed form
notes: the Josephus-problem special case; powers the composition below.

### any-card-any-packet-size
kind: trick
domain |D|: 2704 — any of 52 cards AND any packet size n in 1..52
invariant: [[mixed-radix-full-deck-targeting]] sends the card to position
  n + 1 - J(n); dealing off n cards reverses, carrying it to packet
  position J(n) = [[down-under-survivor-position]]; the elimination deal
  then "randomly" leaves exactly that card
procedure: [tricks/t13_josephus_packet.py](tricks/t13_josephus_packet.py) Part B
scores: freedom=5, opacity=5, simplicity=3, elegance=5
verified: 2026-08-27 session 3, verify() ok over 2704 cases
canonical_form: radix-placement(mixed) ∘ deal-off-reverse ∘ josephus(n)
canonical note: NOVEL COMMIT (session 3, #2): first variable-size
  elimination finale; ties t8 for largest |D| in the library.
notes: spectator's number changes the TARGET, not the finale — the
  down-under deal reads as pure chance.

### two-deal-size-characterization
kind: invariant
domain |D|: 6 factorizations x full (card, n) grids = 15,214 cases
invariant: [[radix-placement-law]] (mixed form) holds for EVERY tested
  factorization N = b1 x b2: (5,10), (6,8), (7,7), (2,26), (26,2), (3,17)
procedure: [tricks/t14_size_characterization.py](tricks/t14_size_characterization.py)
scores: n/a (invariant)
verified: 2026-08-27 session 3, verify() ok on all six grids
canonical_form: radix-placement(mixed: any b1 x b2)
notes: any composite deck size admits two-deal any-card-any-number
  targeting; 52 has four two-deal realizations. UNEVEN piles break the
  algebra: 52 into 3 piles (18/17/17) has 0/27 start-independent placement
  vectors at 3 rounds, 30/81 at 4 rounds reaching only 30/52 positions,
  failing vectors spreading over exactly 2 finals.

### uneven-pile-adaptive-targeting
kind: trick + method
domain |D|: 2704 — any of 52 cards AND any position n in 1..52, using ONLY
  3 piles (sizes 18/17/17) and 5 deals
invariant: none in closed form — a per-target adaptive strategy (placements
  conditioned on the observed pile answers) found by backward induction
  over position-sets: S is controllable iff every pile-class of S has some
  placement whose image is controllable one round deeper
procedure: [tricks/t15_uneven_adaptive.py](tricks/t15_uneven_adaptive.py)
scores: freedom=5, opacity=4, simplicity=1, elegance=3
verified: 2026-08-27 session 3, verify() ok over 2704 cases; strategy
  search proves 4 rounds cap at 30/52 targets even adaptively (image
  bottleneck, not information), 5 rounds cover 52/52
canonical_form: adaptive-strategy-targeting(uneven piles)
canonical note: NOVEL COMMIT (session 3, #3): new MECHANISM class — the
  first entry whose procedure is a searched strategy tree rather than a
  closed-form rule. Existence result: uneven piles are defeatable.
notes: unperformable from memory (52 strategy trees, up to ~3^5 histories
  each) — needs a crib; committed for the method and the existence proof.
  Open refinement: compress the strategy to a human rule, or prove none
  exists. The backward-induction sub-search is itself reusable.

### gather-order
kind: primitive
domain |D|: n/a (deterministic op)
invariant: n/a
procedure: `deck_sim.gather_order(piles, order)` — stack piles in an
  arbitrary given order (first = top); the fully general pickup
scores: n/a (primitive)
verified: 2026-08-27 session 4, `_unit_gather_order()` (equivalence with
  gather_position over all chosen/above combos), runs at import time
canonical_form: gather(permutation)
notes: the two-card problem needs the full b! action space; gather_position
  is the special case preserving the others' relative order.

### two-card-agreement-conservation
kind: invariant (impossibility theorem)
domain |D|: all 702 ordered target pairs x all 702 start pairs, N=27,
  b=3 even piles, rounds 3, 4, 5 — full-information backward reachability
invariant: two cards dealt into the same pile receive EQUAL new position
  digits, cards in different piles DISTINCT ones (pile levels are a
  bijection), so the pattern of base-3 digit positions where the two
  cards' positions agree is CONSERVED (permuted per round) by EVERY
  gathering strategy
procedure: [tricks/t16_double_reveal.py](tricks/t16_double_reveal.py) part_a
scores: n/a (invariant)
verified: 2026-08-27 session 4: for every target pair at every tested round
  count, the reachable set is exactly one agreement-pattern class; 0
  violations over 702 x 3 exhaustive reachability maps
canonical_form: two-card radix conservation (even piles)
notes: consequence — arbitrary double targeting with even piles is
  impossible at ANY depth. Positive use: targets whose pattern matches the
  (observed) start pattern ARE reachable; an adaptive-target double trick
  on even piles remains open (queue). No trace of this two-card question
  found in the Gergonne literature.

### double-reveal-uneven
kind: trick + method
domain |D|: 2652 — every ordered pair of DISTINCT thought-of cards from a
  full 52-card deck (spectator A's card to top, B's to bottom)
invariant: none conserved — uneven piles (18/17/17) dissolve
  [[two-card-agreement-conservation]]; a per-observation adaptive strategy
  (backward induction on the pair space, full 3! ordering actions) exists
  at 8 rounds. Full-information reachability: 6/36/216/997/2009/2597/2652
  at rounds 1-7; 7 rounds is universally reachable but info-limited — the
  observation constraint costs exactly one extra round.
procedure: [tricks/t16_double_reveal.py](tricks/t16_double_reveal.py) part_b
scores: freedom=5, opacity=5, simplicity=0, elegance=3
verified: 2026-08-27 session 4, verify() ok TWICE over 2652 ordered pairs
  (top reveal and bottom reveal)
canonical_form: adaptive-strategy-targeting(pair state, uneven piles)
canonical note: NOVEL COMMIT (session 4, #1): first multi-spectator entry;
  strongest novelty candidate in the library (no literature trace found
  for shared-gather two-card targeting or its obstruction).
notes: VIOLATES the 12-step performability cap (8 deals + 8 pickups = 16)
  and needs machine-sized strategy trees — committed as existence result
  and method, like [[uneven-pile-adaptive-targeting]]. Open: minimal
  rounds for other target pairs; strategy compression; whether a smaller
  uneven deck (e.g. 20 cards, piles 7/7/6) gives a performable version.

---

## Session log

- 2026-08-27 session 4 (single task, user-directed): t16 double reveal.
  Part A: two-card agreement conservation verified exhaustively (702
  targets x 3 depths, 0 violations) — even-pile double targeting
  impossible. Part B: uneven piles dissolve the obstruction; adaptive
  strategy at 8 rounds; end-to-end PASS 2x2652. New primitive gather_order.
  1 novel commit + 1 impossibility invariant. Zero failed verifies (the
  round-7 'none' was the search correctly reporting infeasibility).
- 2026-08-27 session 3: budgets N=3, M=3. All five queue items run: t10
  merged digit-sum force (PASS 486) [mutate], t11 Gilbreath suit divination
  (PASS 49,152 + 1,048,576) [NOVEL #1], t12 48-card spelling (PASS 48)
  [mutate], t13 J(n) invariant + any-card-any-packet-size (PASS 52 + 2704)
  [NOVEL #2], t14 size characterization (PASS 15,214) + uneven-pile
  diagnosis, t15 adaptive uneven-pile targeting (PASS 2704, 5 rounds)
  [NOVEL #3]. Global stop: N reached; queue fully consumed. Zero failed
  verifies. No harness changes this session.
- 2026-08-27 session 2: budgets N=3, M=3. Tasks run from tasks.md queue: t7
  spell-your-own-card (PASS 16) [NOVEL #1], t8 mixed-radix full-deck
  targeting (PASS 2x2704) [NOVEL #2], t9 Gilbreath principle (PASS 139,264
  exhaustive) [NOVEL #3]. Global stop: N reached. Zero failed verifies.
  New primitives: riffle_merge, verify_prop harness extension. Queue item 5
  subsumed by t8; item 4 (t4 merge mutate) still open.
- 2026-08-27: budgets N=3 novel commits, M=3 dry tasks. Tasks run: t1
  harness confirm (PASS 21), t2 mutate (PASS 27 + boundary sweep), t3
  synthesize (PASS 729) [NOVEL #1], t4 compose (PASS 210) [NOVEL #2], t5
  compose (PASS 256 + 16) [NOVEL #3], t6 invariant generalization (PASS
  4,387). Global stop: N reached. Zero failed verifies this session — next
  session should raise ambition (see tasks.md).
