"""domains/cards — the card domain wired into the lakatos engine.

FRAMEWORK.md step 5: this package is the canonical answer to the four plugs
of lakatos/protocols.py, so a second domain has a worked example to copy.
The card modules themselves still live at the repo root (their relocation
into this package is the deferred pure move of FRAMEWORK.md §6); this
package is the WIRING, and root engine.py consumes it.

  Plug 1  Decider           DECIDER — deck_sim.verify / verify_prop over
                            make_deck (52 cards) or make_packet(N) (abstract
                            tokens), adapted to the universal triple
  Plug 2  Recognizers       novelty_oracle.classify — the five-family card
                            dispatcher over lakatos.oracle's policy
  Plug 3  Candidate source  generator.generate_candidates (schema-driven) and
                            engine.dry_run_candidates (the fixed acceptance
                            mix); any iterable of EngineCandidate works
  Plug 4  Parameter sig.    pure data on each candidate; nothing to wire

Conformance: import-time checks here are structural (plug shapes, the
Decider triple on a toy packet). The REAL conformance ledger is the engine
dry-run — `python3 engine.py` from the repo root replays a fixed candidate
mix through every disposition. Import this package from the repo root.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from lakatos.protocols import Decider, check_plugs
from deck_sim import verify, verify_prop, make_deck, make_packet
from novelty_oracle import classify, Candidate as OracleCandidate
from former import fit_round_model, make_instance_test


class CardDecider:
    """Plug 1 — deck_sim's exhaustive harness as the Decider protocol.

    claim is (trick, reveal) for card-reveal effects or ('prop', trick,
    predicate) for structural properties (verify_prop); domain is the full
    iterable of free choices. deck_factory defaults to the 52-card deck;
    pass e.g. lambda: make_packet(81) for abstract packets. Adapts
    deck_sim's (ok, counterexamples) to the universal triple — the witness
    is the FIRST counterexample; the full set stays available via
    deck_sim.verify directly (diagnosis is the highest-value output)."""

    def check(self, claim, domain, deck_factory=make_deck):
        cases = list(domain)
        if claim[0] == 'prop':
            _, trick, predicate = claim
            ok, counter = verify_prop(trick, cases, predicate, deck_factory)
        else:
            trick, reveal = claim
            ok, counter = verify(trick, cases, reveal, deck_factory)
        return (ok, counter[0] if counter else None, len(cases))


DECIDER = CardDecider()

PLUGS = dict(classify=classify, fit=fit_round_model,
             make_instance_test=make_instance_test)

__all__ = ['DECIDER', 'CardDecider', 'PLUGS', 'classify', 'fit_round_model',
           'make_instance_test', 'verify', 'verify_prop', 'make_deck',
           'make_packet', 'OracleCandidate']


# ---- conformance checks (run at import; structural + a toy decider triple) ---

def _unit_wiring():
    check_plugs(**PLUGS)
    assert isinstance(DECIDER, Decider)
    # identity trick on a 4-token abstract packet: exhaustive, holds
    ok, w, n = DECIDER.check(
        (lambda deck, ch: deck, lambda final, ch: final[ch['card']]),
        [{'card': c} for c in range(4)],
        deck_factory=lambda: make_packet(4))
    assert ok and w is None and n == 4, (ok, w, n)
    # off-by-one reveal: fails, witness is a (choices, got, want) case
    ok, w, n = DECIDER.check(
        (lambda deck, ch: deck, lambda final, ch: final[(ch['card'] + 1) % 4]),
        [{'card': c} for c in range(4)],
        deck_factory=lambda: make_packet(4))
    assert not ok and w is not None and n == 4, (ok, w, n)


_unit_wiring()


if __name__ == '__main__':
    print('domains/cards wiring: PASS (plugs validated, Decider conforms, '
          'toy triple holds/fails as built). Full conformance ledger: '
          'python3 engine.py')
