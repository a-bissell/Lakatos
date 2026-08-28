"""proof_rr.py — machine checks E1-E8 for PROOF_reversed_rest.md
(theorem #3: the largest-first ACAAN law).

Spine: Lemma R (reflection conjugacy) — the largest-first round map at
rank c IS the position-reflection conjugate of the Gergonne round map
at the complementary rank a = b-1-c:

    rr_c(x)  =  N-1 - gp_{b-1-c}(N-1-x).

Theorem #3 then inherits theorem #1 (PROOF.md) wholesale: a Gergonne
vector for the mirror target, complemented, is a largest-first vector
for the original target, and the law's own argmin recursion is the
mirrored argmin (theorem #1 holds for ANY minimizer). The kernel is
shared with proof.py; the standalone midpoint recursion (E5) is
checked as well, so the law also stands on its own feet.

Case variables follow a := b-1-c throughout — in that coordinate the
largest-first case structure lines up with the Gergonne one.
"""
import importlib.util

import sympy as sp

from proof import Ctx, zero, b, q0, rho, N, a, j, t, t1, t2, z
from deck_sim import (make_deck, make_packet, deal_into_piles,
                      gather_order, gather_position, verify)

I, F, y = sp.symbols('I F y')
c_ = b - 1 - a                      # the rank, in a-coordinates

GRID = [(bb, NN) for bb in range(2, 8)
        for NN in (bb, bb + 1, 2 * bb - 1, 3 * bb + 2)]


def corr_gp_int(aa, bb, r_):
    return min(aa, r_) * (bb - max(aa + 1, r_))


def C_rr_int(jj, cc, bb, q_, r_):
    """Lemma A closed form (integer): largest-first, pile j at rank c."""
    aa = bb - 1 - cc
    if jj <= aa:
        return (cc + 1) * q_ + max(0, r_ - aa - 1) + \
            (1 if jj < r_ else 0) - 1
    return (cc + 1) * q_ + max(0, r_ - aa) - 1


def rr_map(NN, bb, cc):
    """Simulator round map: pointed pile at rank c, others largest-
    index-first."""
    markers = list(range(NN))
    pos = [None] * NN
    for jj in range(bb):
        others = [k for k in range(bb - 1, -1, -1) if k != jj]
        d = gather_order(deal_into_piles(markers, bb),
                         others[:cc] + [jj] + others[cc:])
        for newp, x in enumerate(d):
            if x % bb == jj:
                pos[x] = newp
    return pos


def gp_map(NN, bb, aa):
    markers = list(range(NN))
    pos = [None] * NN
    for jj in range(bb):
        d = gather_position(deal_into_piles(markers, bb), jj, aa)
        for newp, x in enumerate(d):
            if x % bb == jj:
                pos[x] = newp
    return pos


# --------------------------------------------------------------------- E2 ----
# C_rr derivation: A_rr(j,c) = the c largest indices != j.
#   j <= a: A_rr = [a+1, b-1]        -> count = max(0, rho-a-1)
#   j >  a: A_rr = [a, b-1] \ {j}    -> count = max(0, rho-a) - [j<rho]
# (indicator written as the free symbol I where it cancels)

def check_E2():
    # j <= a, sub-case a < rho: count = rho-a-1 (nonempty by ar fact)
    ctx = Ctx(ar=rho - a - 1, a0=a, ab=b - 1 - a)
    ctx.nonneg(rho - a - 1, lam=[('ar', 1)], what='E2 count >= 0')
    zero((c_ * q0 + (rho - a - 1) + (q0 + I) - 1)
         - ((c_ + 1) * q0 + (rho - a - 1) + I - 1), 'E2 j<=a, a<rho')
    # j <= a, a >= rho: count = 0
    zero((c_ * q0 + 0 + (q0 + I) - 1) - ((c_ + 1) * q0 + I - 1),
         'E2 j<=a, a>=rho')
    # j > a, a < rho: count = (rho-a) - I; sizes[j] adds I back — cancels
    zero((c_ * q0 + ((rho - a) - I) + (q0 + I) - 1)
         - ((c_ + 1) * q0 + (rho - a) - 1), 'E2 j>a, a<rho')
    # j > a, a >= rho: count = 0 - I ... the pile-j indicator: j > a >= rho
    # forces j >= rho so I = 0 on both sides
    zero((c_ * q0 + 0 + (q0 + 0) - 1) - ((c_ + 1) * q0 - 1),
         'E2 j>a, a>=rho')


# --------------------------------------------------------------------- E1 ----

def check_E1():
    """Closed form == simulator on the grid, every (j, c)."""
    for bb, NN in GRID:
        q_, r_ = divmod(NN, bb)
        for cc in range(bb):
            pos = rr_map(NN, bb, cc)
            for x in range(NN):
                jj = x % bb
                assert pos[x] == C_rr_int(jj, cc, bb, q_, r_) - x // bb, \
                    (bb, NN, cc, x)


