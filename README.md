# Lakatos Engine

A derive-and-verify system for self-working card tricks, and an engine
that automates the derivation loop with its skepticism built in.

The project has one rule: nothing counts as working unless `verify()`
in [deck_sim.py](deck_sim.py) passes over the **entire** free-choice
domain — every thinkable card, every namable number, every possible
shuffle in the claimed range. Correctness is decided by the harness,
never by an argument about the procedure. Everything else in the repo
exists to keep that rule honest at scale: recognizers so rediscoveries
cannot pose as novelties, adversarial batteries so narrow testing
cannot pose as robustness, provenance logs so unsearched claims cannot
pose as new, and a proof layer for the one result that earned it.

## Headline results

- **The general-b radix law** (THEOREM,
  [PROOF.md](PROOF.md)): dealing N cards into b piles and gathering
  with `a` piles above the pointed pile acts on the doubled centered
  coordinate as `z <- -b·z + (2a+1-b)·N + 2·corr(a)` with
  `corr(a) = min(a,ρ)·(b - max(a+1,ρ))`, `ρ = N mod b`. Choosing each
  digit to minimize `|z|` yields a pickup vector that brings any
  thought-of card to any named position, for any N ≥ b, whenever
  `b^(r-1) ≥ N`. Proven over the whole hypothesis region and verified
  on ~76k cases across b = 2..8.
- **Full-deck any-card-any-number in six physical steps**: b=6, three
  deals, with a fixed threshold table replacing all arithmetic
  ([tricks/t23_six_pile_buckets.py](tricks/t23_six_pile_buckets.py)).
  A four-deal version with even piles and a quarter-bucket rule is in
  [tricks/t21_four_pile_law.py](tricks/t21_four_pile_law.py).
  Performance protocols: [HOWTO.md](HOWTO.md).
- **A two-card conservation law** (THEOREM,
  [PROOF_conservation.md](PROOF_conservation.md)): with even piles
  (N = b^m), each round rotates the pattern of digit positions where
  two tracked cards agree by exactly one place, under every gathering
  strategy — so double targeting is impossible at any depth unless
  the start pair sits in the target pair's rotated agreement class.
  Uneven piles dissolve the obstruction and adaptive strategies exist
  ([tricks/t16_double_reveal.py](tricks/t16_double_reveal.py), a
  performable 11-card version in t17). No trace of this question was
  found in the literature searched ([PROVENANCE.md](PROVENANCE.md)).
- **Machine-derived laws**: the pipeline re-derived the general-b
  round law from black-box behavior without hints (t25), produced the
  Mongean shuffle position law autonomously (a rediscovery — Monge
  1773 — and recorded as such), and discovered position laws for a
  pickup order outside the classical gather family (reversed-rest,
  b=3 and b=4).

## The engine

    generator -> novelty oracle -> conjecture former -> refuter
                (log & suppress)   (exact fits,        (signature-derived
                                    refusal allowed)    attack schedules)

- [generator.py](generator.py) invents candidates from question
  schemas over the op vocabulary. It is deliberately ignorant of what
  is known; the oracle decides.
- [novelty_oracle.py](novelty_oracle.py) recognizes library-known
  material extensionally and suppresses it into a drift log. Partial
  samples abstain instead of matching.
- [former.py](former.py) fits exact closed forms (rational RREF,
  model trees over atom comparisons) from behavior alone, and refuses
  what its grammar cannot express. It imports nothing from the
  project; an acceptance ledger scans its source to keep it that way.
- [refuter.py](refuter.py) + [refuter_auto.py](refuter_auto.py) grade
  every claim by attacking it with schedules derived from its
  parameter signature — floor probes, escalation beyond the inspiring
  scale, residue-breaking probes — and report per-axis envelopes with
  no silent caps.
- [engine.py](engine.py) runs the loop under candidate-atomic budgets
  with eight dispositions and a bounded repair loop (a refutation
  witness joins the fit grid and the former refits).

Verdicts are graded: `REFUTED` (with witness) < `CONJECTURE` <
`ROBUST_CONJECTURE` (with envelope) < `THEOREM`. The refuter cannot
promote anything to THEOREM; only a proof artifact can, and three
entries hold one: the general-b law, the two-card conservation law,
and the largest-first ACAAN (a reflection conjugate of the first,
[PROOF_reversed_rest.md](PROOF_reversed_rest.md)). Design notes for
the oracle/refuter layer are in
[ENGINE.md](ENGINE.md); the full history of the engine build is in
[CAPSTONE.md](CAPSTONE.md).

## Repository map

| Path | Contents |
|---|---|
| [deck_sim.py](deck_sim.py) | simulator + `verify()`/`verify_prop()` harness (ground truth) |
| [tricks/](tricks/) | 24 runnable proofs, t2–t25; each prints its own verification ledger |
| [LIBRARY.md](LIBRARY.md) | 35 verified entries with domains, scores, and session log |
| [PROOF.md](PROOF.md) / [proof.py](proof.py) | theorem #1 (general-b law) and its machine checks |
| [PROOF_conservation.md](PROOF_conservation.md) / [proof_conservation.py](proof_conservation.py) | theorem #2 (two-card conservation) |
| [PROOF_reversed_rest.md](PROOF_reversed_rest.md) / [proof_rr.py](proof_rr.py) | theorem #3 (largest-first ACAAN, via reflection conjugacy) |
| [PROVENANCE.md](PROVENANCE.md) / [provenance_audit.py](provenance_audit.py) | literature search records and the audit that enforces them |
| [HOWTO.md](HOWTO.md) | human performance protocols for the ACAAN family |
| [HOWTO_double_reveal.md](HOWTO_double_reveal.md) | performance protocol for the 11-card two-spectator double reveal |
| [tasks.md](tasks.md) | queue, budgets, and backlog |
| [files/agent_prompt.md](files/agent_prompt.md) | the original project spec |

## Running the checks

Everything is plain Python 3; [proof.py](proof.py) additionally needs
`sympy`. Each module runs its unit checks at import and prints a
ledger when executed directly.

```bash
python3 deck_sim.py            # harness self-check (21-card trick)
```

```bash
cd tricks && python3 t22_general_b_law.py   # the law, 32,896 cases
```

```bash
python3 engine.py              # pipeline dry run, 9/9 (~1s)
```

```bash
python3 generator.py           # generator metric ledger, 11/11 (~2s)
```

```bash
python3 former_acceptance.py   # former ledger, 6/6 incl. no-hints guard
```

```bash
python3 refuter_battery.py     # whole-library battery, 7/7 (~3.7M cases, ~100s)
```

```bash
python3 provenance_audit.py    # novelty-claim coverage audit
```

```bash
python3 proof.py               # theorem #1 checks C1-C10 (~30s)
```

```bash
python3 proof_conservation.py  # theorem #2 checks D1-D8 (~30s)
```

## Honesty notes

Several entries record the project catching its own errors: an
adaptive mechanism that turned out to be classical under audit, an
impossibility claim overturned one session later, a machine fit
refuted by its own battery, a false robustness stamp produced by a
curated test set and killed by a derived one, and a missing case in
the proof found by the proof kernel. These are kept in
[LIBRARY.md](LIBRARY.md) and [CAPSTONE.md](CAPSTONE.md) deliberately:
the guardrails are the point of the repo, and their catches are the
evidence they work. Provenance verdicts are relative to the logged
queries only — web search, no magic-literature databases — and say so.
