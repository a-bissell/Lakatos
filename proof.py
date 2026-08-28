"""proof.py — machine checks C1-C10 for PROOF.md (engine item 8).

The proof kernel is deliberately tiny and auditable:

  * zero(e)            — exact polynomial identity (sympy expand == 0);
  * Ctx.nonneg(goal)   — goal >= 0 by a Farkas certificate: goal is
                         EXACTLY a nonnegative rational combination of
                         hypothesis facts (each asserted >= 0), products
                         of facts allowed, plus a nonnegative constant;
  * Ctx.infeasible()   — facts jointly impossible: a nonnegative
                         combination of them is IDENTICALLY a negative
                         constant.

Everything else is straight-line case analysis: each case fixes the
outcomes of the min/max/indicator comparisons, justifies every
resolution with a certificate, and checks the resulting identity
exactly. Case splits are binary/ternary complements by construction
(syntactic exhaustiveness). N = b*q0 + rho is substituted everywhere —
no floor functions appear in any symbolic expression.

Simulator grounding: C1/C2/C4 also cross-check the formalized
conventions against deal_into_piles/gather_position on a (b, N) grid,
and C10 re-runs verify() at boundary-tight configs (b^(r-1) = N).

Unit checks at import reject bad certificates, false identities, and a
wrongly-claimed infeasibility.
"""
import sympy as sp
from deck_sim import (make_deck, make_packet, deal_into_piles,
                      gather_position, verify)

b, q0, rho, a, j, t, t1, t2, v, z, d, B, W, fa, fb = sp.symbols(
    'b q0 rho a j t t1 t2 v z d B W fa fb')
N = b * q0 + rho


def zero(e, what=''):
    r = sp.expand(e)
    assert r == 0, f'identity fails{" (" + what + ")" if what else ""}: {r}'


class Ctx:
    """Facts: {name: expr}, each asserted >= 0 under the case's
    hypotheses. Certificates reference facts by name."""

    def __init__(self, **facts):
        self.facts = {k: sp.expand(e) for k, e in facts.items()}

    def _combo(self, lam, prods, const):
        e = sp.Rational(const)
        assert sp.Rational(const) >= 0
        for name, c in lam:
            assert sp.Rational(c) >= 0, (name, c)
            e += sp.Rational(c) * self.facts[name]
        for names, c in prods:
            assert sp.Rational(c) >= 0, (names, c)
            p = sp.Rational(c)
            for nm in names:
                p *= self.facts[nm]
            e += p
        return e

    def nonneg(self, goal, lam=(), prods=(), const=0, what=''):
        r = sp.expand(goal - self._combo(lam, prods, const))
        assert r == 0, f'Farkas cert fails{" (" + what + ")" if what else ""}: residual {r}'

    def infeasible(self, lam, what=''):
        e = sp.expand(self._combo(lam, (), 0))
        assert e.is_number and e < 0, \
            f'infeasibility cert fails{" (" + what + ")" if what else ""}: {e}'


def base_ctx(**extra):
    """H1 (b >= 2), H2 (N >= b i.e. q0 >= 1), 0 <= rho <= b-1."""
    facts = dict(b2=b - 2, q01=q0 - 1, rho0=rho, rho_hi=b - 1 - rho)
    facts.update(extra)
    return Ctx(**facts)


GRID = [(bb, NN) for bb in range(2, 9)
        for NN in (bb, bb + 1, 2 * bb - 1, 3 * bb + 2)]


def corr_int(aa, bb, r_):
    return min(aa, r_) * (bb - max(aa + 1, r_))


def C_int(jj, aa, bb, q_, r_):
    """The Lemma 2 closed form, integer version."""
    if jj <= aa:
        return (aa + 1) * q_ + min(aa + 1, r_) - 1
    return (aa + 1) * q_ + min(aa, r_) + (1 if jj < r_ else 0) - 1


def L_int(tt, aa, bb, q_, r_):
    """The Lemma 3 preimage left end, integer version."""
    Da = (aa + 1) * q_ + min(aa, r_) - 1
    return bb * (Da - tt) + (r_ if aa < r_ else 0)


