"""lakatos/fitter.py — the exact conjecture-fitter, domain-agnostic.

Extracted from former.py (engine item 3) as part of the lakatos/domains split
(FRAMEWORK.md, step 1). This is the mechanical heart of the former: exact
rational linear fits and piecewise-linear model trees over an INJECTED feature
basis. It knows nothing about the domain it fits — no cards, no simulator, no
committed law. A domain supplies a FeatureBasis (its atoms and how to read them
off a point); the fitter derives the quadratic feature row and the
atom-comparison split predicates from that alone.

Refusal is a first-class outcome: exact_fit returns None on an inconsistent
system; fit_tree returns None when no exact tree exists within depth/budget.
The fitter never approximates — least-squares never appears here.
"""
from fractions import Fraction


class FeatureBasis:
    """A domain's fit vocabulary. `atoms` is the ordered tuple of atom names;
    `read(pt)` maps a point (any dict) to {atom_name: int value}. The fitter
    derives, knowing nothing else about the domain:
      * feature_row(pt) = [1] + atoms + all pairwise products  (quadratic basis)
      * predicates      = ordered atom pairs (u, v), each a split  u < v
    The entire domain lives in `read`; swap it and the same fitter fits."""

    def __init__(self, atoms, read):
        self.atoms = tuple(atoms)
        self.read = read
        self.names = (['1'] + list(self.atoms) +
                      [f'{self.atoms[i]}*{self.atoms[k]}'
                       for i in range(len(self.atoms))
                       for k in range(i, len(self.atoms))])
        self.predicates = [(u, v) for u in self.atoms for v in self.atoms
                           if u != v]

    def feature_row(self, pt):
        v = self.read(pt)
        xs = [v[nm] for nm in self.atoms]
        row = [1] + xs
        for i in range(len(xs)):
            for k in range(i, len(xs)):
                row.append(xs[i] * xs[k])
        return row


# ---- exact linear algebra (incremental RREF, early inconsistency exit) -------

class _Echelon:
    """Incremental exact row reduction. add() returns False the moment the
    system becomes inconsistent, so failed fits are cheap."""

    def __init__(self, width):
        self.width = width
        self.rows = []          # (coeffs list[Fraction], rhs, pivot_col), RREF

    def add(self, feats, y):
        r = [Fraction(f) for f in feats]
        rhs = Fraction(y)
        for prow, prhs, pcol in self.rows:
            f = r[pcol]
            if f:
                r = [ri - f * pi for ri, pi in zip(r, prow)]
                rhs -= f * prhs
        pcol = next((i for i, ri in enumerate(r) if ri), None)
        if pcol is None:
            return rhs == 0
        inv = Fraction(1) / r[pcol]
        r = [ri * inv for ri in r]
        rhs *= inv
        for k, (er, erhs, ecol) in enumerate(self.rows):
            f = er[pcol]
            if f:
                self.rows[k] = ([ei - f * ri for ei, ri in zip(er, r)],
                                erhs - f * rhs, ecol)
        self.rows.append((r, rhs, pcol))
        return True

    def solve(self):
        """One exact solution with every free variable set to 0."""
        sol = [Fraction(0)] * self.width
        for prow, prhs, pcol in self.rows:
            sol[pcol] = prhs
        return sol


def exact_fit(basis, pts, ys):
    """Exact linear fit of ys over basis.feature_row(pts), or None if
    inconsistent. The returned coefficients are re-verified against every
    point."""
    ech = _Echelon(len(basis.names))
    for pt, y in zip(pts, ys):
        if not ech.add(basis.feature_row(pt), y):
            return None
    sol = ech.solve()
    for pt, y in zip(pts, ys):
        if sum(c * f for c, f in zip(sol, basis.feature_row(pt)) if c) != y:
            return None
    return sol


# ---- model tree: piecewise-linear with atom-comparison splits ----------------

class _FitBudget(Exception):
    pass


class Leaf:
    def __init__(self, coeffs):
        self.coeffs = coeffs


class Node:
    def __init__(self, u, v, lo, hi):
        self.u, self.v, self.lo, self.hi = u, v, lo, hi      # lo: u < v


