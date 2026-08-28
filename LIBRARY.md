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
  performer computes nothing but "which suit is missing". Suit-based
  Gilbreath reveals are standard repertoire in the literature (Mulcahy,
  AMS feature column) — "NOVEL COMMIT" here means novel to this
  library, per PROVENANCE.md gilbreath-rediscovery.

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
notes: SUPERSEDED as a trick (2026-08-27 session 6) by
  [[fixed-vector-uneven-acaan]]: the session-6 oracle audit discovered that
  fixed relative-placement vectors cover all 52 targets at r=5 — the
  adaptive machinery is unnecessary for the effect. The r<=4 impossibility
  results and the strategy-search METHOD stand.
  Original notes: unperformable from memory (52 strategy trees, up to ~3^5
  histories each) — needs a crib; committed for the method and the
  existence proof.
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

### double-reveal-performable
kind: trick
domain |D|: 110 — every ordered pair of DISTINCT thought-of cards from an
  11-card packet (spectator A's card to top, B's to bottom)
invariant: none in closed form — a REACTIVE strategy: the pickup ordering
  depends ONLY on (round, pile A points at, pile B points at), no history.
  Found by greedy synthesis under full-information distance pruning
  (admissible: every image pair must stay within reach of the remaining
  rounds), deterministic LCG restarts.
procedure: [tricks/t17_small_double_reveal.py](tricks/t17_small_double_reveal.py)
scores: freedom=4, opacity=5, simplicity=4, elegance=4
verified: 2026-08-27 session 5, verify() ok TWICE over 110 ordered pairs
  (A-top and B-bottom); re-verified in-repo after sync on 2026-08-27
