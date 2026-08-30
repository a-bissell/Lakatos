# FRAMEWORK.md — the core/domains split

*A design sketch for extracting the Lakatos discovery engine from the card
domain. The thesis: the engine that turns "search" into an honest theorem-hunt
is domain-agnostic; cards are a testbed chosen because self-working procedures
have a tiny finite free-choice domain, so ground truth is a cheap exhaustive
check.*

## 0. Why this is mostly already done

The current coupling, read straight off the imports:

| module | imports from `deck_sim` | verdict |
|---|---|---|
| `refuter_auto.py` | **none** (only `dataclasses`) | **already core** |
| `former.py` | **none** (only `fractions`) | **already core** (the fitter math) |
| `refuter.py` | `deal_into_piles, gather_position` — **only in the `__main__` demo** | core + a demo to move out |
| `novelty_oracle.py` | deck ops, used by the `_match_*` recognizers | split: policy is core, recognizers are content |
| `proof.py` | deck ops + `sympy` | split: Farkas kernel is core, C1–C10 are content |
| `engine.py` | oracle/former/refuter (no deck ops) | core loop; imports become the seam |
| `generator.py` | deck ops + oracle + engine | content (the question schemas) |

So the extraction is not a rewrite. It is: (a) move two files as-is, (b) split
three files along a line that already exists inside them, (c) turn four
hardcoded call sites into injected plugs.

## 1. The one principle

**`core/` may not import from any domain. Domains provide four plugs and
inherit everything else.** The universal currency between them is one triple,
which the code already speaks everywhere:

```
(holds: bool, witness: Any|None, n_cases: int)
```

That is exactly what `deck_sim.verify()` returns, what
`Conjecture.instance_test` returns, and what the refuter attacks over. It never
mentions cards.

## 2. Directory layout

```
core/
  ladder.py       status ladder + Envelope (the load-bearing labels)
  decider.py      the Decider protocol + the exhaustive-check contract
  refuter.py      Conjecture, refute(), confirmatory_verdict, false-confidence delta
  schedule.py     Axis, derive_schedule(), auto_conjecture()   [= refuter_auto.py, verbatim]
  fitter.py       _Echelon, exact_fit, fit_tree, tree_eval     [= former.py fitter core, verbatim]
  oracle.py       SuppressedLog + classify() policy engine     [recognizers injected]
  engine.py       run_engine(): budgets, 8 dispositions, drift metric [plugs injected]
  provenance.py   the audit: novelty claims require dated records
  proof_kernel.py Ctx, nonneg(), infeasible(), base_ctx()      [Farkas cert kernel]

domains/cards/
  decider.py      deck_sim: make_packet, deal/gather/spell ops, verify/verify_prop
  recognizers.py  _match_gergonne/faro/josephus/gilbreath/library_targeting
  schemas.py      generator q_* question schemas + Axis signatures per schema
  round_model.py  fit_round_model, FittedRoundModel (the card-shaped fit target)
  proofs/         C1–C10 (general-b), conservation, reversed-rest
  provenance/     PROVENANCE.md records

  # every existing .md (ENGINE, CAPSTONE, HOWTO*, PROOF*) is domain narrative
```

## 3. The four plugs

Each is grounded in a contract the code already implements.

### Plug 1 — Decider  *(the one non-negotiable)*
Replaces `deck_sim.verify` / `verify_prop`. A domain is admissible **only if it
has a total, deterministic, exhaustive check over a bounded free-choice
domain.** This is the seam that makes every downstream guarantee real; a domain
without it can still use the loop but the refuter degrades to sampling and the
false-confidence delta loses its teeth.

```python
class Decider(Protocol):
    def check(self, claim, domain) -> tuple[bool, Any, int]:
        """Evaluate `claim` over the ENTIRE free-choice `domain`.
        Returns (holds, witness_or_None, n_cases). Total & deterministic:
        the harness decides correctness, never a narrative about it."""
```

Cards satisfy it because a self-working trick's free choices are a handful of
cuts/positions — brute-forceable whole. `make_packet(N)` + `deck_factory` (engine
item 1) is what let the same decider run at N=144; that generalization is the
template for every port.

### Plug 2 — Recognizers  *(known-result filter)*
A domain supplies a list; `core/oracle.classify()` runs the **policy** over them
unchanged. Current recognizers already return exactly this shape:

