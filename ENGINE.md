# card_stuff — engine (oracle branch)

A meta-system for turning verified card-procedure search into an honest
theorem-hunt. The card domain is a testbed; the goal is a loop that resists its
own drift toward confident-but-wrong. Three modules so far.

## Modules

### `deck_sim.py` — verifier (ground truth)
Deterministic simulator. Self-working card procedures have tiny finite
free-choice domains, so `verify()` / `verify_prop()` brute-force the **entire**
domain. The harness decides correctness, never a narrative about it.

### `refuter.py` — adversarial promotion path
Turns "passes verification" into a graded, **adversarial** verdict. Built to
want conjectures dead. Reports the *false-confidence delta*: what a confirmatory
loop (test only inspiring scales) would commit, minus what survives attack.

Status ladder — labels are load-bearing:

| status | meaning | logical status |
|---|---|---|
| `NOT_A_CANDIDATE` | fails at its own inspiring scales | — |
| `REFUTED` | counterexample found (witness recorded) | **sound**: a kill is real |
| `ROBUST_CONJECTURE` | survived the adversarial battery; no proof | **incomplete**: "unrefuted within the declared, escalated envelope" |
| `THEOREM` | has a proof | **unreachable by this module, by design** |

A `ROBUST_CONJECTURE` must carry its envelope (which axes escalated, to what
scale, under what budget). "Robust" always means "within this envelope."

Known limit: the refuter is only as strong as its attack generator. A *curated*
adversary launders the author's blind spots into a false robust stamp; use
**automated, monotone scale-escalation**, not hand-picked attacks. (Demonstrated
in `__main__`: a late-breaking false conjecture that a curated adversary passes
and escalation kills.)

### `novelty_oracle.py` — rediscovery filter (not a novelty certifier)
Matches a candidate's **behavior** (the permutation it induces, or the invariant
it preserves) against five known families: Gergonne, Faro, Josephus, Gilbreath,
Hummer. Matches on what the procedure *does*, never on what the code looks like —
so a Gergonne procedure dressed up as "new" is still caught.

Asymmetric error policy (the core design choice):
- **false NOVEL** (miss a rediscovery) → recoverable downstream.
- **false KNOWN** (kill a real result) → invisible & catastrophic.
So recognizers **abstain when unsure** rather than declare KNOWN, and every match
is **logged with a witness** (log-and-suppress) so a false KNOWN is auditable.

Verdicts: `MATCHED(family, witness)` → suppressed/logged · `ABSTAIN` → routed
onward + surfaced for review · `NOT_MATCHED(checked families)` → routed onward.

`NOT_MATCHED` is **not** "novel". It means "not obviously one of the checked
families" (permutation kind checks Gergonne/Faro/Josephus; property kind checks
Gilbreath; Hummer is declared but unimplemented — the op vocabulary has no
orientation primitives, so it is deliberately not wired and cannot emit a false
KNOWN). The suppressed log doubles as a diagnostic: the fraction suppressed as
(e.g.) Gergonne over a long run measures whether the generator is exploring or
orbiting the known.

Measured properties (see self-audit): 0 / 20,000 random permutations false-match
Gergonne; one faro↔Gergonne signature overlap that fails **safe** (→ ABSTAIN, not
a false KNOWN). Residual false-KNOWN vector: **under-sampling** — CLOSED by the
post-audit sampling pin: candidates declare a `sample_scope`, the scope is
written into the log, and a signature match on a partial sample ABSTAINS
(surfaces for review) instead of suppressing. See AUDIT.md for the audit that
motivated these fixes — including the case where the audit corrected the
auditor (t15 is extensionally Gergonne-family; fixed 5-vectors cover 52/52
targets on uneven piles).

## What is NOT built (honest map)
- **Generator with expanding representation** — the inventive core; the real
  research risk. A fixed deal/gather/spell vocabulary can only rediscover.
- **Literature half of novelty** — provenance-scoped search for what clears the
  oracle + refuter.
- **Proof step** — the only thing that reaches `THEOREM` from `ROBUST_CONJECTURE`.
- **Integration loop** — generator → oracle (suppress) → conjecture → refuter,
  with budgets and the suppressed log as the live drift metric.

## Run
```
python3 deck_sim.py         # harness self-test
python3 refuter.py          # confirmatory-vs-adversarial verdicts
python3 novelty_oracle.py   # family recognizers + suppressed log
```
