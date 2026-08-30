"""lakatos/proof_kernel.py — the Farkas certificate kernel, domain-agnostic.

Extracted from proof.py (engine item 8) per FRAMEWORK.md step 3. The kernel is
deliberately tiny and auditable, and knows nothing about any domain — it
operates on sympy expressions over whatever symbols a domain supplies:

  * zero(e)            — exact polynomial identity (sympy expand == 0);
  * Ctx.nonneg(goal)   — goal >= 0 by a Farkas certificate: goal is EXACTLY a
                         nonnegative rational combination of hypothesis facts
                         (each asserted >= 0), products of facts allowed, plus
                         a nonnegative constant;
  * Ctx.infeasible()   — facts jointly impossible: a nonnegative combination of
                         them is IDENTICALLY a negative constant.

A domain builds a Ctx from its own hypothesis facts (expressions over its own
symbols) and discharges each goal with a certificate. This is the only step
that promotes a ROBUST_CONJECTURE to THEOREM; the refuter cannot reach it.

Unit checks at import reject bad certificates, false identities, and a
wrongly-claimed infeasibility — over generic symbols, never card ones.
"""
import sympy as sp


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


# ---- kernel unit checks (run at import; over GENERIC symbols) ----------------

def _unit_kernel():
    m, n, w = sp.symbols('m n w')
    c = Ctx(p=m, q=n)                          # facts p = m >= 0, q = n >= 0
    c.nonneg(m, lam=[('p', 1)])
    c.nonneg(2 * m + 3 * n, lam=[('p', 2), ('q', 3)])
    c.nonneg(m * n, prods=[(('p', 'q'), 1)])
    for bad in (lambda: c.nonneg(m - 1, lam=[('p', 1)]),        # residual -1
                lambda: c.nonneg(-m, lam=[('p', 1)]),           # goal not >= combo
                lambda: c.nonneg(m, lam=[('p', -1)], const=2 * m),  # neg coeff / non-const
                lambda: zero(m)):                               # false identity
        try:
            bad()
        except (AssertionError, TypeError):
            continue  # rejected (TypeError = non-rational certificate part)
        raise AssertionError('kernel accepted a bad certificate')
    c = Ctx(x=w - 1, y=-w)                      # w >= 1 and w <= 0: impossible
    c.infeasible([('x', 1), ('y', 1)])
    try:
        Ctx(x=w - 1, y=w).infeasible([('x', 1), ('y', 1)])
    except AssertionError:
        pass
    else:
        raise AssertionError('kernel accepted a bad infeasibility cert')


_unit_kernel()


if __name__ == '__main__':
    print('lakatos/proof_kernel.py unit checks: PASS (bad certs / false '
          'identities / wrong infeasibility all rejected, generic symbols)')