```python
class Recognizer(Protocol):
    family: str
    def __call__(self, cand) -> dict | None:
        # {'family': str, 'confidence': 'exact'|'abstain', 'witness': str}  or None
```

The core policy — **asymmetric error** (false KNOWN is invisible & catastrophic
→ abstain when unsure), **log-and-suppress with a witness**, the **sampling
pin** (partial-sample match ABSTAINs), abstain-on-multiple-match — is
domain-free and stays in core. Only the tuple at `novelty_oracle.py:301-307`
changes: from hardcoded to injected.

```python
def classify(cand, recognizers, log) -> dict:   # was: recognizers hardcoded
```

The suppressed-log summary is the **drift metric** for any domain: fraction
suppressed-as-known = "are we exploring or orbiting what we already know?"

### Plug 3 — Candidate source  *(the inventive core; the real research risk)*
A domain yields candidates; the envelope is already generic
(`EngineCandidate(name, provenance, oracle_view, parametric, conjecture_spec)`),
the *schemas* that fill it are content.

```python
class CandidateSource(Protocol):
    def __iter__(self) -> Iterator[Candidate]: ...
    # each Candidate carries any subset of:
    #   oracle_view()   -> object the Recognizers match on (behavioral)
    #   parametric      -> {query, fit_grid, axes, valid, cost, cap, claim}  (for the fitter)
    #   conjecture_spec -> {instance, axes, inspiring, valid, cost, cap, claim} (ready claim)
```

Honest note carried over from ENGINE.md: a fixed vocabulary can only
*rediscover*. Expanding representation is the unsolved part in **every** domain,
not a card limitation.

### Plug 4 — Parameter signature  *(pure data; core needs zero changes)*
The refuter attacks from a signature, never from domain objects.
`schedule.derive_schedule` and `refuter.refute` already consume only this:

```python
axes      : list[Axis]        # Axis(name, lo, step='linear'|'increment')
inspiring : list[tuple]       # params that suggested the pattern
valid, cost, cap              # domain predicates over params
instance_test : Callable[..., tuple]   # params -> (ok, witness, n_cases)   <- Plug-1 triple
```

`refuter_auto.py` proves this is already clean: it imports nothing but
`dataclasses`. Move it to `core/schedule.py` untouched.

## 4. What core keeps, unchanged in spirit

- **The status ladder** `NOT_A_CANDIDATE → REFUTED → ROBUST_CONJECTURE →
  THEOREM`, with `ROBUST_CONJECTURE` *required* to carry its envelope and
  `THEOREM` *structurally unreachable* except via a proof artifact. Pure Lakatos;
  no cards.
- **The refuter**: monotone scale-escalation, floor probes, multi-anchor walks,
  envelope-edge bisection, no-silent-caps, the false-confidence delta, and the
  laundering specimen (curated adversary stamps a false ROBUST; derived schedule
  kills it at the floor). All operate on Plug 4.
