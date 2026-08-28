# PROOF — the general-b radix law (engine item 8)

The first THEOREM-status entry. Every algebraic identity and inequality
below is machine-verified by [proof.py](proof.py) (check IDs C1-C10 in
the margins); the surrounding skeleton — two inductions and one
discrete intermediate-value step — is prose, marked P1-P3. The
formalization's conventions are grounded in the simulator by
cross-checks (C1, C2, C4) and the theorem's statement is re-tied to
ground truth by fresh verify() runs at boundary-tight configurations
(C10). See "Scope and honesty" at the end for exactly what is machine
and what is prose.

## Theorem

Let b, N, r be integers with

  H1: b >= 2      H2: N >= b      H3: b^(r-1) >= N.

Deal-and-gather round (the simulator's semantics, [deck_sim.py](deck_sim.py)):
positions are 0-indexed from the top; dealing sends the card at
position x to pile j = x mod b (round-robin, last dealt on top);
gathering with pickup a in {0, ..., b-1} places exactly a of the other
piles, in their index order, on top of the pile containing the card.

Define rho = N mod b, q0 = floor(N/b), corr(a) = min(a, rho) * (b -
max(a+1, rho)), and for a 1-indexed target n the recursion

  z_0 = 2(n-1) - (N-1);
  z_{k+1} = -b * z_k + (2a+1-b) * N + 2 * corr(a),
  choosing at each step a digit a in {0, ..., b-1} minimizing
  |z_{k+1}| (any minimizer; the implementation's larger-a tie-break is
  one such choice).

THEOREM. The digit sequence a_1, ..., a_r produced by r steps of the
recursion, applied in REVERSE order as pickups (a_r first), brings the
card to 1-indexed position n from EVERY starting position, for every
target n in 1..N.

This is the law verified empirically in
[t22](tricks/t22_general_b_law.py) (32,896 cases, with t20/t21 ~76k
across b = 2..8, plus t24's abstract packets to N=144) and re-derived
without hints by the conjecture former (t25). What follows replaces
"verified on every tested configuration" with a proof over the entire
hypothesis region.

## Lemma 1 (pile sizes and depths) — C1, C1s

Pile j receives the cards {x : x = j mod b} = {j, j+b, ...}; its size
is sizes[j] = ceil((N-j)/b), and since later-dealt cards go on top,
card x sits at depth sizes[j] - 1 - floor(x/b) from the pile's top.

  sizes[j] = q0 + [j < rho].

Machine: C1s proves the division identity per case (j < rho and
j >= rho) by exhibiting quotient and remainder with certified range
0 <= s < b (division uniqueness); C1 cross-checks sizes and depths
against deal_into_piles on a (b, N) grid — this is the step that pins
the formalization to the simulator's actual convention.

## Lemma 2 (round-map closed form) — C2, C3

Gathering with pickup a when the card is in pile j puts on top the a
lowest-indexed piles other than j: the set A(j, a) = {0..a-1} if
j > a, else {0..a} \ {j}. The card's new position is

  newpos(x) = C(j, a) - floor(x/b),  where
  C(j, a) = sum_{k in A} sizes[k] + sizes[j] - 1
          = (a+1) q0 + min(a+1, rho) - 1                   if j <= a
          = (a+1) q0 + min(a, rho) + [j < rho] - 1         if j > a.

Machine: C3 derives the closed form from Lemma 1 symbolically —
sum_{k in A} sizes[k] = a*q0 + |A ∩ [0, rho)|, with the interval-
intersection cardinalities resolved per sub-case under Farkas-certified
case conditions (the j <= a case's indicator [j < min(a+1, rho)] =
[j < rho] cancellation included). C2 cross-checks newpos against
deal_into_piles + gather_position over the full (x, a) grid at every
grid config. (This closed form is extensionally the former's 5-leaf
tree from [[machine-rederived-round-law]]; the two case-splits differ
syntactically, agree everywhere.)

## Lemma 3 (single-target preimage is b consecutive positions) — C4

Fix a target position t and pickup a. The positions x whose round
image is t are exactly

  X(t, a) = [L(t, a), L(t, a) + b - 1] ∩ [0, N),  where
  L(t, a) = b*(D_a - t) + rho * [a < rho],
  D_a     = (a+1) q0 + min(a, rho) - 1.

Proof shape: within pile j the depth requirement C(j, a) - t has at
most one solution x = b(C(j, a) - t) + j, and that x lies in [0, N)
exactly when the depth is within the pile (so clipping to [0, N) is
exactly "the preimage exists in that pile"). Ranging over j, the b
candidate positions split into at most three runs — j <= a (where C
is j-independent), a < j < rho, and j >= max(a+1, rho) — which are
affine in j with unit step; the runs abut end-to-end and concatenate
into one interval of exactly b consecutive integers.

Machine: C4 proves the run concatenation per case (a < rho with
sub-cases a <= rho-2 / a = rho-1, and a >= rho): each adjacency is an
exact identity, each nonemptiness a certified inequality, and the
total width is b. A simulator grid check then confirms X(t, a)
directly for every (t, a) at every grid config.

## Lemma 4 (interval preimage and the midpoint recursion) — C5

For a contiguous target interval T = [t1, t2] (width w = t2 - t1 + 1),
the positions mapping INTO T under pickup a are

  pre(T, a) = [L(t2, a), L(t1, a) + b - 1] ∩ [0, N),

contiguous of unclipped width b*w — because L(t-1, a) = L(t, a) + b
makes the per-target b-blocks tile without gaps. Defining the doubled
center z(T) = t1 + t2 - (N - 1), the unclipped preimage satisfies

  z(pre) = -b * z(T) + (2a+1-b) * N + 2 * corr(a)

— exactly the theorem's recursion. In particular corr absorbs the
pile-size irregularity: b*min(a,rho) - (a+1)*rho + rho*[a<rho] =
min(a,rho)*(b - max(a+1,rho)) in both cases.

Machine: C5 verifies the tiling step (L(t-1) - L(t) = b), the endpoint
recursion, the width, and the doubled-center identity as exact
polynomial identities in (a, b, q0, rho, t1, t2) per case a < rho /
a >= rho, with N = b*q0 + rho substituted throughout — no floors, no
halving, all integer-exact.

## Lemma 5 (offset structure) — C6

Let f(a) = (2a+1-b) N + 2 corr(a) (so z' = -b z + f(a)). Then

  f(0) = -(b-1) N,   f(b-1) = (b-1) N,
  2 (N - b + 1) <= f(a+1) - f(a) <= 2 (N + b - 2),

so under H2 the offsets are strictly increasing and span exactly
[-(b-1)N, (b-1)N] with gaps at most 2(N + b - 2).

Machine: C6 proves corr(0) = corr(b-1) = 0, the three consecutive-
difference cases corr(a+1) - corr(a) = b - rho (a+1 < rho), b - 2 rho
(a+1 = rho), -rho (a >= rho), and both gap bounds per case, all with
Farkas certificates over the case conditions.

## Lemma 6 (one-step bound) — C7, P1

If |z| <= N + d (d >= -1), then the minimizing digit gives

  |z'| <= N + max(b - 2, b*d).

Proof: v := b z has |v| <= b(N + d).
(i) If v lies in the offset span, then since f is strictly increasing
(Lemma 5) with f(0) <= v <= f(b-1), some consecutive pair brackets v
(P1: discrete intermediate value over a finite monotone sequence —
prose), and the nearer of the two offsets is within half a gap:
|z'| <= N + b - 2 (C7: Farkas refutation — both distances exceeding
the half-gap contradicts the gap bound).
(ii) If v > f(b-1), the offset f(b-1) is at distance
v - (b-1)N <= b(N+d) - (b-1)N = N + b*d (C7); symmetrically for
v < f(0). The minimizer is at most either bound.

## Lemma 7 (envelope and coverage) — C8, C9, P2

Let d_k bound |z_k| - N. C9: |z_0| <= N - 1, so d_0 = -1. By Lemma 6,
d_1 = max(b-2, -b) = b - 2, and inductively (P2, with C8 certifying
the step max(b-2, b*(b-2)*B) = (b-2)*b*B for B = b^(k-1) >= 1):

  |z_k| <= N + (b-2) * b^(k-1)   for k >= 1.

Coverage: after r steps the unclipped requirement interval has width
b^r and doubled center z_r; it contains every position 0..N-1 iff
|z_r| <= b^r - N (an exact doubled-endpoint computation, C8). And

  (b^r - N) - (N + (b-2) b^(r-1)) = 2 b^(r-1) - 2N >= 0

is EXACTLY hypothesis H3 (C8) — the sufficient condition b^(r-1) >= N
is the coverage condition with zero slack against this envelope, which
is why the bound is sufficient yet (as the frontier data shows) not
necessary: the envelope is worst-case over targets.

## Conclusion (forward correctness) — P3, C10

P3 (duality, prose): run the recursion backward from the target
interval I_0 = {n-1} choosing digits a_1, ..., a_r; I_k = pre(I_{k-1},
a_k) by construction, so by Lemma 3/4 every position of [0, N) lying
in I_k moves into I_{k-1} when pickup a_k is applied — the clipped
part of I_k is exactly the set of true positions with images in
I_{k-1} (Lemma 3's biconditional). By coverage (Lemma 7 + H3), I_r
contains ALL of [0, N); applying pickups a_r, ..., a_1 in that order
therefore walks every starting position down the chain I_r -> I_{r-1}
-> ... -> I_0 = {n-1}. Every card reaches the target. QED.

C10 re-ties the whole statement to the ONE INVIOLABLE RULE: fresh
verify() runs at boundary-tight configurations (b^(r-1) = N exactly:
(5,25,3), (6,36,3), (7,49,3), (2,32,6), abstract (12,144,3); uneven
rho != 0 near the boundary: (6,33,3), (5,23,3)) — the proof does not
replace ground truth, it explains it.

## Scope and honesty

* Machine-checked (C1s, C3-C9): every identity and inequality —
  division algebra, the closed form, run concatenation, the tiling and
  midpoint recursion, offset span/gaps, the step bound's arithmetic,
  the envelope step, and coverage-iff-H3. The kernel is
  [proof.py](proof.py)'s Ctx: nonnegativity by explicit Farkas
  certificates (nonnegative rational combinations of hypothesis facts,
  products of two facts allowed), infeasibility by certified negative
  combinations, equalities by sympy exact polynomial expansion. The
  kernel's own failure modes are unit-tested (bad certificates and
  false identities rejected).
* Prose (P1-P3): the discrete intermediate-value step (a finite
  strictly-increasing sequence brackets every in-span value), the
  induction over rounds, and the backward/forward duality. Each is a
  standard finite argument with no hidden case analysis; none
  involves the corr algebra where all previous errors in this
  project's history occurred.
* Simulator-grounded (C1, C2, C4 grids; C10 verify): the conventions
  (deal order, gather order, depth orientation) are DEFINED by
  deck_sim.py, so the formalization is checked against it rather than
  trusted to transcribe it.
* Tie-breaks: the proof needs only SOME minimizer; law_vector's
  larger-a tie-break is one. Validity is claimed under H1-H3 only;
  below H3 the law may or may not work (t22's frontier data), and for
  N < b nothing is claimed.
* Status: semi-formal in the sense of item 8 — a Lean/Coq
  formalization would replace P1-P3 and the kernel with a proof
  assistant; nothing else would change.
