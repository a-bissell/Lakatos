# PROOF — the largest-first ACAAN law (theorem #3)

The third THEOREM-status entry, and the shortest: it is theorem #1
seen in a mirror. Machine checks E1-E8 live in
[proof_rr.py](proof_rr.py) (kernel shared with [proof.py](proof.py));
prose steps R1-R2 are named below. The theorem resolves the
card-dependent sibling of the generator's reversed-rest survivors
([[generator-v1-round-laws]]) and closes the theorem-#3 gate opened
by the contiguity check.

## Theorem

Let b >= 2, N >= b, b^(r-1) >= N (the hypotheses of theorem #1).
One round: the spectator points at the pile holding their card; the
performer picks the piles up LARGEST-INDEX-FIRST, inserting the
pointed pile at rank c in {0, ..., b-1} (c piles above it). Define

  corr_rr(c) = -corr(b-1-c),

with corr the general-b correction of [[general-b-radix-law]], and
run the recursion z <- -b*z + (2c+1-b)*N + 2*corr_rr(c) from
z_0 = 2(n-1) - (N-1), choosing any |z|-minimizing digit each step.

THEOREM. The digits, reversed and applied as ranks, bring every card
to 1-indexed position n, for every target n in 1..N.

Verified independently in [t26](tricks/t26_reversed_rest_acaan.py):
33,141 cases over 13 configs, twelve of them boundary-tight,
including full-deck forms at b = 4 and b = 6 and the abstract
(12, 144, 3) packet.

## Lemma A (round-map closed form) — E1, E2

With a := b-1-c (the complementary rank — in this coordinate the case
structure aligns with the Gergonne one), the pile above-set is the c
largest indices other than j, and the tracked card's new position is
C_rr(j, c) - floor(x/b) with

  C_rr = (c+1) q0 + max(0, rho-a-1) + [j < rho] - 1     if j <= a
  C_rr = (c+1) q0 + max(0, rho-a)               - 1     if j > a.

The same cancellation as theorem #1's Lemma 2 appears in the j > a
case: the pointed pile's own size indicator cancels against the count
of large piles above it. E2 certifies the counting; E1 checks the
form against the simulator for every (j, c) on the grid.

## Lemma R (reflection conjugacy) — E3, E4

Let r(x) = N-1-x be the position reflection. Then for every rank c
and every position x:

  rr_c(x) = r( gp_{b-1-c}( r(x) ) )

— the largest-first round map IS the reflection conjugate of the
Gergonne round map at the complementary rank. Two ingredients:

  * Reflection algebra (E4): the card x = b*y + j reflects to a card
    in pile j' = (rho-1-j) mod b at deal index sizes[j]-1-y — division
    identities with certified remainder ranges, one case for j < rho
    and one for j >= rho.
  * The algebraic core (E3): substituting, the conjugacy reduces to

      C_rr(j, c) + C_gp(j', b-1-c) = N - 2 + sizes[j],

    verified per case cell (a < rho / a >= rho crossed with j < rho /
    j >= rho, sub-split on which C_gp branch j' lands in — every
    resolution Farkas-certified). E4 also checks the full conjugacy
    on the simulator: rr_c == r . gp_{b-1-c} . r at every grid
    config and rank.

## The theorem from the mirror — R1, R2, E6

R1 (prose): r is an involution, so conjugation composes:
rr_{c_k} ∘ ... ∘ rr_{c_1} = r ∘ (gp_{a_k} ∘ ... ∘ gp_{a_1}) ∘ r with
a_i = b-1-c_i. If a Gergonne vector sends EVERY card to the mirror
target N+1-n (theorem #1 provides one whenever b^(r-1) >= N), the
complemented vector sends every card to n under largest-first
pickups.

R2 (prose + E6): the law's own recursion is the mirrored argmin. E6
certifies f_rr(b-1-a) = -f_gp(a) per case, (-b*z + F) =
-(-b*(-z) + (-F)) identically, and z_0(n) = -z_0(N+1-n); so c
minimizes |z'| for (z, rr) exactly when b-1-c minimizes for (-z, gp),
and the rr trajectory from z_0(n) is the pointwise negation of a gp
trajectory from z_0(N+1-n) whose digit choices are minimizers.
Theorem #1 was proven for ANY minimizer, so that mirrored trajectory
is a valid Gergonne vector for the mirror target, and by R1 its
complement — the rr law's own output — is valid for n. (Argmin ties
may resolve differently from t22's larger-digit rule; t26 measures
this: 66/73 vectors are exact complements, 7 differ only at ties,
and all verify.)

## Standalone recursion — E5

Independent of the mirror, the preimage interval L_rr(t, c) =
b*(D - t) + (b if a < rho else rho), D = (c+1) q0 + max(0, rho-a-1)
- 1, tiles with step b and has doubled-center recursion exactly
z' = -b*z + (2c+1-b)*N + 2*corr_rr(c) — certified symbolically and
checked against the simulator's preimages at every grid config (the
theorem-#3 gate check, now a permanent proof obligation). So the
law also stands without the conjugacy, inheriting theorem #1's
offset-gap/envelope/coverage superstructure unchanged (E6's mirror
identities show the offset multiset is the exact negated reflection,
so span and gap bounds carry over verbatim).

## What is actually new here — E8

The family coincides with Gergonne gathering at even N and at the
edge ranks (c = 0, c = b-1), and differs at EVERY uneven-N interior
rank (E8: 45/45 on the grid). Its mathematical content is therefore
a reflection conjugate of theorem #1 — the honest framing is that
theorem #3 is a structural corollary, not an independent discovery.
What the entry contributes: the duality itself (corr_rr = -corr
mirrored, vector = complemented mirror-target vector — a clean
symmetry of the Gergonne dynamics not stated in the sources
provenance logged); the resolution of the generator's survivor family
(its card-dependent sibling now has a proven targeting law, and the
survivors' own card-independent maps provably admit no fixed-vector
targeting, being bijections); and a second performable pickup
convention — largest-first is arguably the more natural physical
motion — whose crib is "complement the digits, mirror the target."

## Scope and honesty

* Machine-checked (E1-E8): the counting derivation, the closed form
  against the simulator, the reflection algebra with certified
  ranges, the conjugacy core identity per cell, the full map-level
  conjugacy on the grid, the standalone recursion, the mirror
  identities, fresh verify() ground truth, and distinctness.
* Prose (R1-R2): involution conjugation composes; the mirrored-argmin
  argument riding theorem #1's any-minimizer statement. Both lean on
  PROOF.md's proven core; neither introduces new case analysis.
* Scope: identical hypotheses to theorem #1 (b >= 2, N >= b,
  b^(r-1) >= N). The generator survivors' literal card-independent
  laws are NOT this theorem — they are round laws for fixed
  bijections (provable by Lemma A's algebra alone) and support no
  fixed-vector targeting.
