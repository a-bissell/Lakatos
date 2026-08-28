"""refuter_auto.py — attack schedules derived from parameter signatures
(engine item 4). No curated lists.

The known limit recorded in README.md: "a curated adversary launders the
author's blind spots into a false robust stamp." This module removes the
author from the loop. A conjecture declares its parameter SIGNATURE —
axes with domain floors and escalation styles, a validity predicate, a
cost model with a cap — and the schedule is DERIVED:

  * floor probes     each axis pushed DOWN to the smallest valid value
                     (bisected against validity, since axes couple), plus
                     the all-floors corner when valid;
  * escalation       each axis pushed BEYOND its inspiring maximum —
                     doubling for 'linear' axes, +1 steps for 'increment'
                     axes (exponents). Walks run from SEVERAL anchors
                     (the costliest inspiring point AND each floor
                     probe), because a cheap corner affords a deep walk
                     that the expensive corner cannot (e.g. r escalates
                     far at the b floor). When a step overshoots
                     validity or the cost cap, the axis is bisected back
                     to the LARGEST valid value still beyond inspiring;
                     when a walk completes clean, one extra bisection
                     pushes to the envelope edge. No stopping short
                     silently;
  * joint escalation one step on every axis simultaneously, if valid;
  * random draws     deterministic LCG draws over [floor, 2x escalated
                     max] per axis, validity- and cost-filtered.

No silent caps: derive_schedule also returns a per-axis report saying
whether the axis was escalated beyond inspiring, and if not, WHY
(validity-limited or cost-limited). A battery that cannot attack an axis
must say so out loud.
"""
from dataclasses import dataclass


@dataclass
class Axis:
    name: str
    lo: int               # smallest value in the parameter's domain
    step: str = 'linear'  # 'linear' (escalate by doubling) | 'increment' (+1)


def _ok(params, valid, cost, cap):
    if valid is not None and not valid(*params):
        return False
    if cost is not None and cap is not None and cost(*params) > cap:
        return False
    return True


def _with(params, i, v):
    q = list(params)
    q[i] = v
    return tuple(q)


def _bisect_max(params, i, lo_v, hi_v, valid, cost, cap):
    """Largest v in [lo_v, hi_v] making axis i valid+affordable, else None.
    Assumes feasibility is downward-closed above lo_v on this axis (true
    for cost-monotone axes; a non-monotone validity just yields a sound,
    possibly conservative probe)."""
    best = None
    while lo_v <= hi_v:
        mid = (lo_v + hi_v) // 2
        if _ok(_with(params, i, mid), valid, cost, cap):
            best = mid
            lo_v = mid + 1
        else:
            hi_v = mid - 1
    return best


def _bisect_min(params, i, lo_v, hi_v, valid, cost, cap):
    """Smallest v in [lo_v, hi_v] making axis i valid+affordable, else None."""
    best = None
    while lo_v <= hi_v:
        mid = (lo_v + hi_v) // 2
        if _ok(_with(params, i, mid), valid, cost, cap):
            best = mid
            hi_v = mid - 1
        else:
            lo_v = mid + 1
    return best


def derive_schedule(axes, inspiring, valid=None, cost=None, cap=None,
                    seed=20260828, n_random=4):
    """Returns (schedule, axis_report).
    schedule: {'boundary': [...], 'beyond': [...], 'random_draw': [...]}
    axis_report: {axis_name: 'escalated to V' | 'validity-limited at MX'
                  | 'cost-limited at MX'} — the no-silent-caps ledger."""
    k = len(axes)
    assert inspiring and all(len(p) == k for p in inspiring)
    mx = [max(p[i] for p in inspiring) for i in range(k)]
    seen = set(map(tuple, inspiring))
    # reference point: costliest inspiring param (ties -> lexicographic max)
    ref = max(inspiring, key=lambda p: ((cost(*p) if cost else 0), p))

    def add(bucket, p):
        if p is not None and p not in seen and _ok(p, valid, cost, cap):
            bucket.append(p)
            seen.add(p)

    boundary, beyond, report = [], [], {}

    # floor probes (bisected: axes couple through validity)
    for i, ax in enumerate(axes):
        v = _bisect_min(ref, i, ax.lo, ref[i], valid, cost, cap)
        if v is not None:
            add(boundary, _with(ref, i, v))
    corner = tuple(ax.lo for ax in axes)
    add(boundary, corner)

    # per-axis escalation beyond the inspiring maximum, walked from every
    # anchor: the costliest inspiring point and each floor probe (a cheap
    # corner affords a deep walk the expensive corner cannot)
    anchors = [ref] + [p for p in boundary]
    esc_hi = list(mx)
    for i, ax in enumerate(axes):
        got = None
        for anchor in anchors:
            v = max(mx[i], anchor[i])
            limit = 4 if ax.step == 'linear' else 8
            clean = True
            for _ in range(limit):
                nv = 2 * v if ax.step == 'linear' else v + 1
                p = _with(anchor, i, nv)
                if _ok(p, valid, cost, cap):
                    add(beyond, p)
                    v = nv
                    got = max(got or 0, nv)
                else:
                    clean = False
                    e = _bisect_max(anchor, i, v + 1, nv, valid, cost, cap)
                    if e is not None and e > mx[i]:
                        add(beyond, _with(anchor, i, e))
                        got = max(got or 0, e)
                    break
            if clean and v > max(mx[i], anchor[i]):
                e = _bisect_max(anchor, i, v + 1, 8 * v, valid, cost, cap)
                if e is not None:
                    add(beyond, _with(anchor, i, e))
                    got = max(got or 0, e)
        if got:
            esc_hi[i] = got
            report[ax.name] = f'escalated to {got}'
        else:
            probe = _with(ref, i, mx[i] + 1)
            why = ('validity-limited' if valid is not None
                   and not valid(*probe) else 'cost-limited')
            report[ax.name] = f'{why} at {mx[i]}'

    # joint escalation: one step on every axis at once
    joint = tuple(2 * mx[i] if axes[i].step == 'linear' else mx[i] + 1
                  for i in range(k))
    add(beyond, joint)

    # deterministic draws over [floor, 2x escalated max]
    s, draws, tries = seed, [], 0
    while len(draws) < n_random and tries < 60 * n_random:
        tries += 1
        p = []
        for i, ax in enumerate(axes):
            s = (1103515245 * s + 12345) % (1 << 31)
            span = max(2 * esc_hi[i] - ax.lo, 1)
            p.append(ax.lo + s % span)
        p = tuple(p)
        if p not in seen and _ok(p, valid, cost, cap):
            draws.append(p)
            seen.add(p)

    return ({'boundary': boundary, 'beyond': beyond, 'random_draw': draws},
            report)


