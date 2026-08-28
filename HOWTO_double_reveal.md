# The Two-Thoughts Packet — performing the 11-card double reveal

Machine-verified: [tricks/t17_small_double_reveal.py](tricks/t17_small_double_reveal.py),
both reveals over all 110 ordered pairs of distinct thought-of cards
(see LIBRARY.md, [[double-reveal-performable]]; tables re-derived and
re-verified 2026-08-28, and the round-4 shortcut below was verified
separately, both reveals x 110 for each middle ordering). The physical
protocol is exactly the procedure the simulator verified: everything
stays FACE UP the whole time — no flips, ever.

## Effect

Eleven cards are spread face up. TWO spectators each merely think of
a card they see (different cards). Four quick deals; each time, both
spectators silently point at the pile that holds their card. The
performer never asks anything else and never touches a card out of
turn. After the fourth pickup: the first spectator's card is on TOP
of the packet, the second spectator's is on the BOTTOM.

Two thought-of cards, eight physical actions, no setup, no math done
in the head — one small crib does everything.

## Why this packet, why these piles

This is the smallest configuration that works, and its shape is
forced by a theorem. With EVEN piles, no gathering strategy — however
clever, however many rounds — can ever steer two cards independently:
a conserved pattern in the two cards' positions makes it provably
impossible at any depth ([[two-card-conservation-theorem]],
PROOF_conservation.md). Uneven piles dissolve that obstruction, and
11 cards into piles of 3/3/3/2 is the smallest packet where a
memoryless lookup table exists (9 and 10 cards admit strategies, but
only ones that track history). Four rounds is also tight: three
rounds are information-theoretically impossible.

## What you need

- Any 11 distinct cards. A clean choice: Ace through Jack of one
  suit ("the royal court will judge two thoughts").
- Two spectators: **A** (their card ends on top) and **B** (bottom).
  Decide the roles up front and keep them straight — the crib is not
  symmetric.
- The crib below (38 entries + one closing rule).

No setup. Any starting order of the 11 cards works — including a
spectator-shuffled packet.

## The two moves

**The deal.** Hold the packet face up. Deal cards one at a time,
face up, into four piles LEFT TO RIGHT, round-robin (pile 1, 2, 3,
4, 1, 2, ...), each new card going ON TOP of its pile. Eleven cards
give piles of 3, 3, 3 and 2 — the short pile 4 on the right is
correct, not a mistake. Number the piles 1–4 left to right.

**The pickup.** A crib entry like `2-4-3-1` reads left to right as
top to bottom of the new stack: drop pile 2 onto pile 4, drop that
combined stack onto pile 3, drop everything onto pile 1. (First
named = top of the assembled packet.)

## The procedure

Each round: deal into four piles, ask both spectators to point at
the pile holding their card (they answer simultaneously; in early
rounds they may well point at the same pile — that is fine), find
the row for A and the column for B, assemble as written. Four
rounds, then the reveal.

### Round 1

| A points at | B: pile 1 | B: pile 2 | B: pile 3 | B: pile 4 |
|---|---|---|---|---|
| **pile 1** | 2-3-4-1 | 2-4-3-1 | 3-4-2-1 | 4-3-2-1 |
| **pile 2** | 1-3-4-2 | 2-4-3-1 | 3-4-1-2 | 4-3-1-2 |
| **pile 3** | 1-2-4-3 | 2-4-1-3 | 3-2-1-4 | 1-4-2-3 |
| **pile 4** | 1-3-2-4 | 2-1-3-4 | 3-2-1-4 | 2-1-3-4 |

### Round 2

| A points at | B: pile 1 | B: pile 2 | B: pile 3 | B: pile 4 |
|---|---|---|---|---|
| **pile 1** | 2-1-3-4 | 3-2-4-1 | 2-3-4-1 | 1-2-3-4 |
| **pile 2** | 3-2-4-1 | 3-2-4-1 | 3-4-2-1 | 2-1-3-4 |
| **pile 3** | 3-4-1-2 | 1-2-4-3 | 3-2-1-4 | 3-2-1-4 |
| **pile 4** | — | — | — | — |

A cannot be in pile 4 in round 2 — round 1's pickups guarantee it.
An entire row of the crib takes care of itself.

### Round 3

| A points at | B: pile 1 | B: pile 2 | B: pile 3 | B: pile 4 |
|---|---|---|---|---|
| **pile 1** | — | 2-4-3-1 | 3-4-1-2 | 4-3-2-1 |
| **pile 2** | 1-3-2-4 | — | 3-4-1-2 | — |
| **pile 3** | — | 2-1-4-3 | — | 1-4-2-3 |
| **pile 4** | 1-2-4-3 | 2-3-4-1 | 3-1-2-4 | — |

From round 3 on the two spectators will NEVER point at the same pile
— the strategy has provably separated their cards. A shared point in
round 3 or 4 means someone changed their card; smile and start over.

### Round 4 — no table

One rule, verified for every case: **A's pile goes on top, B's pile
goes on the bottom, and the other two piles go between them in
either order.** (Both middle orders were machine-verified over all
110 pairs; the middle genuinely does not matter.)

## The reveal

The work is done: A's card is the top card of the packet, B's is the
bottom card. Milk it. Ask each spectator to NAME their thought-of
card for the first time — nothing was ever said aloud until now —
then turn up the top card for A and show the bottom card for B. The
fact that neither card was ever named, touched, or looked for is the
entire trick; let the audience realize it.

## Field notes

- The dashes in rounds 2–4 are impossible observations, not gaps: if
  the pointing was honest, you will never need them.
- Both spectators pointing at the same pile in rounds 1–2 is normal
  and covered by the diagonal entries.
- The cards must be distinct and the A/B roles fixed. If you prefer
  B on top, swap the roles at the start, not the crib.
- Pace: the lookups are two-coordinate reads; with the crib card in
  hand the whole routine runs under ninety seconds. The round-4 rule
  needs no card at all, so the routine ENDS with you visibly not
  consulting anything.
- Why you can perform this with total confidence: every one of the
  110 possible pairs of thoughts has been machine-verified for both
  reveals, and the impossibility that makes it surprising — that
  even piles could never do this — is a proven theorem, not a hunch.