# --------------------------------------------------------------------- E4 ----

def check_E4():
    """Reflection algebra: the card at x = b*y + j reflects to
    N-1-x, whose pile is j' = (rho-1-j) mod b and whose deal index is
    sizes[j]-1-y. Division identities with certified ranges."""
    # case j < rho: N-1-j = b*q0 + (rho-1-j), remainder in [0, b)
    ctx = Ctx(jr=rho - 1 - j, j0=j, rho_hi=b - 1 - rho)
    zero((N - 1 - j) - (b * q0 + (rho - 1 - j)), 'E4 j<rho quotient')
    ctx.nonneg(rho - 1 - j, lam=[('jr', 1)], what='E4 rem >= 0')
    ctx.nonneg((b - 1) - (rho - 1 - j), lam=[('rho_hi', 1), ('j0', 1)],
               const=1, what='E4 rem < b')
    # case j >= rho: N-1-j = b*(q0-1) + (b+rho-1-j), remainder in [0, b)
    ctx = Ctx(jge=j - rho, jb=b - 1 - j, rho0=rho)
    zero((N - 1 - j) - (b * (q0 - 1) + (b + rho - 1 - j)),
         'E4 j>=rho quotient')
    ctx.nonneg(b + rho - 1 - j, lam=[('jb', 1), ('rho0', 1)],
               what='E4 rem >= 0')
    ctx.nonneg((b - 1) - (b + rho - 1 - j), lam=[('jge', 1)],
               what='E4 rem < b')
    # depth reflection: N-1-(b*y+j) = b*(sizes[j]-1-y) + s, same s
    zero((N - 1 - (b * y + j)) - (b * ((q0 + 1) - 1 - y) + (rho - 1 - j)),
         'E4 depth, j<rho')
    zero((N - 1 - (b * y + j)) - (b * (q0 - 1 - y) + (b + rho - 1 - j)),
         'E4 depth, j>=rho')
    # simulator tie: full map conjugacy rr_c == reflect . gp_{b-1-c} . reflect
    for bb, NN in GRID:
        for cc in range(bb):
            rr = rr_map(NN, bb, cc)
            gp = gp_map(NN, bb, bb - 1 - cc)
            assert rr == [NN - 1 - gp[NN - 1 - x] for x in range(NN)], \
                (bb, NN, cc)


# --------------------------------------------------------------------- E3 ----
# Lemma R's algebraic core:  C_rr(j, c) + C_gp(j', b-1-c) =
# N - 2 + sizes[j],  j' = (rho-1-j) mod b.

def _gp_C(jp, mn, ind):
    """C_gp with its min/indicator resolved for the cell: j' <= a form
    uses mn = min(a+1, rho); j' > a form uses mn = min(a, rho) + ind."""
    return (a + 1) * q0 + mn + ind - 1


