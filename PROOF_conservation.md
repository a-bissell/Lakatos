# PROOF — two-card agreement conservation (theorem #2)

The second THEOREM-status entry, and the first impossibility theorem:
it quantifies over EVERY gathering strategy, the quantifier a test
battery handles worst. Machine checks D1-D8 live in
[proof_conservation.py](proof_conservation.py) (kernel shared with
[proof.py](proof.py)); prose steps Q1-Q3 are named explicitly. The
theorem is strictly stronger than the verified library invariant: the
agreement pattern is not merely conserved up to permutation — it is
rotated by EXACTLY one digit position per round, independent of the
strategy.

## Theorem

Let b >= 2, m >= 1, N = b^m (even piles). Write each position
p in [0, N) as its m base-b digits, digit_i(p) = floor(p / b^i) mod b
(digit 0 low). For two cards at positions p, q define the agreement
set

  A(p, q) = { i : digit_i(p) = digit_i(q) }  ⊆  {0, ..., m-1}.

One round = deal the deck into b piles (round-robin, the simulator's
semantics), then gather the piles in ANY order σ (all b! orders
allowed, chosen adversarially, adaptively, with full information —
both cards ride the same deal and the same gather).

THEOREM. After one round, for every σ:

  A(p', q') = rot(A(p, q)),   rot(i) = (i - 1) mod m.

Consequently, after r rounds under ANY strategy,
A = rot^r(A(start)): the agreement set is rotated r steps, its
CARDINALITY is invariant, and a target pair (s, t) is reachable from
a start pair (p, q) only if A(s, t) = rot^r(A(p, q)).

COROLLARY (double-targeting impossibility). Sending spectator A's
card to the top (position 0, all digits 0) and B's to the bottom
(position N-1, all digits b-1) requires A(targets) = ∅, hence
A(start) = ∅: the two thought-of cards must differ in EVERY base-b
digit of their start positions. At N = 27 that admits 216 of the 702
ordered start pairs; the other 486 are unreachable at any depth by
any strategy. This is the obstruction t16 part A measured
exhaustively; the theorem extends it to every b, m, and round count.

COROLLARY (the t16 observation explained). At m = 3, rot^3 = id, so
at r = 3 rounds the reachable pairs of a target lie in the target's
OWN agreement class — exactly the "one agreement-pattern class per
target" that session 4's backward reachability found.

## Lemma A (even-pile round map, arbitrary gather) — D1/D3

With all pile sizes q0 = b^(m-1) (Lemma 1 of [PROOF.md](PROOF.md)
with rho = 0, simulator-grounded there by C1), a card at position
x = b·y + d, 0 <= d < b, sits in pile d at depth q0 - 1 - y.
Gathering in order σ stacks the piles; with every pile the same size,
the card's new position is

  x' = rank_σ(d) · b^(m-1)  +  (b^(m-1) - 1 - y),

where rank_σ(d) is the pile's position in the gather order (0 = top).
The concatenation step is definitional (Q2); D3 checks the formula
against deal_into_piles + gather_order for every σ at every grid
config (all b! orders through b = 6, deterministic samples at b = 8).

## Lemma B (digit action of a round) — D2

The two summands of Lemma A are digit-disjoint, and each is digit-wise
explicit:

  * complement: for y in [0, b^k), digit_i(b^k - 1 - y) =
    (b-1) - digit_i(y). Induction on k (Q3): the identity
    b^k - 1 - (b·y' + d) = b·(b^(k-1) - 1 - y') + (b - 1 - d)
    is exact, and 0 <= b-1-d < b certifies it as the canonical
    decomposition, so digit 0 complements and the rest recurse.
  * high digit: for e = p·b^(m-1) + w with 0 <= w < b^(m-1) and
    0 <= p < b, digit_{m-1}(e) = p and digit_i(e) = digit_i(w) for
    i < m-1 (division uniqueness, ranges certified).

