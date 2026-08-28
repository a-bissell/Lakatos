"""provenance_audit.py — novelty claims must carry search logs (item 7).

LIBRARY.md is allowed to say "likely new" the way it is allowed to say
"verified": only against a recorded artifact. verify() counts are that
artifact for correctness; PROVENANCE.md records (dated queries, sources,
a controlled verdict) are that artifact for novelty. This audit is the
mechanical link:

  * every LIBRARY entry whose text claims novelty (markers below) must
    be covered by at least one PROVENANCE record;
  * every record must point at entries that exist, carry a date, at
    least one logged query, at least one source with a URL, and a
    verdict from the controlled vocabulary;
  * a KNOWN verdict additionally requires the library entry itself to
    acknowledge the literature (a rediscovery may not read as a
    discovery);
  * the stale tag "provenance search pending" may not remain anywhere
    in LIBRARY.md.

The audit never judges the verdicts — a NOT-FOUND is a statement about
the logged queries, not about the literature. What it enforces is that
the log EXISTS and the entry text is consistent with it.
"""
import re

# an entry claiming novelty is recognizable by one of these
NOVELTY_MARKERS = (
    'NOVEL COMMIT', 'novelty candidate', 'not found published',
    'No trace', 'no literature trace', 'likely new',
    'provenance search pending',
)

VERDICTS = ('KNOWN', 'KNOWN-FAMILY', 'NOT-FOUND')

# a KNOWN entry must acknowledge the literature in its own text
ACK_WORDS = ('rediscover', 'literature', 'classical')

STALE_TAG = 'provenance search pending'


def parse_entries(md_text):
    """{entry_name: body_text} for every '### name' block. A body ends
    at the next heading OR at a horizontal rule / '##' section — else
    the last entry would swallow the session log and inherit its
    markers."""
    out = {}
    parts = re.split(r'^### +(.+?) *$', md_text, flags=re.M)
    for i in range(1, len(parts) - 1, 2):
        body = re.split(r'^---\s*$|^## ', parts[i + 1], flags=re.M)[0]
        out[parts[i].strip()] = body
    return out


def flagged_entries(library_text):
    return sorted(name for name, body in parse_entries(library_text).items()
                  if any(m in body for m in NOVELTY_MARKERS))


def parse_records(prov_text):
    """[{name, entries, date, verdict, n_queries, n_sources}] per record."""
    recs = []
    for name, body in parse_entries(prov_text).items():
        rec = dict(name=name, entries=[], date=None, verdict=None,
                   n_queries=0, n_sources=0)
        section = None
        for line in body.splitlines():
            m = re.match(r'^(entries|claim|date|verdict|queries|sources|'
                         r'consequence):\s*(.*)$', line)
            if m:
                section = m.group(1)
                val = m.group(2).strip()
                if section == 'entries':
                    rec['entries'] = [e.strip() for e in val.split(',')
                                      if e.strip()]
                elif section == 'date':
                    rec['date'] = val
                elif section == 'verdict':
                    rec['verdict'] = val
                continue
            if re.match(r'^\s+- ', line):
                if section == 'queries':
                    rec['n_queries'] += 1
                elif section == 'sources' and 'http' in line:
                    rec['n_sources'] += 1
        recs.append(rec)
    return recs


def audit(library_text, prov_text):
    """Returns (ok, problems, stats). problems is a list of strings —
    empty means the provenance ledger is complete and well-formed."""
    problems = []
    lib = parse_entries(library_text)
    flagged = flagged_entries(library_text)
    recs = parse_records(prov_text)

    if STALE_TAG in library_text:
        problems.append(f'LIBRARY.md still contains the stale tag '
                        f'"{STALE_TAG}" — the log exists now; point at it')

    covered = set()
    for r in recs:
        covered.update(r['entries'])
        where = f"record '{r['name']}'"
        if not r['entries']:
            problems.append(f'{where}: no entries listed')
        for e in r['entries']:
            if e not in lib:
                problems.append(f'{where}: entry "{e}" not in LIBRARY.md')
        if not (r['date'] and re.fullmatch(r'\d{4}-\d{2}-\d{2}', r['date'])):
            problems.append(f'{where}: missing/malformed date')
        if r['verdict'] not in VERDICTS:
            problems.append(f'{where}: verdict {r["verdict"]!r} not in '
                            f'{VERDICTS}')
        if r['n_queries'] < 1:
            problems.append(f'{where}: no queries logged')
        if r['n_sources'] < 1:
            problems.append(f'{where}: no sources with URLs logged')
        if r['verdict'] == 'KNOWN':
            for e in r['entries']:
                body = lib.get(e, '').lower()
                if e in lib and not any(w in body for w in ACK_WORDS):
                    problems.append(
                        f'{where}: verdict KNOWN but entry "{e}" does not '
                        f'acknowledge the literature '
                        f'(needs one of {ACK_WORDS})')

    for e in flagged:
        if e not in covered:
            problems.append(f'flagged entry "{e}" (claims novelty) has no '
                            f'PROVENANCE record')

    stats = dict(entries=len(lib), flagged=len(flagged), records=len(recs),
                 covered=len(covered & set(lib)),
                 queries=sum(r['n_queries'] for r in recs),
                 sources=sum(r['n_sources'] for r in recs))
    return (not problems), problems, stats