def fit_tree(basis, pts, ys, depth=5, min_side=6, budget=None):
    """Smallest-first DFS for an exact model tree. None if no fit in grammar."""
    if budget is None:
        budget = {'solves': 0, 'cap': 4000}
    budget['solves'] += 1
    if budget['solves'] > budget['cap']:
        raise _FitBudget()
    sol = exact_fit(basis, pts, ys)
    if sol is not None:
        return Leaf(sol)
    if depth == 0:
        return None
    for u, v in basis.predicates:
        lo_i = [i for i, pt in enumerate(pts)
                if basis.read(pt)[u] < basis.read(pt)[v]]
        if len(lo_i) < min_side or len(pts) - len(lo_i) < min_side:
            continue
        lo_set = set(lo_i)
        hi_i = [i for i in range(len(pts)) if i not in lo_set]
        lo = fit_tree(basis, [pts[i] for i in lo_i], [ys[i] for i in lo_i],
                      depth - 1, min_side, budget)
        if lo is None:
            continue
        hi = fit_tree(basis, [pts[i] for i in hi_i], [ys[i] for i in hi_i],
                      depth - 1, min_side, budget)
        if hi is None:
            continue
        return Node(u, v, lo, hi)
    return None


def _tree_eq(t1, t2):
    if isinstance(t1, Leaf) and isinstance(t2, Leaf):
        return t1.coeffs == t2.coeffs
    if isinstance(t1, Node) and isinstance(t2, Node):
        return ((t1.u, t1.v) == (t2.u, t2.v)
                and _tree_eq(t1.lo, t2.lo) and _tree_eq(t1.hi, t2.hi))
    return False


def simplify_tree(t):
    """Merge structurally identical branches (a split the data never needed).
    Exactly semantics-preserving. Structure-only — no basis needed."""
    if isinstance(t, Leaf):
        return t
    lo, hi = simplify_tree(t.lo), simplify_tree(t.hi)
    return lo if _tree_eq(lo, hi) else Node(t.u, t.v, lo, hi)


def tree_eval(basis, tree, pt):
    while isinstance(tree, Node):
        v = basis.read(pt)
        tree = tree.lo if v[tree.u] < v[tree.v] else tree.hi
    return sum(c * f for c, f in zip(tree.coeffs, basis.feature_row(pt)) if c)


def _linear_str(basis, coeffs):
    terms = []
    for c, nm in zip(coeffs, basis.names):
        if c == 0:
            continue
        if nm == '1':
            terms.append(str(c))
        elif c == 1:
            terms.append(nm)
        elif c == -1:
            terms.append(f'-{nm}')
        else:
            terms.append(f'{c}*{nm}')
    return ' + '.join(terms).replace('+ -', '- ') if terms else '0'


def tree_str(basis, tree, indent='    '):
    if isinstance(tree, Leaf):
        return indent + _linear_str(basis, tree.coeffs)
    return (f'{indent}if {tree.u} < {tree.v}:\n'
            f'{tree_str(basis, tree.lo, indent + "    ")}\n'
            f'{indent}else:\n'
            f'{tree_str(basis, tree.hi, indent + "    ")}')


# ---- unit checks (run at import; use a GENERIC basis, never a card one) ------

def _unit_generic_fit():
    """Prove the fitter is domain-free: fit over atoms ('p', 'q') that have
    nothing to do with cards."""
    basis = FeatureBasis(('p', 'q'), lambda pt: {'p': pt['p'], 'q': pt['q']})
    pts = [{'p': p, 'q': q} for p in range(4) for q in range(4)]
    ys = [3 * pt['p'] - 2 * pt['q'] + 7 + pt['p'] * pt['q'] for pt in pts]
    sol = exact_fit(basis, pts, ys)
    assert sol is not None
    for pt, y in zip(pts, ys):
        assert sum(c * f for c, f in zip(sol, basis.feature_row(pt))) == y
    # a cubic in p is outside the quadratic basis -> exact_fit must refuse
    cub = [{'p': p, 'q': 0} for p in range(6)]
    assert exact_fit(basis, cub, [p ** 3 for p in range(6)]) is None
    # model tree rediscovers y = max(p, q) via a p<q split
    ymax = [max(pt['p'], pt['q']) for pt in pts]
    t = fit_tree(basis, pts, ymax, min_side=4)
    assert t is not None and isinstance(t, Node)
    for pt, y in zip(pts, ymax):
        assert tree_eval(basis, t, pt) == y
    same = Node('p', 'q', Leaf([1, 2]), Leaf([1, 2]))
    assert isinstance(simplify_tree(same), Leaf)


_unit_generic_fit()


if __name__ == '__main__':
    print('lakatos/fitter.py unit checks: PASS (exact fit, refusal, model tree '
          '— over a generic non-card basis)')
    basis = FeatureBasis(('p', 'q'), lambda pt: {'p': pt['p'], 'q': pt['q']})
    pts = [{'p': p, 'q': q} for p in range(4) for q in range(4)]
    t = fit_tree(basis, pts, [max(pt['p'], pt['q']) for pt in pts], min_side=4)
    print('demo — rediscovered closed form for y = max(p, q):')
    print(tree_str(basis, t))
