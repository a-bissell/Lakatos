"""core/ — the domain-agnostic Lakatos discovery engine.

Extracted from the card domain per FRAMEWORK.md. Nothing in this package may
import from a domain (deck_sim, generator schemas, the card recognizers/proofs).
Domains depend on core, never the reverse.

Step 1 of the split (this commit): the two already-dependency-free modules.
  core.schedule  — refuter attack-schedule derivation  (was refuter_auto.py)
  core.fitter    — exact fits + model trees over an injected FeatureBasis
                   (the domain-agnostic heart of the former)
"""