- **The fitter**: `exact_fit` (rational RREF, early inconsistency exit),
  `fit_tree` (model trees over atom comparisons), **refusal as a first-class
  outcome**, and the no-hints boundary (scan the fitter's own source for domain
  vocabulary so it can't import the answer).
- **The engine loop**: candidate-atomic budgets, every skip named (no silent
  truncation), eight dispositions, dry-run-as-acceptance-ledger.
- **The provenance audit**: a novelty claim without a dated record fails; makes
  "likely new" as auditable as a case count.
- **The proof kernel**: `Ctx`/Farkas certificates + exact identity checks, with
  the irreducibly-prose steps *named* rather than hidden.

## 5. The three real splits (everything else is a move)

1. **`novelty_oracle.py`** → `core/oracle.py` (SuppressedLog + `classify` policy)
   + `domains/cards/recognizers.py` (the five `_match_*`). Line of the cut
   already visible at 301–307.
2. **`proof.py`** → `core/proof_kernel.py` (`Ctx`, `nonneg`, `infeasible`,
   `base_ctx`) + `domains/cards/proofs/` (C1–C10 and the law algebra). The
   kernel already knows nothing about the specific inequalities.
3. **`former.py`** → `core/fitter.py` (`_Echelon`, `exact_fit`, `fit_tree`,
   `tree_eval` — already zero-dependency) + `domains/cards/round_model.py`
   (`fit_round_model`, `FittedRoundModel` — card-shaped: slope/const trees over
   b, N). The generic fitter does not know a "round" from a "row."

`refuter.py` needs only its `__main__` radix demo relocated to a domain example;
`refuter_auto.py` and the engine loop move as-is with imports swapped for
injected plugs.

## 6. Migration order (each step leaves the tree green)

1. **DONE** (commit `b13680a`). `git mv refuter_auto.py` → `core/schedule.py`
   (verbatim; only `dataclasses`); `former.py` fitter core → `core/fitter.py`,
   parameterized by an injected `FeatureBasis` so core carries no card/law
   knowledge. `former.py` keeps only `ROUND_BASIS` + extraction, re-exposing
   every public signature via thin wrappers (−164 net lines). No-hints guard
   hardened to scan both files. Green: former_acceptance 6/6, engine 13167
   cases, refuter_battery 8/8 (3.92M), t25 PASS.
2. **DONE** (commit `473496c`). Extracted the asymmetric-error POLICY to
   `core/oracle.py` (`SuppressedLog`, `classify`, `RecognizerSet`);
   `novelty_oracle.py` became a thin dispatcher supplying the five card
   recognizers, with the two domain-specific policy inputs injected (`refine`
   = LibraryTargeting ≻ Gergonne; `note` = Hummer disclosure). All four
   importers untouched via re-export. Green: oracle_audit + library_known_audit
   ACCEPTANCE PASS, t18–t23 MATCH / t16/t17 route on, generator 11/11.
3. **DONE**. Extracted the Farkas kernel (`zero`, `Ctx` with
   `nonneg`/`infeasible`) to `core/proof_kernel.py`, sympy-only, with a
   generic-symbol self-test at import; `proof.py` keeps the card symbols,
   `base_ctx`, the law algebra, and C1–C10, importing + re-exporting the
   kernel so `proof_conservation.py` (theorem #2) and `proof_rr.py`
   (theorem #3) are untouched. Green: C1–C10 PASS (27,700 cases), D1–D8
   PASS, E1–E8 PASS.
4. **DONE**. The loop is now domain-agnostic in `core/engine.py`, taking three
   injected plugs (keyword-only): `classify` (oracle dispatcher), `fit`
   (former), `make_instance_test`. `engine.py` at root became card wiring — it
   supplies `novelty_oracle.classify` + `former.fit_round_model` and keeps the
   dry-run acceptance ledger; `generator.py`'s `from engine import …` is
   untouched. The refuter's generic core (`Conjecture`, `confirmatory_verdict`,
   `refute` — dataclass + `typing`, no `deck_sim`) moved with it to
   `core/refuter.py`, leaving `refuter.py` as card wiring (`radix_place`,
   `targeting_instance`, drift specimens) that re-exports for
   former_acceptance/refuter_battery; this also fixed a step-1 core→root leak
   (`core/schedule.py` now imports `Conjecture` from `core.refuter`). Green:
   engine dry-run 13167 cases, generator 11/11, former_acceptance 6/6.
5. Define the four `Protocol`s in `core/` as the published contract; write a
   `domains/cards/__init__.py` that wires the plugs. The engine dry-run is now
   the framework's conformance test for the cards domain.

*Note: steps 1–2 kept the card domain files at repo root (as step 1 did for
`deck_sim`/`former`); the `domains/cards/` relocation in §2 is a later pure
move, deferred so each core extraction stays a small, green-at-every-step
commit.*

## 7. Admissibility test for a second domain

Before porting, a candidate pursuit must answer:

- **Decider?** Is there a total, deterministic, exhaustive check over a bounded
  free-choice domain? *(No → the engine runs but downgrades to sampling; say so.)*
- **Alphabet + schema?** A candidate vocabulary and at least one question
  schema. *(Fixed vocab ⇒ rediscovery only.)*
- **Known-result recognizers?** With the abstain/witness contract. *(Absence of a
  match is never evidence of novelty — the Mongean-law coverage gap is the
  cautionary case.)*
- **Parameter signature?** Axes + scale + `instance_test`, so the refuter can
  escalate.

Plausible fits: combinatorial-identity hunts, small-algorithm/heuristic
discovery with a test oracle, decidable puzzle/game families, program synthesis
with a checkable spec. Poor fits: open-world or stochastic-oracle domains, where
"the harness decides, never a narrative" cannot hold.