def check_E3():
    target_lo = (b + 1) * q0 + rho - 1      # sizes[j] = q0+1 (j < rho)
    target_hi = (b + 1) * q0 + rho - 2      # sizes[j] = q0   (j >= rho)
    # Cell A: a < rho, j < rho  (C_rr the same whether j <= a or j > a);
    # j' = rho-1-j, [j' < rho] = 1 (j >= 0)
    Crr = (c_ + 1) * q0 + rho - a - 1
    ctx = Ctx(ar=rho - a - 1, j0=j, jr=rho - 1 - j)
    ctx.nonneg(rho - 1 - (rho - 1 - j), lam=[('j0', 1)],
               what="E3 A [j'<rho]=1")
    #   A-sub1: j' > a  (j <= rho-a-2): C_gp = (a+1)q0 + a + 1 - 1
    Ctx(sub=rho - a - 2 - j, ar=rho - a - 1).nonneg(
        (rho - 1 - j) - (a + 1), lam=[('sub', 1)], what='E3 A1 case')
    zero(Crr + _gp_C(None, a, 1) - target_lo, 'E3 cell A1')
    #   A-sub2: j' <= a: C_gp = (a+1)q0 + (a+1) - 1  [min(a+1,rho)=a+1]
    Ctx(ar=rho - a - 1).nonneg(rho - (a + 1), lam=[('ar', 1)],
                               what='E3 A2 min(a+1,rho)=a+1')
    zero(Crr + _gp_C(None, a + 1, 0) - target_lo, 'E3 cell A2')
    # Cell B: a < rho, j >= rho  (forces j > a); j' = b+rho-1-j,
    # j' >= rho > a and [j' < rho] = 0
    Crr = (c_ + 1) * q0 + (rho - a) - 1
    ctx = Ctx(ar=rho - a - 1, jge=j - rho, jb=b - 1 - j)
    ctx.nonneg((b + rho - 1 - j) - rho, lam=[('jb', 1)],
               what="E3 B [j'>=rho]")
    ctx.nonneg((b + rho - 1 - j) - (a + 1), lam=[('jb', 1), ('ar', 1)],
               what="E3 B j'>a")
    zero(Crr + _gp_C(None, a, 0) - target_hi, 'E3 cell B')
    # Cell C: a >= rho, j < rho  (forces j <= a); j' = rho-1-j <= a
    Crr = (c_ + 1) * q0 + 0 + 1 - 1
    ctx = Ctx(ra=a - rho, jr=rho - 1 - j, j0=j)
    ctx.nonneg(a - (rho - 1 - j), lam=[('ra', 1), ('j0', 1)], const=1,
               what="E3 C j'<=a")
    ctx.nonneg((a + 1) - rho, lam=[('ra', 1)], const=1,
               what='E3 C min(a+1,rho)=rho')
    zero(Crr + _gp_C(None, rho, 0) - target_lo, 'E3 cell C')
    # Cells D (j <= a) and E (j > a): a >= rho, j >= rho; j' = b+rho-1-j,
    # [j' < rho] = 0; C_gp = (a+1)q0 + rho - 1 in BOTH j'-subcases:
    #   j' <= a:  min(a+1, rho) = rho
    #   j' >  a:  min(a, rho) + 0 = rho
    for name, Crr, facts in (
            ('D', (c_ + 1) * q0 + 0 + 0 - 1,
             dict(ra=a - rho, jge=j - rho, aj=a - j, ab=b - 1 - a)),
            ('E', (c_ + 1) * q0 + 0 - 1,
             dict(ra=a - rho, ja=j - a - 1, jb=b - 1 - j))):
        ctx = Ctx(**facts)
        # [j' < rho] = 0: j' - rho = b-1-j >= 0
        if name == 'D':
            ctx.nonneg((b + rho - 1 - j) - rho,
                       lam=[('ab', 1), ('aj', 1)],
                       what="E3 D [j'>=rho]")
        else:
            ctx.nonneg((b + rho - 1 - j) - rho, lam=[('jb', 1)],
                       what="E3 E [j'>=rho]")
        ctx.nonneg((a + 1) - rho, lam=[('ra', 1)], const=1,
                   what=f'E3 {name} min(a+1,rho)=rho')
        ctx.nonneg(a - rho, lam=[('ra', 1)],
                   what=f'E3 {name} min(a,rho)=rho')
        zero(Crr + _gp_C(None, rho, 0) - target_hi, f'E3 cell {name}')


# --------------------------------------------------------------------- E5 ----
# Standalone midpoint recursion (supplementary): L_rr, tiling, width,
# and the doubled-center identity with corr_rr = -corr_gp(b-1-c).

def check_E5():
    for name, mx0, g, corr_rr in (
            # a < rho (e = 1): count floor max(0,rho-a-1) = rho-a-1,
            # offset g = b, corr_rr = -a*(b-rho)
            ('a<rho', rho - a - 1, b, -a * (b - rho)),
            # a >= rho (e = 0): count 0, offset g = rho,
            # corr_rr = -rho*(b-a-1)
            ('a>=rho', 0, rho, -rho * (b - a - 1))):
        D = (c_ + 1) * q0 + mx0 - 1
        L = lambda tt: b * (D - tt) + g
        zero(L(t - 1) - L(t) - b, f'E5 tiling {name}')
        lo2, hi2 = L(t2), L(t1) + b - 1
        zero((hi2 - lo2 + 1) - b * (t2 - t1 + 1), f'E5 width {name}')
        zc = t1 + t2 - (N - 1)
        zero((lo2 + hi2 - (N - 1))
             - (-b * zc + (2 * c_ + 1 - b) * N + 2 * corr_rr),
             f'E5 center {name}')
    # simulator tie: preimage of every target is [L, L+b-1] ∩ [0, N)
    for bb, NN in GRID:
        q_, r_ = divmod(NN, bb)
        for cc in range(bb):
            aa = bb - 1 - cc
            pos = rr_map(NN, bb, cc)
            for tt in range(NN):
                D = (cc + 1) * q_ + max(0, r_ - aa - 1) - 1
                Lv = bb * (D - tt) + (bb if aa < r_ else r_)
                want = set(range(max(Lv, 0), min(Lv + bb, NN)))
                got = {x for x in range(NN) if pos[x] == tt}
                assert got == want, (bb, NN, cc, tt, Lv)


# --------------------------------------------------------------------- E6 ----