# ---------------------------------------------------------------- C1 / C1s --

def check_C1s():
    """Division identity behind sizes[j] = q0 + [j < rho]: exhibit
    quotient and remainder for (N - j + b - 1) with certified range."""
    # case j < rho: quotient q0 + 1, remainder rho - j - 1
    c = base_ctx(jr=rho - 1 - j, j0=j)
    zero((N - j + b - 1) - (b * (q0 + 1) + (rho - j - 1)), 'C1s quot hi')
    c.nonneg(rho - j - 1, lam=[('jr', 1)], what='C1s rem >= 0')
    c.nonneg((b - 1) - (rho - j - 1), lam=[('rho_hi', 1), ('j0', 1)],
             const=1, what='C1s rem < b')
    # case j >= rho: quotient q0, remainder b - 1 - (j - rho)
    c = base_ctx(jge=j - rho, jlt=b - 1 - j)
    zero((N - j + b - 1) - (b * q0 + (b - 1 - (j - rho))), 'C1s quot lo')
    c.nonneg(b - 1 - (j - rho), lam=[('jlt', 1), ('rho0', 1)],
             what='C1s rem >= 0')
    c.nonneg((b - 1) - (b - 1 - (j - rho)), lam=[('jge', 1)],
             what='C1s rem < b')


def check_C1():
    """Simulator tie: sizes and depths on the grid."""
    for bb, NN in GRID:
        q_, r_ = divmod(NN, bb)
        piles = deal_into_piles(list(range(NN)), bb)
        for jj in range(bb):
            assert len(piles[jj]) == q_ + (1 if jj < r_ else 0), (bb, NN, jj)
        for x in range(NN):
            jj = x % bb
            depth = len(piles[jj]) - 1 - x // bb
            assert piles[jj].index(x) == depth, (bb, NN, x)


# ----------------------------------------------------------------- C2 / C3 --

def check_C3():
    """sum_{k in A} sizes[k] + sizes[j] - 1 == C(j, a), per case.
    Indicators appear as a free symbol I where they cancel."""
    I = sp.Symbol('I')  # [j < rho], unresolved where it cancels
    # --- case j <= a ------------------------------------------------------
    # A = [0, a+1) \ {j};  |A ∩ [0, rho)| = m - [j < m], m = min(a+1, rho)
    # sub-case rho <= a+1:  m = rho, so [j < m] == [j < rho] literally;
    # the indicator cancels against sizes[j] = q0 + [j < rho]:
    S_A = a * q0 + (rho - I)
    zero(S_A + (q0 + I) - 1 - ((a + 1) * q0 + rho - 1), 'C3 j<=a, rho<=a+1')
    # sub-case rho >= a+2:  m = a+1; [j < a+1] = 1 and [j < rho] = 1
    c = base_ctx(aj=a - j, j0=j, a0=a, ra2=rho - a - 2)
    c.nonneg(a - j, lam=[('aj', 1)], what='C3 [j<a+1]=1')
    c.nonneg(rho - 1 - j, lam=[('ra2', 1), ('aj', 1)], const=1,
             what='C3 [j<rho]=1')
    S_A = a * q0 + ((a + 1) - 1)
    zero(S_A + (q0 + 1) - 1 - ((a + 1) * q0 + (a + 1) - 1),
         'C3 j<=a, rho>=a+2')
    # --- case j > a -------------------------------------------------------
    # A = [0, a);  |A ∩ [0, rho)| = min(a, rho); indicator survives in C
    for sub, mn, cert in (('a<=rho', a, ('ra', rho - a)),
                          ('a>rho', rho, ('ar', a - rho - 1))):
        c = base_ctx(**{cert[0]: cert[1]})
        c.nonneg(cert[1], lam=[(cert[0], 1)], what=f'C3 case cond {sub}')
        S_A = a * q0 + mn
        zero(S_A + (q0 + I) - 1 - ((a + 1) * q0 + mn + I - 1),
             f'C3 j>a, {sub}')


