"""Task 25 (ENGINE item 3 proof): the conjecture former re-derives the
general-b targeting law from raw round maps — no hints — and its
model-planned pickup vectors pass verify() on the simulator.

The full acceptance ledger (no-hints guard, refuter ladder, negative
control, t22 cross-certification) lives in former_acceptance.py at the
repo root. This script is the tricks/-convention runnable proof: fit the
closed form from the black-box round maps, plan every target's pickup
vector from the MODEL alone, and let verify() judge over the entire
(card x target) domain.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..'))
from former import fit_round_model
from former_acceptance import (FIT_GRID, GROUND_TRUTH_GRID, gergonne_query,
                               run_ground_truth)


if __name__ == '__main__':
    model = fit_round_model(gergonne_query, FIT_GRID)
    assert model is not None, 'former refused the Gergonne round maps'
    print('machine-fitted closed form (no hints):')
    print('  ' + model.describe().replace('\n', '\n  '))

    total, all_ok = 0, True
    for N, b, r in GROUND_TRUTH_GRID:
        (ok, counter), cases = run_ground_truth(model, N, b, r)
        total += cases
        all_ok &= ok
        print(f'  N={N} b={b} r={r}: {"PASS" if ok else "FAIL"} '
              f'over {cases} cases'
              + ('' if ok else f'  e.g. {counter[:2]}'))
    print(f't25 {"PASS" if all_ok else "FAIL"}: model-planned targeting, '
          f'{total} verified cases')
