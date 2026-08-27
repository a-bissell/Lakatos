# Fair & Uneven — performing the universal-radix ACAAN

Machine-verified: `tricks/t20_universal_radix_law.py`, 18,223 cases across
18 packet sizes (see LIBRARY.md, [[universal-radix-law]]). The physical
protocol below is the exact procedure the simulator verified: everything
stays FACE UP the whole time — no flips, ever (a flip reverses the packet
and breaks the mathematics).

## Effect
A shuffled deck. One spectator thinks of any card they see; another names
any number n from 1 to 52. Five quick deals later, the thought-of card is
exactly n cards deep. No setup, no sleight, nothing memorized but a
five-digit code you compute in your head.

## Requirements
- Any 52-card deck, genuinely shuffled (any order works).
- The whole procedure is done with cards face up on the table.

## Step 1 — the choices
Spread the deck face up; a spectator remembers any card. Ask for a number
n between 1 and 52. (n may be named any time before the pickups begin.)

## Step 2 — compute the five digits (in your head or on paper)
Start with m = n − 1. Five times, do:

| if m is…      | write digit | new m       |
|---------------|-------------|-------------|
| 16 or less    | 0           | 50 − 3m     |
| 17 to 34      | 1           | 103 − 3m    |
| 35 or more    | 2           | 154 − 3m    |

Then REVERSE the five digits — the reversed list is your pickup code,
first pickup first.

Worked examples (traces are code-generated, not hand-computed):
- n = 20: m: 19→46→16→2→44, writes 1,2,0,0,2 → pickups **2,0,0,2,1**
- n = 1:  m: 0→50→4→38→40,  writes 0,2,0,2,2 → pickups **2,2,0,2,0**
- n = 52: m: 51→1→47→13→11, writes 2,0,2,0,0 → pickups **0,0,2,0,2**

## Step 3 — five rounds of deal, point, pick up
Each round:
1. Deal the whole packet FACE UP into three piles, left to right, one card
   at a time (left pile gets the extra cards).
2. The spectator points to the pile containing their card. (They see every
   face; you never need to.)
3. Pick up using this round's digit — the digit is how many of the OTHER
   two piles end up above the pointed pile, keeping the other two piles in
   left-to-right order among themselves. Concretely, build one face-up
   packet reading top-down:
   - digit 0: pointed pile, then left other, then right other
   - digit 1: left other, then pointed pile, then right other
   - digit 2: left other, then right other, then pointed pile
   ("Left other" = the leftmost of the two piles NOT pointed at. Stack by
   placing lower piles first, then the higher ones on top of them, without
   turning anything over.)

## Step 4 — the reveal
After the fifth pickup, count cards off the face of the packet: the n-th
card is the thought-of card.

## The four-deal upgrade (recommended)
Verified separately (t21, 24,415 cases): the same trick with FOUR piles
needs only FOUR deals, and 52 splits evenly (13/13/13/13).
- Digits: start z = 2n − 53. Four times:
  z < −26 → digit 0 · −26 ≤ z < 0 → digit 1 · 0 ≤ z < 26 → digit 2 ·
  z ≥ 26 → digit 3; then z ← −4z + (2·digit − 3)·52.
  Reverse the four digits for the pickup order.
- Rounds: deal face up into FOUR piles left to right; spectator points;
  the digit is how many of the other three piles go above the pointed
  pile, others keeping their left-to-right order (reading top-down:
  the first `digit` others, then the pointed pile, then the rest).
- Examples (code-generated): n=15: z: −23→40→−4→−36, writes 1,3,1,0 →
  pickups 0,1,3,1. n=52: z: 51→−48→36→12, writes 3,0,3,2 → pickups
  2,3,0,3.
- General N with 4 piles: z = 2(n−1) − (N−1); candidates
  −4z + (2a−3)N + 2δ with δ(N mod 4): ≡0 (0,0,0,0), ≡1 (0,2,1,0),
  ≡2 (0,2,2,0), ≡3 (0,1,2,0); pick the digit leaving |z| smallest;
  4^(r−1) ≥ N rounds.

## The expert form: six piles, three deals (six steps total)
Verified (t22): with SIX piles the full deck needs only THREE rounds.
Heavier mental math — six candidates per digit — so this is the expert
option; the four-pile version stays the recommended one.
- rho = 52 mod 6 = 4; corrections per digit a = 0..5: (0, 2, 4, 6, 4, 0).
- z = 2n − 53; three times: compute −6z + (2a−5)·52 + 2·corr(a) for each
  a, keep the digit whose result is smallest in absolute value (tie: the
  larger digit), update z to it. Reverse the three digits.
- Example (code-generated): n=15 → pickups 5, 2, 1.
- Deal into six piles left to right; digit = how many of the other five
  piles go above the pointed pile, others keeping left-to-right order.

## The general law (any piles, any packet)
For b piles, N cards, r deals with b^(r−1) ≥ N (often fewer work):
z = 2(n−1) − (N−1); each step choose the digit a in 0..b−1 minimizing
|−b·z + (2a+1−b)·N + 2·min(a,ρ)·(b − max(a+1,ρ))| where ρ = N mod b;
update z; reverse the digits. Every instance in this file is this one
law.

## Any packet size (three piles)
The same algorithm runs any packet of N cards with r pickups where
3^(r−1) ≥ N (r=3 up to 9 cards, r=4 up to 27, r=5 up to 81):
- digit 0 if 6m < 2N−3; digit 2 if 6m > 4N−3; digit 1 otherwise
- new m = K − 3m with K = (N−2, 2N−1, 3N−2); middle K is 2N−2 when N is
  divisible by 3 (then no +1 correction exists anywhere).
Never any ties: 6m is even, both thresholds are odd.

## Why it works (one paragraph)
Each deal-and-pickup moves the thought-of card by x′ = A − ⌊x/3⌋, and the
constants A are (for the pointed-pile pickup rule above) independent of
which pile is pointed at, up to a one-unit offset the algebra absorbs. Five
rounds contract the whole deck to a single position, and the digit
recursion is the base-(−3) expansion of the target's offset from the deck
center, digit set {−N, 0, +N}, with a +1 fingerprint from the uneven
piles. Verified exhaustively; see t19/t20.