def check_C2():
    """Simulator tie: closed form == gather_position on the grid."""
    for bb, NN in GRID:
        q_, r_ = divmod(NN, bb)
        markers = list(range(NN))
        for aa in range(bb):
            piles = deal_into_piles(markers, bb)
            for x in range(NN):
                jj = x % bb
                got = gather_position(deal_into_piles(markers, bb),
                                      jj, aa).index(x)
                assert got == C_int(jj, aa, bb, q_, r_) - x // bb, \
                    (bb, NN, x, aa)


# ---------------------------------------------------------------------- C4 --

def _concat(runs, ctx, what):
    """Runs [(lo_i, hi_i)]: prove each nonempty (hi - lo >= 0 by the
    given cert) and adjacent (lo_{i+1} == hi_i + 1); returns the
    concatenated (lo, hi)."""
    for i, (lo, hi, cert) in enumerate(runs):
        ctx.nonneg(hi - lo, **cert)
        if i:
            zero(lo - (runs[i - 1][1] + 1), f'{what} adjacency {i}')
    return runs[0][0], runs[-1][1]


def check_C4():
    """Single-target preimage = b consecutive positions; L formula."""
    # case a < rho, sub-case a <= rho - 2 (middle run nonempty)
    c = base_ctx(ar1=rho - a - 1, ar2=rho - a - 2, a0=a, jb=b - 1 - j)
    Da = (a + 1) * q0 + a - 1          # min(a, rho) = a  [rho - a >= 0]
    c.nonneg(rho - a, lam=[('ar1', 1)], const=1, what='C4 min(a,rho)=a')
    # C values: j <= a -> Da + 1;  a < j < rho -> Da + 1;  j >= rho -> Da
    zero(((a + 1) * q0 + (a + 1) - 1) - (Da + 1), 'C4 Ca = Da+1')
    base = b * (Da - t)
    lo, hi = _concat(
        [(base + rho, base + (b - 1),
          dict(lam=[('rho_hi', 1)], what='C4 run3')),
         (base + b, base + b + a, dict(lam=[('a0', 1)], what='C4 run1')),
         (base + b + a + 1, base + b + rho - 1,
          dict(lam=[('ar2', 1)], what='C4 run2'))],
        c, 'C4 a<=rho-2')
    zero(lo - (base + rho), 'C4 L, a<rho')
    zero(hi - lo + 1 - b, 'C4 width, a<=rho-2')
    # sub-case a = rho - 1: substitute rho -> a+1, middle run empty
    S = {rho: a + 1}
    c = base_ctx(a0=a, ab1=b - a - 2)
    baseS = (b * (Da - t)).subs(S)
    lo, hi = _concat(
        [((base + rho).subs(S), (base + (b - 1)).subs(S),
          dict(lam=[('ab1', 1)], what='C4 run3 (a=rho-1)')),
         ((base + b).subs(S), (base + b + a).subs(S),
          dict(lam=[('a0', 1)], what='C4 run1 (a=rho-1)'))],
        c, 'C4 a=rho-1')
    zero(lo - (baseS + (a + 1)), 'C4 L, a=rho-1')
    zero(hi - lo + 1 - b, 'C4 width, a=rho-1')
    # case a >= rho: all C values equal Da' = (a+1)q0 + rho - 1
    # sub-case a <= b-2 (second run nonempty)
    c = base_ctx(ra=a - rho, a0=a, ab2=b - 2 - a)
    Dp = (a + 1) * q0 + rho - 1        # min(a, rho) = rho
    c.nonneg(a - rho, lam=[('ra', 1)], what='C4 min(a,rho)=rho')
    zero(((a + 1) * q0 + rho - 1) - Dp, 'C4 Ca (min(a+1,rho)=rho)')
    base = b * (Dp - t)
    lo, hi = _concat(
        [(base + 0, base + a, dict(lam=[('a0', 1)], what='C4 runA')),
         (base + a + 1, base + b - 1,
          dict(lam=[('ab2', 1)], what='C4 runB'))],
        c, 'C4 a>=rho, a<=b-2')
    zero(lo - base, 'C4 L, a>=rho')
    zero(hi - lo + 1 - b, 'C4 width, a>=rho, a<=b-2')
    # sub-case a = b-1 (substitute a -> b-1: the j <= a run is everything)
    Sa = {a: b - 1}
    lo, hi = (base + 0).subs(Sa), (base + a).subs(Sa)
    zero(lo - base.subs(Sa), 'C4 L, a=b-1')
    zero(hi - lo + 1 - b, 'C4 width, a=b-1')
    # simulator tie: preimage sets on the grid
    for bb, NN in GRID:
        q_, r_ = divmod(NN, bb)
        markers = list(range(NN))
        for aa in range(bb):
            img = {}
            for x in range(NN):
                jj = x % bb
                img[x] = gather_position(deal_into_piles(markers, bb),
                                         jj, aa).index(x)
            for tt in range(NN):
                Lv = L_int(tt, aa, bb, q_, r_)
                want = set(range(max(Lv, 0), min(Lv + bb, NN)))
                got = {x for x in range(NN) if img[x] == tt}
                assert got == want, (bb, NN, aa, tt, Lv)