canonical_form: adaptive-strategy-targeting(pair, uneven piles, reactive)
canonical note: NOVEL COMMIT (session 5, #1): first PERFORMABLE
  multi-spectator entry — 11 cards, 4 piles (3/3/3/2), 4 deals + 4 pickups
  = 8 steps, and a 47-entry crib (16/12/10/9 rows per round) instead of
  machine-sized trees.
notes: sweep results (min full-info rounds for top/bottom, cap 6):
  b=2 never within 6; b=3: N=8,10,11 need 4, N=13..20 need 5-6;
  b=4: N=9..14 need 3, N=15..19 need 4. Info constraint costs +1 round
  (rounds=3 adaptive-impossible for all b=4 configs tried). N=9, N=10
  have adaptive trees at 4 rounds but no reactive table was found; N=11 is
  the smallest with one. N=13 ("think of any spade") resisted reactive
  search at rounds 4 AND 5 over 100k+ restarts — NOT proven impossible,
  queued. Structural bonus found in the tables: rounds 3-4 contain no
  diagonal observations — the strategy provably separates the two cards
  into distinct piles from round 3 on.
  Reactive tables (observation (pileA,pileB) -> pickup order, top first):
    round 1: (0,0)->1230 (0,1)->1320 (0,2)->2310 (0,3)->3210 (1,0)->0231
             (1,1)->1320 (1,2)->2301 (1,3)->3201 (2,0)->0132 (2,1)->1302
             (2,2)->2103 (2,3)->0312 (3,0)->0213 (3,1)->1023 (3,2)->2103
             (3,3)->1023
    round 2: (0,0)->1023 (0,1)->2130 (0,2)->1230 (0,3)->0123 (1,0)->2130
             (1,1)->2130 (1,2)->2310 (1,3)->1023 (2,0)->2301 (2,1)->0132
             (2,2)->2103 (2,3)->2103
    round 3: (0,1)->1320 (0,2)->2301 (0,3)->3210 (1,0)->0213 (1,2)->2301
             (2,1)->1032 (2,3)->0312 (3,0)->0132 (3,1)->1230 (3,2)->2013
    round 4: (0,1)->0231 (1,0)->1320 (1,2)->1302 (2,0)->2130 (2,1)->2031
             (2,3)->2013 (3,0)->3120 (3,1)->3021 (3,2)->3012

### fixed-vector-uneven-acaan
kind: trick (supersedes the trick claim of [[uneven-pile-adaptive-targeting]])
domain |D|: 2704 — any of 52 cards AND any position n in 1..52, full deck,
  3 uneven piles (18/17/17), FIVE deals, fixed placements
invariant: for every target index a start-independent fixed 5-vector of
  relative placements ("a piles above the pointed pile") exists at r=5 —
  discovered by the session-6 oracle audit after t14/t15 had checked only
  r=3 (0 vectors) and r=4 (30/52 targets) before adopting strategy trees
procedure: [tricks/t18_fixed_vector_acaan.py](tricks/t18_fixed_vector_acaan.py)
scores: freedom=5, opacity=4, simplicity=3, elegance=4
verified: 2026-08-27 session 6, verify() ok over 2704 cases (also verified
  independently in the branch audit, oracle branch AUDIT.md)
canonical_form: radix-placement(uneven, fixed) — Gergonne-family
canonical note: NOT novel — extensionally a fixed-placement Gergonne-family
  instance (the novelty oracle's MATCHED verdict on t15, audited TRUE).
  Committed as the honest replacement for a mislabeled mechanism.
notes: 10 steps. CRIB-FREE as of session 7: [[alternating-radix-law]]
  generates the vector for any named n by a 5-step mental recursion
  (simplicity effectively 3 -> 4). Lesson recorded:
  t15's "adaptive machinery required" was an overclaim by omission — the
  r=5 fixed-vector check was never run until the oracle audit forced it.

### alternating-radix-law
kind: invariant (closed form; makes [[fixed-vector-uneven-acaan]] crib-free)
domain |D|: 10 configs x full (card, n) grids = 9,349 cases, plus the
  one-round position formula checked exactly for every (position,
  placement) at all 10 deck sizes
invariant: for N ≡ 1 (mod 3) cards dealt into 3 uneven piles, one round of
  "gather with a piles above the pointed pile" acts on the tracked card as
  x' = A - floor(x/3), where A is PILE-INDEPENDENT for a in {1,2}
  (A = 2(N-1)/3 and N-1) — the N ≡ 1 coincidence that makes fixed vectors
  possible. Backward requirement-propagation collapses to a midpoint
  recursion; centered on the deck (y = m - (N-1)/2) it is the
  ALTERNATING-RADIX LAW:
      y <- -3y + a'N + [a'=0],   a' = round(3y/N) clamped to {-1,0,+1}
  computed r times from y = (n-1) - (N-1)/2; digits (a'+1) reversed give
  the pickup vector. The +1 correction when the middle placement is chosen
  is the uneven-pile fingerprint. VALIDITY: 3^(r-1) >= N.
procedure: [tricks/t19_acaan_closed_form.py](tricks/t19_acaan_closed_form.py)
scores: n/a (invariant)
verified: 2026-08-27 session 7, verify() ok for (N, r) = (7,3), (10,4),
  (13,4), (16,4), (22,4), (25,4), (31,5), (40,5), (49,5), (52,5) —
  including the tight boundary fits 25 <= 27 and 49 <= 81. Outside the
  condition the law fails AS PREDICTED, and exhaustive vector enumeration
  shows the boundary is real, not algorithmic: at (10,3) only 9/10 and at
  (13,3) only 10/13 targets are reachable by ANY fixed vector.
canonical_form: Gergonne-dynamics closed form (uneven, N ≡ 1 mod 3)
notes: the mathematical territory (floor-map dynamics of uneven Gergonne
  deals) is charted in the literature; this specific algorithmic form —
  greedy alternating-radix digits, the [a'=0] correction, and the
  3^(r-1) >= N feasibility boundary — was derived and machine-verified
  here and not found published. Open: N ≡ 2 (mod 3), where the a=1 gather
  constant becomes pile-dependent and the law as stated cannot apply.

### universal-radix-law
kind: invariant (extends [[alternating-radix-law]] to EVERY deck size)
domain |D|: 18 deck sizes x full (card, n) grids = 18,223 cases, all three
  residues mod 3, six tight boundary fits; round formula checked exactly
  at all 18 sizes
invariant: session 7's claim that the law "cannot apply as stated" for
  N ≡ 2 (mod 3) was WRONG — the pile-dependent gather constant meshes
  with floor(x/3) so requirement preimages stay contiguous, and the
  midpoint constants are unchanged. Universal integer form (tie-free —
  6m is even, thresholds odd):
      K = (N-2, 2N-1, 3N-2), middle 2N-2 when 3 | N
      m starts at n-1; r times:
        6m < 2N-3 -> digit 0 | between -> digit 1 | 6m > 4N-3 -> digit 2
        then m <- K[digit] - 3m
      digits REVERSED = pickups ("piles above the pointed pile")
  Validity: 3^(r-1) >= N is SUFFICIENT everywhere (18/18 PASS) but not
  necessary: N=12 r=3 passes below it (N ≡ 0 contracts better; its
  correction term is zero), while N=26 r=3 fails fundamentally (6/26
  targets reachable by any vector).
procedure: [tricks/t20_universal_radix_law.py](tricks/t20_universal_radix_law.py)
scores: n/a (invariant)
verified: 2026-08-27 session 8, verify() ok for N = 8,11,14,20,26,35,44,50
  (≡2), 9,12,18,24,27,36,45,51 (≡0), 25,52 (≡1) at r per condition
canonical_form: Gergonne-dynamics closed form (any N, 3 piles)
notes: one mental algorithm now performs ACAAN on ANY packet: r=3 to 9
  cards, r=4 to 27, r=5 to 81. For N = 3^k the classic law (t3/t6) is
  depth-optimal (r=k); the universal law trades depth for universality.
  Performance write-up: [HOWTO.md](HOWTO.md). Open: exact necessary
  r-boundary per residue; the b=4-pile analog.

### four-pile-universal-law
kind: invariant (base-(-4) analog of [[universal-radix-law]])
domain |D|: 24 deck sizes x full (card, n) grids = 24,415 cases, all four
  residues mod 4, 16 tight fits; round formula checked exactly at all 24
invariant: dealing into 4 piles, the gather constants deviate by at most
  one unit across piles and every deviation pattern meshes with
  floor(x/4), keeping requirement preimages contiguous. In doubled
  deck-centered coordinates z = 2(n-1) - (N-1) (always integer):
      z <- -4z + (2a-3)N + 2*delta(N mod 4, a)
      delta: N≡0 (0,0,0,0) · N≡1 (0,2,1,0) · N≡2 (0,2,2,0) · N≡3 (0,1,2,0)
      digit = argmin |new z| (ties -> larger digit); digits reversed =
      pickups. For N=52 (≡ 0: delta = 0, piles deal EVENLY 13/13/13/13)
      the argmin equals the pure quarter-bucket rule (boundaries
      z = -26, 0, +26), checked identical for all 52 targets.
  Validity: 4^(r-1) >= N sufficient (24/24 PASS) and again not necessary
  (N=20, 26 pass at r=3 below it with full enumerated reachability;
  N=17 r=3 fundamentally infeasible, 16/17).
procedure: [tricks/t21_four_pile_law.py](tricks/t21_four_pile_law.py)
scores: n/a (invariant)
verified: 2026-08-27 session 9, verify() ok for 24 (N, r) configs,
  N = 8..52 spanning all residues mod 4
canonical_form: Gergonne-dynamics closed form (any N, 4 piles)
notes: FULL-DECK ACAAN IN FOUR DEALS (8 physical steps, down from 10) —
  the strongest performable form of the family. Suggests the general-b
  conjecture: for any pile count b, z <- -bz + (2a-(b-1))N + correction,
  validity b^(r-1) >= N. Open: prove/refute general b; exact necessary
  r-frontier per (b, residue).

### general-b-radix-law
kind: invariant — STATUS: THEOREM as of 2026-08-28 session 15
  (capstone: unifies [[universal-radix-law]] (b=3) and
  [[four-pile-universal-law]] (b=4) as special cases; proof artifact
  [[general-b-law-theorem]] = PROOF.md + proof.py — sufficiency
  b^(r-1) >= N is now PROVEN over the whole hypothesis region, not
  only verified on tested grids)
domain |D|: 27 new (b, N) configs x full grids = 32,896 cases over
  b = 2, 5, 6, 7, 8 (with t20/t21: every pile count 2..8); round formula
  checked exactly at all 27; 20 of 27 configs were tight fits
invariant: closed form for EVERY pile count, derived from the pile-size
  algebra (N = bq + rho) and the always-contiguous preimage property:
      z <- -b*z + (2a+1-b)*N + 2*corr(a)
      corr(a) = min(a, rho) * (b - max(a+1, rho)),  rho = N mod b
      digit = argmin |new z| (tie -> larger a); digits reversed = pickups
  The single corr expression reproduces every previously verified table
  (b=3: (0,1,0) for rho=1 AND rho=2 — the t20 coincidence explained;
  all four b=4 delta tables; b=2: no correction ever).
  Validity: b^(r-1) >= N sufficient (27/27) and CLEARLY not necessary —
  frontier data at r=3, N=52: b=4 FAIL (16/52 reachable), b=5 FAIL
  (50/52 — two targets fundamentally unreachable), b=6 PASS (52/52),
  b=7 PASS. Minimal three-deal full-deck pile count: SIX.
procedure: [tricks/t22_general_b_law.py](tricks/t22_general_b_law.py)
scores: n/a (invariant)
verified: 2026-08-27 session 10, verify() ok for all 27 in-condition
  configs plus below-condition passes at (5,27,3), (6,45,3), (6,52,3),
  (7,52,3)
canonical_form: Gergonne-dynamics closed form (any N, any b)
notes: FULL-DECK ACAAN IN SIX PHYSICAL STEPS (b=6, r=3) — the most
  efficient performable form found; b=4/r=4 remains the recommended
  human version (quarter-bucket rule). b=2 gives a two-pile binary
  version a spectator could deal themselves (N <= 32 within the step
  cap). ENVELOPE EXTENDED (session 12, t24, abstract packets): tight
  fits (64,8,3), (81,9,3), (81,3,5), (100,10,3), (144,12,3) all PASS —
  47,954 more cases, beyond any physical deck. Open: characterize the
  exact necessary (b, N, r) frontier — the b=5/N=52 near-miss (50/52)
  suggests reachable ~ min(N, 2b^2) at r=3.

### six-pile-bucket-rule
kind: invariant (performance form of [[general-b-radix-law]] at b=6, N=52)
domain |D|: bucket==argmin proven for every integer z in [-400, 400];
  full trick re-verified over all 2704 (card, n) cases via the bucket
  rule alone
invariant: the b=6/N=52/r=3 digit choice reduces to fixed thresholds —
  z <= -35 -> 0 | -34..-17 -> 1 | -16..1 -> 2 | 2..18 -> 3 |
  19..35 -> 4 | >= 36 -> 5, then z <- -6z + (-260,-152,-44,64,164,260)[a].
  Exactly ONE tie point exists (6z = 114, i.e. z = 19 — the only digit
  midpoint divisible by 6); the law's larger-digit tie-break assigns it
  digit 4, and the tie is LOAD-BEARING: n=36's trace passes through it.
procedure: [tricks/t23_six_pile_buckets.py](tricks/t23_six_pile_buckets.py)
scores: n/a (invariant)
verified: 2026-08-27 session 11
canonical_form: bucket form of general-b law (6, 52, 3)
notes: the six-step full-deck ACAAN now needs no candidate arithmetic —
  one 6-row threshold table. Process note: the first threshold transcription
  was off by one at two boundaries; the argmin-equivalence assert caught
  it pre-commit.

### machine-rederived-round-law
kind: engine (conjecture former output; extensional twin of
  [[general-b-radix-law]]'s round map, derived without hints)
domain |D|: fitted from 70 black-box (N, b) configs (1,500 cells, b=2..6,
  q0 down to 1); refuter battery 23 params to scale 1890 (b to 12, N to
  189); 240 t22 law vectors cross-certified; 4,353 verify() cases
invariant: former.py — told only "newpos may be affine in floor(x/b)
  with residue case-splits" — queried raw round maps as a black box and
  emitted the exact piecewise closed form (slope -1; intercept found as a
  5-leaf model tree over atoms a, j, rho, q0):
      a >= j: a < rho -> a + q0 + a*q0 ; else rho + q0 + a*q0 - 1
      a < j:  a < rho -> a + q0 + a*q0 - [j >= rho] ;
              else rho + q0 + a*q0 - 1
  Pickup vectors planned from the FITTED form alone (simulator never
  consulted during planning) pass verify() at (52,6,3), (32,2,6),
  (25,5,3); every t22 law_vector is certified by the fitted model at 7
  (N, b, r) configs including the tight (52, 6, 3).
procedure: [former.py](former.py) +
  [former_acceptance.py](former_acceptance.py) +
  [tricks/t25_former_rederivation.py](tricks/t25_former_rederivation.py)
scores: n/a (engine)
verified: 2026-08-27 session 13, acceptance ledger 6/6
canonical_form: machine-fitted model tree, extensionally == the
  general-b round map
notes: the no-hints boundary is enforced mechanically — the acceptance
  ledger scans former.py's source for simulator/law vocabulary. Process
  note: the FIRST fit (grid q0 >= 3 only, an artifact of requiring 3
  floor values per cell) was overfit in a q0-sparse pocket; the
  auto-derived battery REFUTED it at N=11 b=6 — the ladder catching the
  former's own drift. Fixed by two-pass extraction (sparse cells read
  through the already-fitted slope, exactness-checked) plus a
  grid-diversity rule: every grammar atom must vary, including at its
  floor. Negative control: down-under elimination correctly refused as
  outside the grammar rather than approximated.

### signature-derived-refutation
kind: engine (refuter automation; the anti-laundering layer)
domain |D|: whole-library regression ladder = 3,665,316 cases in 101s,
  7/7 checks; plus the laundering demo (10,844-case curated battery
  stamps a false conjecture ROBUST; the derived schedule kills it at a
  floor probe)
invariant: attack schedules are DERIVED from a conjecture's parameter
  signature (axes + validity predicate + cost model), never curated:
  floor probes bisected against validity, escalation walks beyond every
  inspiring maximum from multiple anchors (a cheap corner affords the
  deep walk the expensive corner cannot), envelope-edge bisection when a
  walk overshoots or completes clean, deterministic out-of-grid draws.
  No silent caps: every axis reports 'escalated to V' or an explicit
  validity/cost limit. refute() now grades honestly — CANDIDATE (no
  attacks), CONJECTURE (attacked, never beyond inspiring scale),
  ROBUST_CONJECTURE (survived beyond) — and carries a per-axis envelope,
  so an empty or timid battery can no longer launder a robust stamp.
  Library ladder results (all ROBUST_CONJECTURE): general-b law to
  b=52 piles / N=104 / r=202; parity radix law to b=391; Josephus J(n)
  to n=6,656; Gilbreath to N=20, k=8 (2^20 interleavings); agreement
  conservation to N=32 (b=2, m=5), b=4, 136 rounds; bucket==argmin to
  |z| <= 91,366.
procedure: [refuter_auto.py](refuter_auto.py) +
  [refuter_battery.py](refuter_battery.py) (refute() grading upgraded in
  [refuter.py](refuter.py))
scores: n/a (engine)
verified: 2026-08-28 session 14, battery 7/7
canonical_form: derive_schedule(axes, inspiring, valid, cost, cap) ->
  (schedule, per-axis report)
notes: the laundering specimen is the parity rule claimed for every
  N <= b^r — its inspiring data AND a diverse-looking curated adversary
  sample only N = b^r, so the curated ladder awards a false ROBUST; the
  derived schedule's floor probe (b=2, N=2, r=5) kills it instantly.
  Coverage map and exclusions (strategy-search entries, exhausted finite
  constructions, engine self-audits) documented in refuter_battery.py.
  Conservation newly generalized: verified beyond the b=3 entry at b=2
  and b=4 packets. Battery caps trim the historical parity envelope
  (scale-512 (2,9) stands from refuter.py's own demo, which still runs).

### integrated-engine-loop
kind: engine (item 5: the pipeline as one runnable)
domain |D|: dry-run acceptance 9/9 checks, 12,947 cases, under a second;
  every pipeline path exercised against real library material
invariant: engine.py chains generator -> novelty oracle
  (log-and-suppress) -> conjecture former -> refuter (signature-derived
  schedules only) under per-run budgets (candidates / cases / seconds,
  candidate-atomic, every skip named — no silent truncation), with the
  suppressed log as the live drift metric. Eight dispositions:
  SUPPRESSED / REVIEW / ROUTED / UNSTRUCTURED / SURVIVOR / REFUTED /
  DOWNGRADED / SKIPPED. The generator slot is an interface (item 6);
  the dry-run replays a fixed mix: a t15-style disguised fixed-vector
  ACAAN (suppressed via [[machine-rederived-round-law]]'s sibling
  recognizer), out-faro (suppressed), the same faro on a partial sample
  (sampling pin -> REVIEW), the Mongean family (SURVIVOR — see notes),
  the milk shuffle (former refuses: rise-then-fold is outside the
  grammar), full reversal (ROUTED), and the naive-parity laundering
  specimen as a ready-made claim (REFUTED at the derived floor probe).
procedure: [engine.py](engine.py) (dry-run mode doubles as the
  acceptance ledger; unit checks at import)
scores: n/a (engine)
verified: 2026-08-28 session 14, dry-run ledger 9/9
canonical_form: run_engine(candidates, budget) -> report rows + drift +
  budget accounting
notes: FIRST FULLY-AUTONOMOUS PIPELINE PRODUCT: the Mongean position
  law — newpos = (2j-1)*floor(x/2) + (q0 + rho + j - 1), j = x mod 2 —
  oracle-cleared (outside all five families), machine-fitted from 40
  black-box cells, ROBUST_CONJECTURE with envelope N=1500. No human
  supplied the form. PROVENANCE (item 7, PROVENANCE.md
  mongean-position-law): verdict KNOWN — a REDISCOVERY. Position
  tracking under the Monge shuffle is published since Monge (1773);
  MathWorld carries the iterated closed form. The oracle cleared it
  only because no Monge recognizer exists — a recognizer-coverage gap.
  The pipeline's value here is validation, not discovery; survivor rows
  now carry "provenance log required (PROVENANCE.md)".

### generator-v1-round-laws
kind: engine (item 6: the inventive slot, v1) + two invariant products
domain |D|: 9 candidates through the full loop (88,031 cases, 1.5s);
  metric ledger 11/11
invariant: generator.py instantiates ONE question schema — the
  round-position-law question — over the existing op vocabulary
  (pointed/cyclic/reversed pickups, cut-then-deal, interleaves,
  down-under), emitting each instance with BOTH an oracle view and a
  parametric former view: the generator is deliberately ignorant of
  what is known (pre-filtering would re-introduce author blind spots
  upstream of the guardrails). Dedup is extensional (b=2 cyclic ==
  b=2 reversed-rest: one dropped). Engine run: 6/9 suppressed across
  three families (Gergonne x4, Faro, Josephus — the drift metric
  measuring "orbiting the known"), cut-then-deal honestly REFUSED
  (position law lives in floor((x-a)/b), outside the v1 grammar —
  grammar-v2 backlog), and TWO oracle-NOT_MATCHED survivors at
  ROBUST_CONJECTURE: the REVERSED-REST PICKUP position laws for b=3
  (envelope N=5,248) and b=4 (envelope N=5,000) — machine-fitted
  closed forms for "pile a on top, rest right-to-left", a pickup
  outside the Gergonne gather family.
procedure: [generator.py](generator.py) (running it executes the
  item-6 success metric as a ledger); engine repair loop + scheduler
  residue probes in [engine.py](engine.py) / [refuter_auto.py](refuter_auto.py)
scores: n/a (engine)
verified: 2026-08-28 session 14, metric ledger 11/11
canonical_form: schema x op-vocabulary -> EngineCandidate stream
notes: PROVENANCE (item 7, PROVENANCE.md reversed-rest-pickup-laws):
  verdict KNOWN-FAMILY — arbitrary collection orders on evenly
  divisible decks sit inside the charted p-pile framework (DAM 1997,
  Quintero 2017), so the b | N slice is known territory; the uneven-N
  closed forms (q0/rho case-split intercepts, N mod b != 0) were not
  found — likely new in that regime, relative to the logged queries.
  Three self-corrections in one item, all caught by the machinery:
  (1) the draft claim said "every packet size N" — the refuter's floor
  probe produced N=2,b=3 (empty pile) instantly; scoped to N >= b with
  the counterexample recorded; (2) with b fixed per candidate the
  sparse grid let an exact-on-grid tree alias off-grid (killed at
  N=54) — fixed by densifying the mechanical grid AND adding the
  engine's bounded REPAIR loop (refuter witness joins the fit grid,
  former refits; unit-tested); (3) the repair unit then exposed a
  scheduler blind spot — pure doubling escalation preserves residue
  classes (N = 0 mod b forever), so residue-keyed errors could
  survive — fixed with minimal/odd-offset probes in derive_schedule.
  Each guardrail caught the layer above it.

### general-b-law-theorem
kind: proof (engine item 8: the ladder's top rung, occupied)
domain |D|: hypothesis region H1 b >= 2, H2 N >= b, H3 b^(r-1) >= N —
  ALL of it, by proof; plus 27,700 fresh verify() cases at
  boundary-tight configs and 4 extensional law_vector cross-checks
invariant: THEOREM — under H1-H3 the argmin recursion
  z <- -b*z + (2a+1-b)N + 2*corr(a) (digits reversed = pickups) brings
  every card to every named target. Proof chain (PROOF.md): pile-size
  algebra (division uniqueness, certified quotient/remainder) ->
  round-map closed form C(j,a) -> single-target preimage = b
  consecutive positions (run concatenation) -> interval tiling and the
  midpoint recursion as EXACT endpoint algebra (no floors, no halving)
  -> offset span [-(b-1)N, (b-1)N] with gaps in
  [2(N-b+1), 2(N+b-2)] -> one-step bound |z'| <= N + max(b-2, b*d) ->
  envelope |z_k| <= N + (b-2)b^(k-1) -> coverage iff |z_r| <= b^r - N,
  and (b^r - N) - (N + (b-2)b^(r-1)) = 2b^(r-1) - 2N: hypothesis H3
  IS the coverage condition with zero slack — explaining both why the
  bound is sufficient and why it is not necessary (the envelope is
  worst-case over targets; t22's frontier data lives in the slack).
procedure: [PROOF.md](PROOF.md) (theorem + lemmas, machine-check IDs
  C1-C10, prose steps P1-P3) + [proof.py](proof.py) (kernel: Farkas
  certificates + exact polynomial identities, sympy-backed; kernel
  failure modes unit-tested; simulator grounding C1/C2/C4; ground
  truth C10)
scores: n/a (proof)
verified: 2026-08-28 session 15, PROOF CHECKS PASS C1-C10 (incl.
  verify() at (5,25,3), (6,36,3), (7,49,3), (2,32,6) — all
  b^(r-1) = N exactly — plus uneven near-boundary (6,33,3), (5,23,3)
  and abstract (12,144,3))
canonical_form: theorem(general-b law; semi-formal, machine-checked
  algebra + prose skeleton P1-P3)
notes: division of labor is explicit in PROOF.md's "Scope and
  honesty": every identity/inequality is machine-certified; the three
  prose steps are the discrete intermediate-value argument, the
  induction over rounds, and the backward/forward duality — standard
  finite arguments, none touching the corr algebra where this
  project's historical errors lived. Process note (tradition upheld):
  the kernel caught a genuinely missing case during construction —
  the a = b-1 pickup has an EMPTY second run in the preimage
  concatenation, and the draft case analysis asserted it nonempty;
  the Farkas check refused the certificate (residual -1) and forced
  the a = b-1 sub-case. The refuter ladder's grading still tops at
  ROBUST_CONJECTURE by design: refutation can never promote to
  THEOREM — only a proof artifact can, and this entry is the first.

### provenance-log
kind: engine (item 7: literature logs as first-class artifacts)
domain |D|: 9 dated records covering 17 library entries; 12 logged
  queries + 4 page fetches; audit ledger 9/9 unit checks + full-file
  audit PASS
invariant: claims of newness are now auditable the way "verified" is —
  PROVENANCE.md holds one dated record per novelty claim (queries run,
  sources with URLs, verdict from a controlled vocabulary: KNOWN /
  KNOWN-FAMILY / NOT-FOUND), and provenance_audit.py enforces the link
  mechanically: every entry whose text claims novelty must be covered
  by a record; records may not cite nonexistent entries; a KNOWN
  verdict requires the entry itself to acknowledge the literature; the
  stale "pending" tag may not survive. Verdicts are explicitly relative
  to the logged queries — a NOT-FOUND is a statement about a search,
  never about the literature.
procedure: [PROVENANCE.md](PROVENANCE.md) +
  [provenance_audit.py](provenance_audit.py) (unit checks at import;
  __main__ audits the real files and exits nonzero on any gap)
scores: n/a (engine)
verified: 2026-08-28 session 15, audit PASS over the live files
canonical_form: novelty claim -> dated search record -> mechanical audit
notes: headline verdicts. KNOWN: the Mongean position law (session 14's
  "first autonomous product") is a REDISCOVERY — Monge 1773, closed
  form on MathWorld — recorded as pipeline validation, not discovery.
  KNOWN-FAMILY: the whole uneven-radix family (t19-t23) — floor-map
  Gergonne dynamics are charted (Bolker 2010; DAM 1997; Quintero 2017),
  but every source found treats evenly divisible decks and/or
  fixed-point convergence; the uneven-N corr(a) targeting laws and the
  b^(r-1) >= N boundary were not found. Same verdict for the
  reversed-rest pickup laws (even-N slice charted, uneven-N not found).
  NOT-FOUND: the two-card shared-gather problem (conservation
  obstruction + double reveals) — still the library's strongest
  new-result candidates. A 2025 arXiv survey (Card Dealing Math, 2509.11395) now
  charts the under-down genre including audience-controlled counts, so
  t13's genre is KNOWN-FAMILY. Known limit: web search only — magic
  literature databases and paywalled journals not consulted; records
  append, never edit.

---

## Session log

- 2026-08-28 session 15 (engine item 8, user-directed): the proof
  step. PROOF.md + proof.py: the general-b law's sufficiency
  b^(r-1) >= N proven over the entire hypothesis region — pile-size
  algebra -> closed form -> preimage contiguity -> endpoint/midpoint
  recursion -> offset gaps -> envelope |z_k| <= N + (b-2)b^(k-1) ->
  coverage, with H3 exactly the zero-slack coverage condition. Proof
  kernel: Farkas certificates + exact polynomial identities (checks
  C1-C10; prose P1-P3 documented); kernel caught a missing a = b-1
  empty-run case during construction. Fresh ground truth: 27,700
  verify() cases at boundary-tight configs. general-b-radix-law
  upgraded to THEOREM status — the ladder's top rung occupied for the
  first time. ENGINE QUEUE COMPLETE (items 1-8).
- 2026-08-28 session 15 (engine item 7, user-directed): provenance.
  12 web queries + 4 fetches run against every novelty claim; 9 dated
  records in PROVENANCE.md covering 17 entries; provenance_audit.py
  enforces coverage/vocabulary/acknowledgment mechanically (unit checks
  7 failure modes; full-file audit PASS). Humbling headline: the
  Mongean law is a rediscovery (Monge 1773) — LIBRARY entry corrected;
  reversed-rest laws scoped to "likely new only for N not divisible by
  b"; two-card shared-gather problem remains NOT-FOUND (strongest
  candidates). Item 8 (proof step) next.
- 2026-08-28 session 14 (engine item 6): generator v1. One schema
  (round-position-law) over existing ops, oracle-ignorant emission,
  extensional dedup, full-loop run 9 candidates: 6 suppressed (3
  families), 1 honest refusal, 2 NOT_MATCHED survivors at ROBUST
  (reversed-rest pickup laws, b=3/b=4, envelopes past N=5,000) —
  item-6 success metric met, 11/11. Along the way: claim scoped to
  N >= b by a refuter floor kill; engine gained the bounded
  repair loop (refuter witness -> refit); derive_schedule gained
  residue-breaking probes after the repair unit caught doubling-walk
  residue blindness. Battery + dry-run + acceptance regressions green.
  Session budget reached (3 commits); items 7-8 next.
- 2026-08-28 session 14 (engine items 4+5): refuter automation + the
  integration loop. Item 5: engine.py — oracle/former/refuter chained
  under candidate-atomic budgets, suppressed-log drift metric, dry-run
  acceptance 9/9 (12,947 cases, 0.9s); first autonomous product = the
  Mongean position law (SURVIVOR, envelope N=1500); milk shuffle
  honestly refused; laundering specimen killed inside the loop.
  Items 6-8 pending.
- 2026-08-28 session 14 (engine item 4): refuter automation.
  refuter_auto.py derives attack schedules from parameter signatures
  (floor probes, multi-anchor escalation walks, envelope-edge bisection,
  deterministic draws, no-silent-caps axis reports); refuter.py refute()
  upgraded to graded verdicts (CANDIDATE / CONJECTURE /
  ROBUST_CONJECTURE by whether attacks exceeded inspiring scale) with
  per-axis envelopes and case accounting; refuter_battery.py generates
  Conjecture objects from six library entries and runs the whole-library
  ladder: 7/7, 3.67M cases, 101s, every envelope pushed past prior
  testing. Laundering demo executed: curated adversary awards the false
  robust stamp, derived schedule refutes at a floor probe. Regressions
  clean (former acceptance 6/6 under new refuter; C1/C2 demo intact).
  Items 5-8 pending.
- 2026-08-27 session 13 (engine item 3): conjecture former. former.py is
  a generic exact-fit engine — rational incremental RREF with early
  inconsistency exit, model trees split on atom comparisons, refusal as
  a first-class outcome, attack battery auto-derived from the fit grid's
  parameter signature — and imports nothing from the project. Acceptance
  6/6: re-derived the general-b round law from raw round maps unaided
  (5-leaf tree, extensional twin of t22), ROBUST_CONJECTURE at scale
  1890, down-under control refused, 240 law vectors cross-certified,
  4,353 verify() cases via model-planned vectors (t25). The first fit
  attempt was REFUTED by its own battery (overfit q0-pocket, killed at
  N=11 b=6) — kept on the record as evidence the ladder catches the
  former's drift. Items 4-8 pending.

- 2026-08-27 session 12 (ENGINE track begins; queue reseeded). Item 1:
  harness generalization — verify()/verify_prop() gain deck_factory
  (default 52-card deck, fully backward compatible; regression: harness
  self-check, t22, t23 all pass unchanged) + make_packet(N) primitive,
  all unit-checked. Demonstrated by t24: general-b law verified on
  abstract packets at five tight fits up to N=144/b=12 (47,954 cases) —
  configs session 10 could not test. Item 2: library-as-known — the
  oracle gains an extensional LibraryTargeting recognizer (fixed-vector
  reproduction of the whole map; refines Gergonne; abstains when b^r too
  large) — acceptance ledger passed 6/6 first run incl. REAL adaptive
  t15 caught as a library known; demo regression clean. Engine queue
  items 3-8 pending.
- 2026-08-27 session 11 (user follow-up): t23 six-pile bucket rule —
  thresholds derived from candidate midpoints, equivalence with argmin
  proven over [-400,400], trick re-verified 2704/2704 on buckets alone;
  single tie point z=19 identified and shown to occur (n=36).
- 2026-08-27 session 10 (queue item 1): t22 general-b law. Closed-form
  correction derived for all pile counts; 32,896 cases verified over
  b = 2, 5, 6, 7, 8 first-attempt (family now spans b = 2..8). Frontier
  mapped at r=3/N=52: six piles is the three-deal minimum (b=5 misses by
  exactly two targets). 1 invariant commit (capstone).
- 2026-08-27 session 9 (queue item 1): t21 four-pile law. Derived and
  verified base-(-4) analog over 24,415 cases (24 sizes, all residues
  mod 4, first-attempt PASS incl. 16 tight fits). Full-deck ACAAN drops
  to FOUR deals with even 13-card piles and a pure quarter-bucket digit
  rule. HOWTO + artifacts updated. 1 invariant commit.
- 2026-08-27 session 8 (queue item 1): t20 universal radix law. Session-7
  N≡2 impossibility claim REFUTED by redoing the interval algebra; one
  integer law now covers every N (18,223 cases, 18 sizes, all residues).
  Human-performable write-up committed (HOWTO.md + artifact). 1 invariant
  commit; second self-correction on the record.
- 2026-08-27 session 7 (queue item 1): t19 closed form for the ACAAN crib.
  One-round formula verified at 10 deck sizes; alternating-radix law
  verified over 9,349 cases with validity condition 3^(r-1) >= N; the two
  predicted out-of-condition failures confirmed fundamental by exhaustive
  enumeration. Full-deck ACAAN is now crib-free (mental 5-step digit
  computation). 1 invariant commit; fixed-vector-uneven-acaan upgraded.
- 2026-08-27 session 6 (oracle audit + discovery): engine drop (novelty
  oracle + refuter) landed on branch `oracle` and audited against REAL
  procedures (AUDIT.md there). Refuter extended the t6 radix law envelope
  to scale 512 (262k cases, survived). Audit overturned the deriver's own
  expectation: t15 IS extensionally Gergonne-family — fixed 5-vectors
  cover 52/52 targets — yielding t18 (PASS 2704) which supersedes t15's
  trick claim. t17 correctly routed onward (injectivity proof: fixed
  ordering sequences cannot collapse pairs). 1 commit (not novel), 1
  supersession, 1 envelope extension.
- 2026-08-27 session 5 (single task, user-directed): t17 performable double
  reveal. Sweep over uneven (N, b) configs; N=11/b=4/4 rounds admits a
  REACTIVE strategy (found via distance-pruned greedy synthesis), verified
  2x110. N=13 resisted reactive search (open). 1 novel commit. NOTE: macOS
  TCC revoked repo access mid-session; work done in scratchpad against a
  byte-identical reconstruction of deck_sim.py (diff-confirmed after access
  was restored); commits staged in scratchpad/pending_sync and applied +
  re-verified in-repo on 2026-08-27, same day the repo was placed under git.
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
