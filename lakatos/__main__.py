"""python3 -m lakatos [module ...] — run the package's ledgers.

With no arguments: import every ledger module (each runs its unit checks at
import) and print one line per module; exit non-zero on the first failure.
The proof kernel is SKIPPED, not failed, when sympy is absent — the engine
runs without it and the ladder honestly tops out at ROBUST_CONJECTURE.

With module names: run each named module's own `__main__` ledger (checks +
demo), e.g. `python3 -m lakatos refuter schedule`.
"""
import importlib
import runpy
import sys
import time

from lakatos import LEDGER_MODULES


def run_all():
    ok = True
    for name in LEDGER_MODULES:
        t0 = time.monotonic()
        try:
            importlib.import_module(f'lakatos.{name}')
            status = 'PASS'
        except ImportError as e:
            if name == 'proof_kernel' and 'sympy' in str(e):
                status = 'SKIP (sympy not installed: pip install lakatos[proof])'
            else:
                status, ok = f'FAIL {e!r}', False
        except AssertionError as e:
            status, ok = f'FAIL {e!r}', False
        print(f'  lakatos.{name:<13} {status}  ({time.monotonic() - t0:.2f}s)')
    print(f'LAKATOS LEDGERS {"PASS" if ok else "FAIL"} '
          f'({len(LEDGER_MODULES)} modules; unit checks run at import)')
    return ok


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            runpy.run_module(f'lakatos.{name}', run_name='__main__')
    else:
        sys.exit(0 if run_all() else 1)