# ---------------------------------------------------------------------- C5 --

def check_C5():
    """Tiling, endpoint recursion, width, doubled-center identity,
    and the corr bracket — per case a < rho / a >= rho."""
    for name, mn_a, mx_a1, ind in (('a<rho', a, rho, 1),
                                   ('a>=rho', rho, a + 1, 0)):
        Da = (a + 1) * q0 + mn_a - 1
        Lt = lambda tt: b * (Da - tt) + rho * ind
        corr_c = mn_a * (b - mx_a1)
        zero(Lt(t - 1) - Lt(t) - b, f'C5 tiling {name}')
        lo2, hi2 = Lt(t2), Lt(t1) + b - 1
        zero((hi2 - lo2 + 1) - b * (t2 - t1 + 1), f'C5 width {name}')
        zc = t1 + t2 - (N - 1)
        zero((lo2 + hi2 - (N - 1))
             - (-b * zc + (2 * a + 1 - b) * N + 2 * corr_c),
             f'C5 center {name}')
        # corr bracket: b*min - (a+1)*rho + rho*[a<rho] == min*(b - max)
        zero((b * mn_a - (a + 1) * rho + rho * ind) - corr_c,
             f'C5 bracket {name}')


# ---------------------------------------------------------------------- C6 --

def check_C6():
    """Offset structure: span endpoints, consecutive gaps, gap bounds."""
    f = lambda aa, cc: (2 * aa + 1 - b) * N + 2 * cc
    zero(f(0, 0) + (b - 1) * N, 'C6 f(0)')          # corr(0) = 0
    zero(f(b - 1, 0) - (b - 1) * N, 'C6 f(b-1)')    # corr(b-1) = 0
    base_ctx().nonneg(b - rho, lam=[('rho_hi', 1)], const=1,
                      what='C6 max(b,rho)=b')       # justifies corr(b-1)=0
    # gap g = f(a+1) - f(a) = 2N + 2*dcorr, three cases for dcorr
    cases = []
    # case a+1 < rho: dcorr = b - rho
    c = base_ctx(c1=rho - a - 2, a0=a, ab1=b - 2 - a)
    zero(((a + 1) * (b - rho) - a * (b - rho)) - (b - rho), 'C6 d1')
    cases.append((c, b - rho,
                  dict(lam=[('rho_hi', 2), ('b2', 2)], const=4),
                  dict(lam=[('c1', 2), ('a0', 2)])))
    # case a+1 = rho (rho -> a+1): dcorr = b - 2a - 2
    c = Ctx(b2=b - 2, q01=q0 - 1, a0=a, ab1=b - 2 - a)
    zero(((a + 1) * (b - a - 2) - a * (b - a - 1)) - (b - 2 * a - 2),
         'C6 d2')
    cases.append((c, b - 2 * a - 2,
                  dict(lam=[('ab1', 4)], const=2),
                  dict(lam=[('a0', 4)])))
    # case a >= rho: dcorr = -rho
    c = base_ctx(c3=a - rho, a0=a, ab1=b - 2 - a)
    zero((rho * (b - a - 2) - rho * (b - a - 1)) - (-rho), 'C6 d3')
    cases.append((c, -rho,
                  dict(lam=[('rho_hi', 2)]),
                  dict(lam=[('b2', 2), ('rho0', 2)])))
    for c, dc, lo_cert, hi_cert in cases:
        g = 2 * N + 2 * dc
        c.nonneg(g - 2 * (N - b + 1), **lo_cert)     # gap >= 2(N-b+1) > 0
        c.nonneg(2 * (N + b - 2) - g, **hi_cert)     # gap <= 2(N+b-2)


