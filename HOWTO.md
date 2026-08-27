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

## Any packet size
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
