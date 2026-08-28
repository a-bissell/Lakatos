# PROVENANCE — literature search logs for novelty claims

Engine item 7. Every LIBRARY.md entry that claims novelty ("NOVEL COMMIT",
"novelty candidate", "not found published", "no trace", "likely new") must
have a dated search record here, so the claim is auditable the way a
verify() count is. [provenance_audit.py](provenance_audit.py) enforces
this mechanically: it fails if a flagged entry lacks a record, if a record
points at a nonexistent entry, or if a KNOWN verdict is not acknowledged
in the entry itself.

Verdict vocabulary (controlled — the audit rejects anything else):

- **KNOWN** — the specific result is published. The library entry must
  acknowledge the rediscovery; the claim that stands is at most "derived
  independently / by the machine".
- **KNOWN-FAMILY** — the surrounding framework or family is charted in
  the sources listed, but the specific form claimed (the exact closed
  form, boundary, or composition) was not found under the logged
  queries. "Likely new" is permitted with the family cited.
- **NOT-FOUND** — no trace found under the logged queries. "Likely new"
  is permitted, explicitly relative to this log.

Every verdict is relative to its queries and date — a NOT-FOUND is a
statement about a search, never about the literature. Deeper searches
(magic literature databases, Conjuring Credits, journals behind paywalls)
supersede these records by appending, not editing.

All records below: searches run 2026-08-28 via web search (12 queries,
4 page fetches), sessions 14-15 engine work.

---

### mongean-position-law
entries: integrated-engine-loop
claim: the engine's first autonomous product — the Mongean shuffle
  position law newpos = (2j-1)*floor(x/2) + (q0 + rho + j - 1) — was
  tagged SURVIVOR with provenance pending.
date: 2026-08-28
verdict: KNOWN
queries:
  - "Monge shuffle Mongean shuffle position formula card mathematics"
sources:
  - Monge's Shuffle — Wolfram MathWorld — https://mathworld.wolfram.com/MongesShuffle.html — explicit closed-form relation between initial and final position after m Monge shuffles; single-shuffle position map is classical.
  - Ledet, The Monge Shuffle for two-power decks, Math. Scand. 98 (2006) — https://www.mscand.dk/article/download/14979/12974/34480 — order/structure results for the shuffle.
  - Monge Shuffle — Conjuring Credits — https://www.conjuringcredits.com/doku.php?id=cards:monge_shuffle — magic-literature lineage back to Monge 1773.
consequence: REDISCOVERY. Position tracking under the Monge shuffle has
  been published since Monge (1773); MathWorld carries the iterated
  closed form. The pipeline's value here is validation (oracle cleared it
  only because no Monge recognizer exists — a recognizer-coverage gap,
  not a discovery), and the LIBRARY entry now says so.

### reversed-rest-pickup-laws
entries: generator-v1-round-laws
claim: machine-fitted round-position closed forms for the reversed-rest
  pickup ("pile a on top, rest right-to-left"), b=3 and b=4, valid for
  every N >= b including N not divisible by b.
date: 2026-08-28
verdict: KNOWN-FAMILY
queries:
  - "Gergonne pile problem generalization pickup order arbitrary gather piles card trick mathematics"
  - "card trick 52 cards deal 4 piles then 13 piles two deals any position mixed radix targeting"
sources:
  - The Gergonne p-pile problem and the dynamics of x -> floor((x+r)/p), Discrete Applied Mathematics — https://www.sciencedirect.com/science/article/pii/S0166218X97001327 — treats np-card decks under "some fixed scheme for collecting and redistributing": arbitrary pickup schemes are in scope, but only for evenly divisible decks.
  - Quintero, Mathmagic: on a mathematical model for an old card trick, Recr. Math. Mag. (2017) — https://sciendo.com/pdf/10.1515/rmm-2017-0014 — generalizes the three-pile trick to any a*b-card deck (fixed-point convergence, 222 generated tricks, 3-7 piles); abstract confirms evenly divisible decks only.
consequence: arbitrary collection orders on EVEN decks sit inside the
  charted p-pile framework, so the b | N slice of these laws should be
  considered known territory. The uneven-N closed forms (the q0/rho
  case-split intercepts for N mod b != 0) were not found under these
  queries. Claim allowed: "likely new for N not divisible by b, family
  charted."