Together: writing x's digits (d_0, ..., d_{m-1}),

  digit_{m-1}(x') = rank_σ(d_0),
  digit_i(x')     = (b-1) - d_{i+1}      for i <= m-2.

Each round relabels the old low digit through the permutation
rank_σ, complements the remaining digits, and rotates every digit one
position down.

## Lemma C (agreement transport) — D4

Let p, q go through the SAME round (same σ, hence the same rank_σ).

  * High digits: rank_σ is a bijection, so
    rank_σ(d_0) = rank_σ(d'_0) iff d_0 = d'_0 (Q1a: injectivity of a
    permutation — prose-trivial).
  * Lower digits: ((b-1) - u) - ((b-1) - v) = -(u - v) exactly (D2),
    so digit i of the images agrees iff digit i+1 of the originals
    agrees.

Hence i ∈ A(p', q') iff (i+1) mod m ∈ A(p, q): one left rotation,
with no dependence on σ beyond bijectivity. D4 verifies the full
statement exhaustively at the single-round level: every ordered pair
× every gather order at (b, m) = (2,2), (2,3), (2,4), (3,2), (3,3),
(4,2), (5,2), (6,2), plus sampled orders at (8,2).

## Induction and adaptivity — Q1, D5

Q1 (prose): induct over rounds — each round applies rot once, so r
rounds apply rot^r. Adaptive strategies need no extra argument: for a
FIXED start pair, an adaptive strategy's run realizes some concrete
σ-sequence, so the set of pairs reachable adaptively is contained in
the union over σ-sequences — and the theorem holds for every
sequence. D5 grounds the multi-round claim exhaustively at small
sizes: all σ-sequences × all start pairs at (b, m, r) = (3, 2, 2) and
(2, 3, 3), checking A(final) = rot^r(A(start)) every time.

## The evenness hypothesis is load-bearing — D7

With N not a multiple of b the pile sizes differ, Lemma A's constant
q0 fails, and the complement structure breaks. D7 exhibits a concrete
violation at N = 10, b = 3: a pair and a gather order whose round
changes the agreement-set cardinality. This is the door t16 part B
walked through — uneven piles dissolve the obstruction, which is why
the 52-card double reveal exists at all. One phenomenon, two
theorems: the pile-size irregularity that corr(a) repairs for one
card ([PROOF.md](PROOF.md)) is the same irregularity that breaks this
conservation law for two.

## Corollary arithmetic — D6, D8

D6 checks the impossibility count at N = 27: exactly 216 of 702
ordered pairs differ in all three digits (27 · 2^3), so 486 start
pairs can never be sent to (top, bottom) — consistent with t16 part
A's exhaustive session-4 result, which stands on its own record
(reachable set per target = one agreement class). D8 checks
rot^3 = id on all 8 patterns at m = 3, the identity behind that
observed class structure.

## Scope and honesty

* Machine-checked (D2 symbolic, D3/D4/D5/D6/D7/D8 exhaustive): the
  decomposition identities with range certificates, the negation
  identity, and the theorem's one-round and multi-round content over
  every case at the grid sizes — the single-round check is EXHAUSTIVE
  in every quantifier (all pairs, all b! orders) at eight configs.
* Prose (Q1-Q3): the induction over rounds with the
  adaptivity-collapses-to-sequences argument, the definitional
  concatenation step of gather_order, and the digit-induction
  skeleton. Same character as P1-P3 in [PROOF.md](PROOF.md): standard
  finite arguments, no hidden case analysis.
* The theorem covers N = b^m exactly. For even-but-not-power sizes
  (N = b·k, k not a power of b) the digit framing does not apply as
  stated; the library's original claim (N = 27) and the battery's
  grid (b^m) sit inside the proven region. Uneven N is excluded and
  D7 shows the exclusion is necessary, not cautious.
* The refuter's grading of this entry (ROBUST_CONJECTURE, envelope
  m=5/b=4/rounds=136) remains its empirical record; THEOREM status
  comes from this artifact, per the ladder's design.