def check_E6():
    """Offset mirror and argmin mirror: f_rr(b-1-a) = -f_gp(a), so the
    rr argmin at z is the complemented gp argmin at -z."""
    for name, cg in (('a<rho', a * (b - rho)), ('a>=rho',
                                               rho * (b - a - 1))):
        f_gp = (2 * a + 1 - b) * N + 2 * cg
        f_rr = (2 * c_ + 1 - b) * N + 2 * (-cg)
        zero(f_rr + f_gp, f'E6 offset mirror {name}')
    zero((-b * z + F) + (-b * (-z) + (-F)), 'E6 argmin mirror')
    # z_0 mirror: z0(n) = -z0(N+1-n)
    n = sp.Symbol('n')
    zero((2 * (n - 1) - (N - 1)) + (2 * ((N + 1 - n) - 1) - (N - 1)),
         'E6 z0 mirror')


# --------------------------------------------------------------- E7 / E8 ----

def law_vector_rr(n, NN, bb, r):
    r_ = NN % bb
    zz = 2 * (n - 1) - (NN - 1)
    out = []
    for _ in range(r):
        cands = sorted((abs(-bb * zz + (2 * cc + 1 - bb) * NN
                            - 2 * corr_gp_int(bb - 1 - cc, bb, r_)),
                        -cc, cc) for cc in range(bb))
        cc = cands[0][2]
        zz = -bb * zz + (2 * cc + 1 - bb) * NN \
            - 2 * corr_gp_int(bb - 1 - cc, bb, r_)
        out.append(cc)
    return list(reversed(out))


def check_E7():
    """Ground truth: fresh verify() at boundary-tight configs, plus
    extensional agreement with the shipped t26 implementation."""
    spec = importlib.util.spec_from_file_location(
        't26', 'tricks/t26_reversed_rest_acaan.py')
    t26 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t26)
    configs = [(5, 25, 3), (6, 33, 3), (4, 14, 3), (2, 32, 6)]
    for bb, NN, r in configs:
        for n in range(1, NN + 1):
            assert law_vector_rr(n, NN, bb, r) == \
                t26.law_vector_rr(n, NN, bb, r)
    total = 0
    for bb, NN, r in configs:
        assert bb ** (r - 1) >= NN
        ok, counter, cases = t26.run(NN, bb, r)
        assert ok, (bb, NN, r, counter)
        total += cases
    return len(configs), total


def check_E8():
    """Distinctness: the family differs from gather_position at every
    uneven-N interior rank on the grid (the regime where PROVENANCE
    found the literature silent)."""
    checked = 0
    for bb, NN in GRID:
        if NN % bb == 0 or bb < 3:
            continue
        for cc in range(1, bb - 1):
            assert rr_map(NN, bb, cc) != gp_map(NN, bb, cc), (bb, NN, cc)
            checked += 1
        # and coincides at the edge ranks
        assert rr_map(NN, bb, 0) == gp_map(NN, bb, 0)
        assert rr_map(NN, bb, bb - 1) == gp_map(NN, bb, bb - 1)
    return checked


# ---- unit checks (run at import) --------------------------------------------

def _unit_helpers():
    # C_rr closed form at a hand-checked config: b=3, N=7 (q0=2, rho=1)
    pos = rr_map(7, 3, 0)   # rank 0: pointed pile on top
    assert pos[1] == C_rr_int(1, 0, 3, 2, 1) - 0 == 1
    # conjugacy at one hand point: rr_0(1) == 6 - gp_2(6 - 1)
    gp = gp_map(7, 3, 2)
    assert pos[1] == 6 - gp[5]


_unit_helpers()


if __name__ == '__main__':
    print('proof_rr.py unit checks: PASS (hand values)')
    check_E2()
    print('  PASS  E2  C_rr counting derivation (symbolic)')
    check_E1()
    print('  PASS  E1  C_rr closed form == simulator (grid)')
    check_E4()
    print('  PASS  E4  reflection algebra + full map conjugacy (grid)')
    check_E3()
    print('  PASS  E3  Lemma R core: C_rr + C_gp(mirror) = N-2+sizes[j]')
    check_E5()
    print('  PASS  E5  standalone midpoint recursion + preimage grid')
    check_E6()
    print('  PASS  E6  offset/argmin/z0 mirrors (symbolic)')
    nc, total = check_E7()
    print(f'  PASS  E7  ground truth: verify() at {nc} tight configs '
          f'({total} cases) + t26 extensional agreement')
    n8 = check_E8()
    print(f'  PASS  E8  distinct from Gergonne at all {n8} uneven '
          f'interior ranks; equal at edge ranks')
    print('\nREVERSED-REST PROOF CHECKS PASS (E1-E8; prose R1-R2 in '
          'PROOF_reversed_rest.md; inherits PROOF.md via Lemma R)')
