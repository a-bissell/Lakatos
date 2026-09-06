#!/usr/bin/env python3
"""check_all.py — the whole green bar in one command.

    python3 check_all.py            fast tier: every ledger that runs in
                                    seconds (engine, former, generator, the
                                    audits, the invariant-search ledger, the
                                    lakatos package, the cards wiring, the
                                    harness, all 26 tricks)
    python3 check_all.py --slow     + the slow tier: whole-library battery
                                    (~2 min) and the three proof scripts
    python3 check_all.py --only t2  run the checks whose name matches
    python3 check_all.py -j 1       run sequentially (default: parallel)

A check passes only if its process exits 0 AND its output carries the
script's own PASS verdict (each script prints one; the runner never infers
success from silence or from an exit code alone) AND no forbidden marker
appears. Frontier probes in t19-t22 print 'law FAIL' for configurations
BELOW the sufficient condition by design; those scripts print an overall
VERIFIED/REFUTED verdict, and the runner keys on that instead.

The lakatos ledger runs with RuntimeWarning promoted to an error, so a
regression of the runpy "found in sys.modules" warning fails the bar.

Exit status: 0 iff every selected check passed. Failing checks have the
tail of their output printed.
"""
import argparse
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
TRICKS = os.path.join(ROOT, 'tricks')
PY = sys.executable


def C(name, argv, must, cwd=ROOT, forbid=None, slow=False):
    return dict(name=name, argv=argv, must=must, cwd=cwd,
                forbid=forbid, slow=slow)


CHECKS = [
    C('lakatos package ledgers',
      [PY, '-W', 'error::RuntimeWarning', '-m', 'lakatos'],
      r'LAKATOS LEDGERS PASS'),
    C('lakatos module ledgers (dotted -m form, warning-free)',
      [PY, '-W', 'error::RuntimeWarning', '-m', 'lakatos.oracle'],
      r'unit checks: PASS'),
    C('domains/cards wiring', [PY, '-m', 'domains.cards'], r'wiring: PASS'),
    C('deck_sim harness', [PY, 'deck_sim.py'], r'-> PASS'),
    C('engine dry run (12 acceptance rows)', [PY, 'engine.py'],
      r'ENGINE DRY-RUN PASS'),
    C('former acceptance (no-hints, ladder, cross-cert)',
      [PY, 'former_acceptance.py'], r'ACCEPTANCE PASS'),
    C('generator v1 metric', [PY, 'generator.py'], r'GENERATOR v1 PASS'),
    C('invariant search acceptance (theorem #2 blind)',
      [PY, 'invariants_acceptance.py'], r'INVARIANT SEARCH ACCEPTANCE PASS'),
    C('oracle audit', [PY, 'oracle_audit.py'], r'FIXED-VECTOR ACAAN.*PASS'),
    C('library-known audit', [PY, 'library_known_audit.py'],
      r'ACCEPTANCE PASS'),
    C('provenance audit', [PY, 'provenance_audit.py'],
      r'PROVENANCE AUDIT PASS'),
    # slow tier
    C('refuter battery (whole library)', [PY, 'refuter_battery.py'],
      r'BATTERY PASS', slow=True),
    C('proof #1 general-b law (C1-C10)', [PY, 'proof.py'],
      r'PROOF CHECKS PASS', slow=True),
    C('proof #2 conservation (D1-D8)', [PY, 'proof_conservation.py'],
      r'CONSERVATION PROOF CHECKS PASS', slow=True),
    C('proof #3 largest-first (E1-E8)', [PY, 'proof_rr.py'],
      r'REVERSED-REST PROOF CHECKS PASS', slow=True),
]

# every trick prints its own PASS; the frontier probes key on their verdict
_TRICK_MUST = {
    't19': r'VERIFIED across all in-condition configs',
    't20': r'UNIVERSAL LAW VERIFIED',
    't21': r'FOUR-PILE LAW VERIFIED',
    't22': r'GENERAL-b LAW VERIFIED',
}
_TRICK_FORBID = {k: r'REFUTED' for k in _TRICK_MUST}


def _trick_key(fn):
    return fn.split('_')[0]


_TRICK_FILES = [f for f in os.listdir(TRICKS)
                if re.match(r't\d+_.*\.py$', f)]
for fn in sorted(_TRICK_FILES, key=lambda f: int(f[1:].split('_')[0])):
    k = _trick_key(fn)
    CHECKS.append(C(f'tricks/{fn}', [PY, fn], _TRICK_MUST.get(k, r'\bPASS\b'),
                    cwd=TRICKS, forbid=_TRICK_FORBID.get(k, r'\bFAIL(ED)?\b')))


def run(check):
    t0 = time.monotonic()
    try:
        p = subprocess.run(check['argv'], cwd=check['cwd'], text=True,
                           capture_output=True, timeout=1800)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or '') + '\n[TIMEOUT]', -1
    why = None
    if rc != 0:
        why = f'exit {rc}'
    elif not re.search(check['must'], out, re.M):
        why = f'no verdict matching /{check["must"]}/'
    elif check['forbid'] and re.search(check['forbid'], out, re.M):
        why = f'forbidden marker /{check["forbid"]}/'
    return dict(check, ok=why is None, why=why, out=out,
                secs=time.monotonic() - t0)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--slow', action='store_true',
                    help='include the battery and the proof scripts')
    ap.add_argument('--only', metavar='PATTERN',
                    help='run only checks whose name matches (regex)')
    ap.add_argument('-j', '--jobs', type=int, default=min(4, os.cpu_count() or 1),
                    help='parallel workers (default %(default)s)')
    args = ap.parse_args()

    sel = [c for c in CHECKS if (args.slow or not c['slow'])
           and (not args.only or re.search(args.only, c['name']))]
    if not sel:
        print('no checks selected'); return 2
    print(f'check_all: {len(sel)} checks, {args.jobs} workers'
          f'{" (slow tier included)" if args.slow else ""}\n')
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        results = list(ex.map(run, sel))
    for r in results:
        tag = 'PASS' if r['ok'] else 'FAIL'
        print(f'  {tag}  {r["secs"]:6.1f}s  {r["name"]}'
              + (f'  -- {r["why"]}' if r['why'] else ''))
    failed = [r for r in results if not r['ok']]
    for r in failed:
        print(f'\n---- {r["name"]}: {r["why"]} ---- last 25 lines:')
        print('\n'.join(r['out'].rstrip().split('\n')[-25:]))
    n = len(results)
    print(f'\nCHECK ALL {"PASS" if not failed else "FAIL"} '
          f'({n - len(failed)}/{n}, {time.monotonic() - t0:.0f}s wall)')
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