# ---- unit checks (run at import, per project convention) ---------------------

_LIB_OK = """
### plain-entry
notes: nothing claimed.

### bold-entry
canonical note: NOVEL COMMIT (test).

### humble-entry
notes: rediscovery of a classical result, literature cited. NOVEL COMMIT.

### tail-entry
notes: last entry, claims nothing.

---

## Session log
- NOVEL COMMIT and likely new appear here; the log must not flag
  tail-entry by adjacency.
"""

_PROV_OK = """
### rec-a
entries: bold-entry
date: 2026-08-28
verdict: NOT-FOUND
queries:
  - "a query"
sources:
  - A Title — https://example.org — what it shows
### rec-b
entries: humble-entry
date: 2026-08-28
verdict: KNOWN
queries:
  - "another query"
sources:
  - B Title — https://example.org/b — what it shows
"""


def _unit_pass():
    ok, problems, stats = audit(_LIB_OK, _PROV_OK)
    assert ok, problems
    assert stats['flagged'] == 2 and stats['records'] == 2
    assert stats['queries'] == 2 and stats['sources'] == 2
    # the session log's markers must not leak into the last entry's body
    assert 'tail-entry' not in flagged_entries(_LIB_OK)


def _unit_failures_detected():
    # 1: flagged entry with no record
    ok, probs, _ = audit(_LIB_OK, _PROV_OK.split('### rec-b')[0])
    assert not ok and any('humble-entry' in p and 'no PROVENANCE' in p
                          for p in probs)
    # 2: record pointing at a nonexistent entry
    ok, probs, _ = audit(_LIB_OK, _PROV_OK.replace(
        'entries: bold-entry', 'entries: ghost-entry'))
    assert not ok and any('ghost-entry' in p for p in probs)
    # 3: verdict outside the vocabulary
    ok, probs, _ = audit(_LIB_OK, _PROV_OK.replace('NOT-FOUND', 'MAYBE'))
    assert not ok and any('MAYBE' in p for p in probs)
    # 4: missing sources
    ok, probs, _ = audit(_LIB_OK, _PROV_OK.replace(
        'https://example.org —', 'no url —'))
    assert not ok and any('rec-a' in p and 'sources' in p for p in probs)
    # 5: KNOWN without acknowledgment in the entry text
    lib = _LIB_OK.replace('rediscovery of a classical result, literature '
                          'cited. ', '')
    ok, probs, _ = audit(lib, _PROV_OK)
    assert not ok and any('acknowledge' in p for p in probs)
    # 6: stale pending tag
    ok, probs, _ = audit(_LIB_OK + '\nprovenance search pending\n', _PROV_OK)
    assert not ok and any('stale' in p for p in probs)
    # 7: malformed date
    ok, probs, _ = audit(_LIB_OK, _PROV_OK.replace('2026-08-28', 'soon', 1))
    assert not ok and any('date' in p for p in probs)


_unit_pass()
_unit_failures_detected()


if __name__ == '__main__':
    print('provenance_audit.py unit checks: PASS (coverage, ghost entries, '
          'verdict vocabulary, sources, KNOWN acknowledgment, stale tag, '
          'dates)')
    with open('LIBRARY.md') as f:
        lib = f.read()
    with open('PROVENANCE.md') as f:
        prov = f.read()
    ok, problems, stats = audit(lib, prov)
    print(f"\nlibrary entries: {stats['entries']}, flagged as claiming "
          f"novelty: {stats['flagged']}, provenance records: "
          f"{stats['records']} (covering {stats['covered']} entries, "
          f"{stats['queries']} logged queries, {stats['sources']} sources)")
    for p in problems:
        print(f'  PROBLEM: {p}')
    print(f"\nPROVENANCE AUDIT {'PASS' if ok else 'FAIL'}")
    raise SystemExit(0 if ok else 1)
