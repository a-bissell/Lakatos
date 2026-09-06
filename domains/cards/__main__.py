"""python3 -m domains.cards — the wiring's structural conformance ledger.
The checks run at package import; this prints the verdict line."""
import domains.cards  # noqa: F401  (import-time checks are the ledger)

print('domains/cards wiring: PASS (plugs validated, Decider conforms, '
      'DECIDER.instance_test is exhaustive by construction, toy triple '
      'holds/fails as built). Full conformance ledger: python3 engine.py')