def auto_conjecture(name, claim, instance_test, axes, inspiring,
                    valid=None, cost=None, cap=None, scale=None,
                    seed=20260828):
    """Build a refuter.Conjecture whose entire battery is derived from the
    signature. Returns (conjecture, axis_report)."""
    from refuter import Conjecture
    sched, report = derive_schedule(axes, inspiring, valid, cost, cap, seed)
    conj = Conjecture(
        name=name, claim=claim, instance_test=instance_test,
        scale=scale or (lambda *p: (cost(*p) if cost else max(p))),
        inspiring=list(map(tuple, inspiring)),
        boundary=sched['boundary'], beyond=sched['beyond'],
        random_draw=sched['random_draw'],
        param_names=tuple(ax.name for ax in axes))
    return conj, report


# ---- unit checks (run at import, per project convention) ---------------------

def _unit_schedule():
    axes = [Axis('N', lo=2, step='linear'), Axis('r', lo=1, step='increment')]
    valid = lambda N, r: N >= 2 and 1 <= r and N >= r
    cost = lambda N, r: N * N * r
    sched, report = derive_schedule(axes, [(10, 3), (16, 3)],
                                    valid, cost, cap=100000)
    allp = sched['boundary'] + sched['beyond'] + sched['random_draw']
    # every emitted param is valid, affordable, and not an inspiring dup
    assert allp and all(valid(*p) and cost(*p) <= 100000 for p in allp)
    assert not ({(10, 3), (16, 3)} & set(allp))
    # monotone escalation happened on BOTH axes and the report says so
    assert any(p[0] > 16 for p in sched['beyond'])
    assert any(p[1] > 3 for p in sched['beyond'])
    assert all(v.startswith('escalated') for v in report.values())
    # floors probed
    assert any(p[0] <= 3 for p in allp) and any(p[1] == 1 for p in allp)
    # deterministic
    sched2, _ = derive_schedule(axes, [(10, 3), (16, 3)],
                                valid, cost, cap=100000)
    assert sched == sched2


def _unit_limits_reported():
    axes = [Axis('N', lo=2), Axis('r', lo=1, step='increment')]
    # r is validity-capped at 3; N is cost-capped tightly
    valid = lambda N, r: r <= 3 and N >= 2
    cost = lambda N, r: N
    sched, report = derive_schedule(axes, [(16, 3)], valid, cost, cap=16)
    assert report['r'].startswith('validity-limited')
    assert report['N'].startswith('cost-limited')
    assert all(p[1] <= 3 and p[0] <= 16
               for p in sched['boundary'] + sched['beyond']
               + sched['random_draw'])
    # bisected escalation reaches the envelope edge, not just x2 checks
    sched3, rep3 = derive_schedule(axes, [(16, 3)], valid,
                                   cost=lambda N, r: N, cap=25)
    assert (25, 3) in sched3['beyond'], sched3['beyond']
    assert rep3['N'] == 'escalated to 25'


_unit_schedule()
_unit_limits_reported()


if __name__ == '__main__':
    print('refuter_auto.py unit checks: PASS (escalation on every axis, '
          'floor probes, envelope-edge bisection, limit reporting, '
          'determinism)')
    axes = [Axis('b', lo=2), Axis('N', lo=2), Axis('r', lo=1,
                                                   step='increment')]
    sched, report = derive_schedule(
        axes, [(6, 52, 3), (8, 52, 3)],
        valid=lambda b, N, r: N >= b and b ** (r - 1) >= N,
        cost=lambda b, N, r: N * N * r, cap=200000)
    print('demo — schedule for the general-b signature:')
    for tag in ('boundary', 'beyond', 'random_draw'):
        print(f'  {tag}: {sched[tag]}')
    print(f'  axis report: {report}')