# ---------------------------------------------------------------------- C7 --

def check_C7():
    """One-step bound, both branches (the bracketing 'some a exists' is
    P1, prose: f strictly increasing + span endpoints)."""
    # (i) in-span: both distances > half-gap is infeasible
    c = Ctx(lo=v - fa - (N + b - 2) - 1, hi=fb - v - (N + b - 2) - 1,
            gap=2 * (N + b - 2) - (fb - fa))
    c.infeasible([('lo', 1), ('hi', 1), ('gap', 1)], what='C7 half-gap')
    # (ii) beyond the top offset: distance to f(b-1) <= N + b*d
    c = Ctx(vbd=b * (N + d) - v)
    c.nonneg((N + b * d) - (v - (b - 1) * N), lam=[('vbd', 1)],
             what='C7 out-span right')
    c = Ctx(vbd2=v + b * (N + d))
    c.nonneg((N + b * d) - (-(b - 1) * N - v), lam=[('vbd2', 1)],
             what='C7 out-span left')


# ----------------------------------------------------------------- C8 / C9 --

def check_C8():
    """Envelope step, coverage endpoints, coverage <=> H3."""
    # envelope step: b*(b-2)*B >= b-2 for B = b^(k-1) >= 1
    c = Ctx(b2=b - 2, B1=B - 1)
    c.nonneg(b * (b - 2) * B - (b - 2),
             prods=[(('b2', 'b2', 'B1'), 1), (('b2', 'B1'), 2),
                    (('b2', 'b2'), 1), (('b2',), 1)],
             what='C8 envelope step')
    # doubled endpoints of the round-r interval (b^r = b*W, W = b^(r-1))
    lo2 = z + N - b * W
    hi2 = z + N + b * W - 2 * N      # 2*hi_r = z_r + (N-1) + (b^r - 1)
    zero(hi2 - (z - N + b * W), 'C8 endpoints')
    # coverage: lo_r <= 0 and hi_r >= N-1  <=>  |z_r| <= b*W - N (doubling
    # preserves integer inequalities; prose note). Final chain:
    c = Ctx(WN=W - N, b2=b - 2, W1=W - 1)
    c.nonneg((b * W - N) - (N + (b - 2) * W), lam=[('WN', 2)],
             what='C8 coverage from H3')


def check_C9():
    """|z_0| <= N - 1 for targets t in [0, N-1]."""
    c = base_ctx(t0=t, tN=N - 1 - t)
    z0 = 2 * t - (N - 1)
    c.nonneg((N - 1) - z0, lam=[('tN', 2)], what='C9 upper')
    c.nonneg(z0 + (N - 1), lam=[('t0', 2)], what='C9 lower')


# --------------------------------------------------------------------- C10 --

def law_vector(n, NN, bb, r):
    """The theorem's algorithm (restated from tricks/t22; extensional
    agreement with the shipped implementation is checked in C10)."""
    r_ = NN % bb
    zz = 2 * (n - 1) - (NN - 1)
    digits = []
    for _ in range(r):
        cands = sorted((abs(-bb * zz + (2 * aa + 1 - bb) * NN
                            + 2 * corr_int(aa, bb, r_)), -aa, aa)
                       for aa in range(bb))
        aa = cands[0][2]
        zz = -bb * zz + (2 * aa + 1 - bb) * NN + 2 * corr_int(aa, bb, r_)
        digits.append(aa)
    return list(reversed(digits))