### uneven-radix-closed-forms
entries: alternating-radix-law, universal-radix-law, four-pile-universal-law, general-b-radix-law, six-pile-bucket-rule
claim: closed-form pickup-vector laws for any-card-any-position targeting
  with b piles and ANY deck size N (uneven piles included): the
  alternating-radix recursion, the universal integer form, the base-(-4)
  analog, the general-b corr(a) law with validity b^(r-1) >= N, and the
  six-pile bucket rule.
date: 2026-08-28
verdict: KNOWN-FAMILY
queries:
  - "Bolker Gergonne card trick positional notation radix sort"
  - "Gergonne card trick deck size not multiple of piles uneven piles 52 cards any card any number"
  - "Generalized Gergonne trick continuous approximation unequal piles abstract"
sources:
  - Bolker, Gergonne's Card Trick, Positional Notation, and Radix Sort, Math. Mag. 83:1 (2010) — https://maa.org/sites/default/files/Bolker-MMz-201053228.pdf — radix-sort view and generalizations for b^r decks.
  - The Gergonne p-pile problem and the dynamics of x -> floor((x+r)/p), Discrete Applied Mathematics — https://www.sciencedirect.com/science/article/pii/S0166218X97001327 — iterate formulas and fixed points for the floor-map dynamics, np-card decks.
  - Quintero, Mathmagic (2017) — https://sciendo.com/pdf/10.1515/rmm-2017-0014 — a*b-card decks, one/two stable fixed points per collection function; convergence tricks, not any-position targeting.
  - Generalized Gergonne's Trick and its Continuous Approximation (2016) — https://www.researchgate.net/publication/299466566_Generalized_Gergonne's_Trick_and_its_Continuous_Approximation — dynamical-systems view (attracting fixed points); abstract shows power-of-b examples.
consequence: the floor-map dynamics of Gergonne deals are thoroughly
  charted, INCLUDING general iterate formulas — but every source found
  works with evenly divisible decks and/or convergence to a fixed
  position. Not found: any-card-any-NAMED-position pickup-vector laws
  for N not divisible by b (the corr(a) = min(a,rho)*(b - max(a+1,rho))
  correction), the argmin/bucket digit rule, or the b^(r-1) >= N
  sufficiency boundary with its non-necessity examples. Claim allowed:
  "likely new in this specific algorithmic form; territory charted."
  This matches the wording already in [[alternating-radix-law]].

### two-card-shared-gather
entries: two-card-agreement-conservation, double-reveal-uneven, double-reveal-performable
claim: the two-spectator shared-deal targeting problem — its even-pile
  conservation obstruction (digit-agreement pattern conserved by every
  gathering strategy) and its uneven-pile adaptive/reactive solutions.
date: 2026-08-28
verdict: NOT-FOUND
queries:
  - "card trick two spectators two selected cards dealt piles simultaneously located mathematics Gergonne"
  - "card trick locate two chosen cards two spectators piles mathematics impossibility conserved"
sources:
  - Gergonne's Magic Trick — cut-the-knot — https://www.cut-the-knot.org/Curriculum/Magic/GergonneMagic.shtml — single-card treatments only.
  - Exploring and Extending the Impossible Card Location Trick, College Math. J. 52:5 (2021) — https://www.tandfonline.com/doi/abs/10.1080/07468342.2021.1967696 — multi-card location via deck CUTS, a different mechanism (no shared pile deals).
  - Card Dealing Math, arXiv:2509.11395 (2025) — https://arxiv.org/abs/2509.11395 — recent 39-page survey of dealing-pattern tricks; single tracked card throughout the abstract and blog coverage.
consequence: no trace found of two cards tracked through SHARED
  deal-and-gather rounds — neither the conservation obstruction nor the
  uneven-pile constructions. These remain the library's strongest
  novelty candidates. Standing wording in the entries is consistent with
  this log.

### targeting-elimination-compositions
entries: any-card-any-packet-size, radix-target-down-under-reveal, down-under-survivor-position
claim: compositions that chain radix targeting into a down-under
  elimination finale, including the variable-packet-size form (target
  J(n) via mixed-radix placement, deal off n, eliminate).
date: 2026-08-28
verdict: KNOWN-FAMILY
queries:
  - "under down deal card trick spell target position any card any number mathematics Josephus"
sources:
  - Card Dealing Math, arXiv:2509.11395 (2025) — https://arxiv.org/pdf/2509.11395 — under-down dealing = Josephus, recursive formulas, existing and novel tricks; includes effects where the chosen card is dealt last with audience control over the count.
  - Between mathematics and magic: the Josephus legend and the down-under shuffle — https://doaj.org/article/f6b12dde707d40a2a597dd25197150c2 — the Josephus/down-under correspondence, long charted.
