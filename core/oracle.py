"""core/oracle.py — the rediscovery-filter POLICY, domain-agnostic.

Extracted from novelty_oracle.py (engine item 2) as part of the core/domains
split (FRAMEWORK.md, step 2). The asymmetric-error POLICY lives here; the
family recognizers that define what "known" MEANS stay in the domain
(novelty_oracle.py, for cards).

The one design choice this module enforces:
  * false NOVEL (miss a rediscovery) -> recoverable downstream
  * false KNOWN (kill a real result) -> invisible & catastrophic
So recognizers ABSTAIN when unsure, an exact match earned on a merely PARTIAL
sample ABSTAINS rather than suppresses (the sampling pin), two exact matches at
once ABSTAIN as suspicious, and every suppression is LOGGED with a witness so a
false KNOWN is auditable, never silently lost.

A domain hands classify() a RecognizerSet per candidate:
  recognizers  : iterable of  cand -> hit | None
                 hit = {'family': str, 'confidence': 'exact'|'abstain',
                        'witness': str}
  checked      : list[str]   family names checked (for the NOT_MATCHED note)
  sampling_pin : bool  — if True, an exact match requires the candidate to
                 declare sample_scope == 'exhaustive', else it ABSTAINS.
                 Recognizers that enumerate their whole domain internally
                 (e.g. a property invariant) set this False.
  refine       : optional  list[hit] -> list[hit]  collapsing a more-specific
                 exact match over a more-general one (identity if None).
  note         : optional str appended to the NOT_MATCHED note (a domain
                 coverage disclosure, e.g. a declared-but-unwired family).

classify() reads only cand.name, cand.N (a scale int, for the log), and
cand.sample_scope. Everything else about a candidate is the recognizers'
business — core stays blind to it.
"""


# ---- suppressed log (audit surface for the dangerous error) ------------------

class SuppressedLog:
    def __init__(self):
        self.entries = []

    def record(self, name, family, confidence, witness, N):
        self.entries.append(dict(name=name, family=family,
                                 confidence=confidence, witness=witness, N=N))

    def review_queue(self):
        """What a human should actually look at: anything not an exact match.
        Exact permutation-signature matches sit quietly; uncertainty surfaces."""
        return [e for e in self.entries if e['confidence'] != 'exact']

    def summary(self):
        from collections import Counter
        fam = Counter(e['family'] for e in self.entries)
        return dict(total=len(self.entries), by_family=dict(fam),
                    needs_review=len(self.review_queue()))


# ---- the policy --------------------------------------------------------------

class RecognizerSet:
    """The domain's answer to 'how should this candidate be judged?' — the
    applicable recognizers plus the policy knobs classify() honors."""

    def __init__(self, recognizers, checked, sampling_pin=True, refine=None,
                 note=None):
        self.recognizers = list(recognizers)
        self.checked = list(checked)
        self.sampling_pin = sampling_pin
        self.refine = refine
        self.note = note


def classify(cand, rset, log):
    """Run the recognizers, apply the asymmetric policy, log-and-suppress.

    Sampling pin: a signature match earned on a PARTIAL sample never
    suppresses — it ABSTAINS and surfaces for review, because a branching
    procedure could look like a family on the sampled cases and diverge on the
    rest (the residual false-KNOWN vector). A RecognizerSet whose recognizers
    enumerate their whole domain internally sets sampling_pin=False."""
    hits = [r(cand) for r in rset.recognizers]
    exact = [h for h in hits if h and h['confidence'] == 'exact']
    abstains = [h for h in hits if h and h['confidence'] == 'abstain']

    if rset.refine is not None and exact:
        exact = rset.refine(exact)

    if exact and rset.sampling_pin and cand.sample_scope != 'exhaustive':
        fams = [h['family'] for h in exact]
        log.record(cand.name, '+'.join(fams), 'sampled',
                   f"signature match on PARTIAL sample "
                   f"(scope={cand.sample_scope}) — not suppressed", cand.N)
        return {'verdict': 'ABSTAIN', 'families': fams,
                'reason': f"matched {'+'.join(fams)} on a partial sample — "
                          f"pin to exhaustive card sampling to suppress"}
    if len(exact) == 1:
        h = exact[0]
        witness = h['witness'] + f" [sample scope: {cand.sample_scope}]"
        log.record(cand.name, h['family'], 'exact', witness, cand.N)
        return {'verdict': 'MATCHED', 'family': h['family'],
                'confidence': 'exact', 'witness': witness}
    if len(exact) > 1:                        # two families at once = suspicious
        log.record(cand.name, '+'.join(h['family'] for h in exact),
                   'ambiguous', 'multiple exact matches', cand.N)
        return {'verdict': 'ABSTAIN', 'reason': 'multiple family matches',
                'families': [h['family'] for h in exact]}
    if abstains:
        log.record(cand.name, abstains[0]['family'], 'abstain',
                   abstains[0]['witness'], cand.N)
        return {'verdict': 'ABSTAIN', 'reason': abstains[0]['witness']}
    note = (f"not one of the checked families ({', '.join(rset.checked)}) "
            f"— routed onward, NOT certified novel")
    if rset.note:
        note += f"; {rset.note}"
    return {'verdict': 'NOT_MATCHED', 'families_checked': rset.checked,
            'note': note}