def check_C10():
    """Ground truth at boundary-tight configs (b^(r-1) == N where
    possible) — the proof explains verify(), never replaces it."""
    configs = [(5, 25, 3), (6, 36, 3), (7, 49, 3), (2, 32, 6),
               (6, 33, 3), (5, 23, 3), (12, 144, 3)]
    # extensional agreement with the shipped t22 implementation
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        't22', 'tricks/t22_general_b_law.py')
    t22 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t22)
    for bb, NN, r in configs[:6]:
        for n in range(1, NN + 1):
            assert law_vector(n, NN, bb, r) == t22.law_vector(n, NN, bb, r)
    total = 0
    for bb, NN, r in configs:
        assert bb ** (r - 1) >= NN
        factory = ((lambda NN=NN: make_packet(NN)) if NN > 52
                   else make_deck)

        def trick(deck, choices, bb=bb, NN=NN, r=r):
            dd = deck[:NN]
            card = choices['card']
            for aa in law_vector(choices['n'], NN, bb, r):
                piles = deal_into_piles(dd, bb)
                jj = next(i for i, p in enumerate(piles) if card in p)
                dd = gather_position(piles, jj, aa)
            return dd

        domain = [{'card': c, 'n': n}
                  for c in factory()[:NN]
                  for n in range(1, NN + 1)]
        ok, counter = verify(trick, domain, lambda f, ch: f[ch['n'] - 1],
                             deck_factory=factory)
        assert ok, (bb, NN, r, counter)
        total += len(domain)
    return len(configs), total


# ---- kernel unit checks (run at import) -------------------------------------

def _unit_kernel():
    c = Ctx(p=b - 2, q=q0 - 1)
    c.nonneg(b - 2, lam=[('p', 1)])
    c.nonneg(2 * b + 3 * q0 - 7, lam=[('p', 2), ('q', 3)])
    c.nonneg((b - 2) * (q0 - 1), prods=[(('p', 'q'), 1)])
    for bad in (lambda: c.nonneg(b - 3, lam=[('p', 1)]),
                lambda: c.nonneg(2 - b, lam=[('p', 1)]),
                lambda: c.nonneg(b - 2, lam=[('p', -1)], const=2 * b - 4),
                lambda: zero(b - 2)):
        try:
            bad()
        except (AssertionError, TypeError):
            continue  # rejected (TypeError = non-rational certificate part)
        raise AssertionError('kernel accepted a bad certificate')
    c = Ctx(x=v - 1, y=-v)   # v >= 1 and v <= 0: impossible
    c.infeasible([('x', 1), ('y', 1)])
    try:
        Ctx(x=v - 1, y=v).infeasible([('x', 1), ('y', 1)])
    except AssertionError:
        pass
    else:
        raise AssertionError('kernel accepted a bad infeasibility cert')


_unit_kernel()


if __name__ == '__main__':
    checks = [('C1s division algebra for pile sizes', check_C1s),
              ('C1  sizes/depths == simulator (grid)', check_C1),
              ('C3  round-map closed form (symbolic)', check_C3),
              ('C2  closed form == simulator (grid)', check_C2),
              ('C4  preimage interval + L formula', check_C4),
              ('C5  tiling / endpoints / midpoint law', check_C5),
              ('C6  offset span and gap bounds', check_C6),
              ('C7  one-step bound arithmetic', check_C7),
              ('C8  envelope step + coverage <=> H3', check_C8),
              ('C9  initial bound |z_0| <= N-1', check_C9)]
    print('proof.py kernel unit checks: PASS (bad certs rejected)')
    for name, fn in checks:
        fn()
        print(f'  PASS  {name}')
    nc, total = check_C10()
    print(f'  PASS  C10 ground truth: verify() at {nc} boundary-tight '
          f'configs ({total} cases)')
    print('\nPROOF CHECKS PASS (C1-C10; prose steps P1-P3 documented in '
          'PROOF.md)')