consequence: J(n) and down-under trickery are classical and freshly
  re-surveyed (2025); "chosen card dealt last despite audience-chosen
  count" effects EXIST in that literature, so the genre of t13 is
  charted. Not found: the specific composition where a mixed-radix
  targeting phase computes the J(n) landing spot for a freely named
  packet size with a freely thought-of card. Claim allowed: "components
  classical; this composition not found under logged queries."

### adaptive-spell-stack
entries: spell-your-own-card
claim: a stack encoding spell length in position mod 4 combined with an
  ADAPTIVE pickup (branching on the spectator's public pile answer) so
  every card lands at its own name's spell length.
date: 2026-08-28
verdict: KNOWN-FAMILY
queries:
  - "spell your card trick stack setup spelling length mathematics self-working adaptive"
sources:
  - Spelling Bee (card trick) — Wikipedia — https://en.wikipedia.org/wiki/Spelling_Bee_(card_trick) — the spelling-trick genre with prepared stacks is classical and extensively catalogued.
consequence: spelling reveals from prepared stacks are a standard genre.
  Not found: the residue-class encoding + pile-answer-adaptive pickup
  mechanism. Claim allowed: "genre classical; adaptive mechanism not
  found under logged queries."

### gilbreath-rediscovery
entries: gilbreath-principle, gilbreath-suit-divination
claim: committed as NOVEL-to-library (first spectator-shuffle invariant
  and first spectator-shuffle reveal in this library).
date: 2026-08-28
verdict: KNOWN
queries:
  - "card trick two spectators two selected cards dealt piles simultaneously located mathematics Gergonne"
sources:
  - Twenty-One Card Trick — Wikipedia — https://en.wikipedia.org/wiki/Twenty-One_Card_Trick — context for the classic-trick canon.
  - AMS Feature Column (Mulcahy) — https://www.ams.org/publicoutreach/feature-column/fcarc-mulcahy5 — Gilbreath-principle effects, including suit-based reveals, are standard repertoire.
consequence: REDISCOVERY, and always recorded as such — the entries
  cite Gilbreath (1958, 1966) and claim only their exhaustively
  verified domains. "NOVEL COMMIT" in those entries means novel TO THIS
  LIBRARY (first spectator-shuffle mechanism class here), not novel to
  the literature; this record makes that reading explicit.

### digitsum-force-composition
entries: center-then-digit-sum-force, merged-digitsum-force
claim: composition of center convergence with the 10-20 digit-sum force
  (and its merged form absorbing the adjustment into the last pickup).
date: 2026-08-28
verdict: KNOWN-FAMILY
queries:
  - "10-20 force OR ten twenty force card trick digit sum casting out nines count"
sources:
  - The 10-20 Force — https://magichobbyist.org/maths/mathsforce10to20.html — the digit-sum force is classical (casting out nines, force position 9).
  - Casting out nines — Wikipedia — https://en.wikipedia.org/wiki/Casting_out_nines — the underlying arithmetic.
consequence: the force is classical; the specific composition with
  3-pile center convergence (and the merged-pickup variant) was not
  found. Claim allowed: "force classical; composition not found under
  logged queries."

### mixed-radix-and-adaptive-methods
entries: mixed-radix-full-deck-targeting, uneven-pile-adaptive-targeting
claim: two-deal any-card-any-position targeting of a full 52-card deck
  via mixed radix (4x13), and the backward-induction strategy-tree
  method for uneven piles.
date: 2026-08-28
verdict: KNOWN-FAMILY
queries:
  - "card trick 52 cards deal 4 piles then 13 piles two deals any position mixed radix targeting"
  - "card trick adaptive strategy backward induction pile choice conditioned observed answers mathematics"
sources:
  - Bolker, Gergonne's Card Trick, Positional Notation, and Radix Sort (2010) — https://maa.org/sites/default/files/Bolker-MMz-201053228.pdf — radix generalizations of Gergonne targeting; the natural home of mixed-radix variants.
  - Backward induction — Wikipedia — https://en.wikipedia.org/wiki/Backward_induction — the method itself is standard game theory.
consequence: radix-sort targeting generalizations are charted (Bolker),
  and backward induction is textbook — but neither the explicit 4x13/
  13x4 two-deal full-deck any-position procedure nor the application of
  strategy-tree synthesis to uneven-pile card targeting was found under
  these queries. Claim allowed: "family charted; specific procedure and
  method application not found."
