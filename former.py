"""former.py — the conjecture former (engine item 3).

Mechanizes the productive middle step of sessions 7-11: stare at raw
behavior maps, notice affine-in-floor structure, emit an exact closed form,
and package it as a refutable conjecture.

Design contract (the no-hints boundary):
  * Input is a BLACK-BOX parametric round operation
        query(N, b, a) -> newpos list   (newpos[x] = where start position x lands)
    over a packet of N tokens with a round parameter a in 0..b-1. This module
    imports NOTHING from the project: it knows nothing about the simulator's
    operations or any committed law. former_acceptance.py enforces that
    boundary mechanically by scanning this file's source.
  * Declared inductive bias (checked point-by-point, never silently assumed):
        newpos(x) = slope(j, a; N, b) * floor(x / b) + intercept(j, a; N, b)
    with j = x mod b, where slope and intercept are PIECEWISE-LINEAR over the
    atoms  a, j, rho = N mod b, q0 = N div b, b, N  and their pairwise
    products, on cells cut by atom comparisons u < v (a model tree).
    All fits are EXACT rational solves; least-squares never appears here.
  * Refusal is a first-class outcome: a black box outside the grammar
    (non-constant step in q, or no exact piecewise fit within depth/budget)
    makes fit_round_model() return None. The former must not hallucinate.
  * A fitted model is still only a CONJECTURE: exact on its fit grid,
    refutable beyond it. make_instance_test() packages model-vs-black-box
    comparison for refuter.py's ladder; auto_battery() derives the attack
    schedule mechanically from the fit grid's parameter signature.
"""
from fractions import Fraction

ATOMS = ('a', 'j', 'rho', 'q0', 'b', 'N')


def atom_values(pt):
    N, b = pt['N'], pt['b']
    return {'a': pt['a'], 'j': pt['j'], 'rho': N % b, 'q0': N // b,
            'b': b, 'N': N}


def feature_row(pt):
    v = atom_values(pt)
    xs = [v[nm] for nm in ATOMS]
    row = [1] + xs
    for i in range(len(xs)):
        for k in range(i, len(xs)):
            row.append(xs[i] * xs[k])
    return row


FEATURE_NAMES = (['1'] + list(ATOMS) +
                 [f'{ATOMS[i]}*{ATOMS[k]}'
                  for i in range(len(ATOMS)) for k in range(i, len(ATOMS))])


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


def exact_fit(pts, ys):
    """Exact linear fit of ys over feature_row(pts), or None if inconsistent.
    The returned coefficients are re-verified against every point."""
    ech = _Echelon(len(FEATURE_NAMES))
    for pt, y in zip(pts, ys):
        if not ech.add(feature_row(pt), y):
            return None
    sol = ech.solve()
    for pt, y in zip(pts, ys):
        if sum(c * f for c, f in zip(sol, feature_row(pt)) if c) != y:
            return None
    return sol


# ---- model tree: piecewise-linear with atom-comparison splits ----------------

PREDICATES = [(u, v) for u in ATOMS for v in ATOMS if u != v]   # u < v


class _FitBudget(Exception):
    pass


class Leaf:
    def __init__(self, coeffs):
        self.coeffs = coeffs


class Node:
    def __init__(self, u, v, lo, hi):
        self.u, self.v, self.lo, self.hi = u, v, lo, hi      # lo: u < v


def fit_tree(pts, ys, depth=5, min_side=6, budget=None):
    """Smallest-first DFS for an exact model tree. None if no fit in grammar."""
    if budget is None:
        budget = {'solves': 0, 'cap': 4000}
    budget['solves'] += 1
    if budget['solves'] > budget['cap']:
        raise _FitBudget()
    sol = exact_fit(pts, ys)
    if sol is not None:
        return Leaf(sol)
    if depth == 0:
        return None
    for u, v in PREDICATES:
        lo_i = [i for i, pt in enumerate(pts)
                if atom_values(pt)[u] < atom_values(pt)[v]]
        if len(lo_i) < min_side or len(pts) - len(lo_i) < min_side:
            continue
        lo_set = set(lo_i)
        hi_i = [i for i in range(len(pts)) if i not in lo_set]
        lo = fit_tree([pts[i] for i in lo_i], [ys[i] for i in lo_i],
                      depth - 1, min_side, budget)
        if lo is None:
            continue
        hi = fit_tree([pts[i] for i in hi_i], [ys[i] for i in hi_i],
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
    Exactly semantics-preserving."""
    if isinstance(t, Leaf):
        return t
    lo, hi = simplify_tree(t.lo), simplify_tree(t.hi)
    return lo if _tree_eq(lo, hi) else Node(t.u, t.v, lo, hi)


def tree_eval(tree, pt):
    while isinstance(tree, Node):
        v = atom_values(pt)
        tree = tree.lo if v[tree.u] < v[tree.v] else tree.hi
    return sum(c * f for c, f in zip(tree.coeffs, feature_row(pt)) if c)


def _linear_str(coeffs):
    terms = []
    for c, nm in zip(coeffs, FEATURE_NAMES):
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


def tree_str(tree, indent='    '):
    if isinstance(tree, Leaf):
        return indent + _linear_str(tree.coeffs)
    return (f'{indent}if {tree.u} < {tree.v}:\n'
            f'{tree_str(tree.lo, indent + "    ")}\n'
            f'{indent}else:\n'
            f'{tree_str(tree.hi, indent + "    ")}')


# ---- stage 1: extract per-(j, a) cells from the black box --------------------

RICH = 3   # floor values needed to certify affinity within a cell directly


def extract_tables(query, N, b):
    """Harvest raw per-(j, a) cells at one (N, b). A RICH cell (>= 3 floor
    values) has its affinity checked on the spot: a non-constant step is a
    structural refusal (returns None). SPARSE cells (1-2 values, small
    packets) are kept raw; fit_round_model interprets them through the
    slope fitted on rich cells, with an exactness check — so small-q0
    configs can constrain the fit instead of being unrepresentable."""
    cells = []
    for a in range(b):
        mp = query(N, b, a)
        for j in range(b):
            vs = [mp[x] for x in range(j, N, b)]
            if len(vs) >= RICH:
                step = vs[1] - vs[0]
                if any(vs[k + 1] - vs[k] != step
                       for k in range(len(vs) - 1)):
                    return None
            cells.append(({'a': a, 'j': j, 'N': N, 'b': b}, vs))
    return cells


# ---- stage 2: fit both tables, wrap as a model -------------------------------

class FittedRoundModel:
    def __init__(self, slope_tree, c_tree, grid, n_points):
        self.slope_tree, self.c_tree = slope_tree, c_tree
        self.grid, self.n_points = grid, n_points

    def predict(self, x, a, N, b):
        pt = {'a': a, 'j': x % b, 'N': N, 'b': b}
        val = tree_eval(self.c_tree, pt) + tree_eval(self.slope_tree, pt) * (x // b)
        assert val.denominator == 1, (x, a, N, b, val)
        return int(val)

    def table(self, N, b):
        """Full predicted map, one row per round parameter a."""
        return [[self.predict(x, a, N, b) for x in range(N)]
                for a in range(b)]

    def describe(self):
        return (f'fitted on {len(self.grid)} (N, b) configs, '
                f'{self.n_points} (j, a) cells\n'
                f'newpos(x) = slope * floor(x/b) + intercept,  j = x mod b\n'
                f'slope:\n{tree_str(self.slope_tree)}\n'
                f'intercept:\n{tree_str(self.c_tree)}')


def fit_round_model(query, grid):
    """grid: list of (N, b). Returns FittedRoundModel or None (refusal).

    Two-pass: (1) fit the slope on rich cells (affinity already certified
    by extract_tables); (2) turn EVERY cell — sparse ones included — into
    an intercept observation via the fitted slope, refusing any cell whose
    values are inconsistent with that slope; fit the intercept tree on all
    of them. Sparse cells thus constrain the model instead of being lost,
    which is what lets the fit grid span small q0."""
    cells = []
    for N, b in grid:
        got = extract_tables(query, N, b)
        if got is None:
            return None
        cells.extend(got)
    rich = [(pt, vs) for pt, vs in cells if len(vs) >= RICH]
    if not rich:
        return None
    try:
        s_tree = fit_tree([pt for pt, _ in rich],
                          [vs[1] - vs[0] for _, vs in rich])
        if s_tree is None:
            return None
        c_pts, c_ys = [], []
        for pt, vs in cells:
            s = tree_eval(s_tree, pt)
            c0 = {v - s * q for q, v in enumerate(vs)}
            if len(c0) != 1:
                return None
            c_pts.append(pt)
            c_ys.append(c0.pop())
        c_tree = fit_tree(c_pts, c_ys)
        if c_tree is None:
            return None
    except _FitBudget:
        return None
    return FittedRoundModel(simplify_tree(s_tree), simplify_tree(c_tree),
                            list(grid), len(c_pts))


# ---- conjecture packaging (for refuter.py's ladder) --------------------------

def make_instance_test(model, query):
    """Exhaustive model-vs-black-box comparison at one (N, b), in the
    (ok, witness, n_cases) shape refuter.Conjecture expects."""
    def instance_test(N, b):
        cases = 0
        for a in range(b):
            mp = query(N, b, a)
            for x in range(N):
                cases += 1
                if model.predict(x, a, N, b) != mp[x]:
                    return False, {'N': N, 'b': b, 'x': x, 'a': a,
                                   'model': model.predict(x, a, N, b),
                                   'box': mp[x]}, cases
        return True, None, cases
    return instance_test


def auto_battery(grid, seed=20260827):
    """Mechanical attack schedule from the fit grid's parameter signature:
    corners (smallest packets, both rho extremes at scale), monotone
    escalation past every grid maximum, and deterministic out-of-grid draws.
    No hand-curated cases."""
    bs = sorted({b for _, b in grid})
    n_max = max(N for N, _ in grid)
    bmin, bmax = bs[0], bs[-1]
    boundary = []
    for b in (bmin, bmax):
        boundary += [(b, b), (b + 1, b), (2 * b - 1, b),
                     (8 * b, b), (8 * b + b - 1, b)]
    beyond = [(2 * n_max, bmin), (2 * n_max, bmax), (4 * n_max + 1, 2)]
    beyond += [(N, b) for b in (bmax + 1, bmax + 2, bmax + 6)
               for N in (101, 144)]
    s, draws = seed, []
    for _ in range(4):
        s = (1103515245 * s + 12345) % (1 << 31)
        b = 2 + s % 11
        s = (1103515245 * s + 12345) % (1 << 31)
        draws.append((b + s % 200, b))
    return {'boundary': boundary, 'beyond': beyond, 'random_draw': draws}


# ---- model-based targeting planner (uses the MODEL only, never the box) ------

def targeting_vectors(model, N, b, r):
    """Image of the full start set under every r-round parameter sequence,
    computed purely from the fitted model. Returns {vector: frozenset(finals)};
    a vector targets position p iff its image is exactly {p}."""
    tab = model.table(N, b)
    levels = {(): frozenset(range(N))}
    for _ in range(r):
        nxt = {}
        for vec, P in levels.items():
            for a in range(b):
                nxt[vec + (a,)] = frozenset(tab[a][x] for x in P)
        levels = nxt
    return levels


# ---- unit checks (run at import, per project convention) ---------------------

def _unit_exact_fit():
    pts = [{'a': a, 'j': j, 'N': 17, 'b': 4}
           for a in range(4) for j in range(4)]
    ys = [3 * p['a'] - 2 * p['j'] + 7 + p['a'] * p['j'] for p in pts]
    sol = exact_fit(pts, ys)
    assert sol is not None
    for p, y in zip(pts, ys):
        assert sum(c * f for c, f in zip(sol, feature_row(p))) == y
    cubic_pts = [{'a': a, 'j': 0, 'N': 13, 'b': 6} for a in range(6)]
    assert exact_fit(cubic_pts, [a ** 3 for a in range(6)]) is None


def _unit_tree():
    pts = [{'a': a, 'j': j, 'N': 20, 'b': 5}
           for a in range(5) for j in range(5)]
    ys = [max(p['a'], p['j']) for p in pts]
    t = fit_tree(pts, ys)
    assert t is not None and isinstance(t, Node)
    for p, y in zip(pts, ys):
        assert tree_eval(t, p) == y
    # simplify merges branches the data never needed, and nothing else
    same = Node('a', 'j', Leaf([1, 2]), Leaf([1, 2]))
    assert isinstance(simplify_tree(same), Leaf)
    assert isinstance(simplify_tree(Node('a', 'j', Leaf([1]), Leaf([2]))), Node)


def _unit_extract_refusal():
    # a map that is NOT affine in floor(x/b) must be refused at extraction
    def bad_query(N, b, a):
        return [(x * x + a) % N for x in range(N)]
    assert extract_tables(bad_query, 15, 3) is None
    # a map that IS must be harvested (9 cells), and a small packet's
    # sparse cells are kept raw rather than refused
    def good_query(N, b, a):
        return [(x // b) * 2 + (x % b) + a for x in range(N)]
    got = extract_tables(good_query, 15, 3)
    assert got is not None and len(got) == 9
    sparse = extract_tables(good_query, 5, 3)
    assert sparse is not None and all(len(vs) <= 2 for _, vs in sparse)


def _unit_fit_round_model():
    def q(N, b, a):
        return [3 * (x // b) + 2 * (x % b) + a for x in range(N)]
    m = fit_round_model(q, [(12, 3), (13, 3), (5, 3), (9, 2)])
    assert m is not None
    for N, b in ((17, 3), (4, 3)):
        for a in range(b):
            got = q(N, b, a)
            assert all(m.predict(x, a, N, b) == got[x] for x in range(N))
    # a black box inconsistent with any single slope must be refused
    def q_bad(N, b, a):
        return [((x // b) * (x // b) + x) % N for x in range(N)]
    assert fit_round_model(q_bad, [(12, 3), (13, 3)]) is None


_unit_exact_fit()
_unit_tree()
_unit_extract_refusal()
_unit_fit_round_model()


if __name__ == '__main__':
    print('former.py unit checks: PASS (exact fit, refusal, model tree)')
    pts = [{'a': a, 'j': j, 'N': 20, 'b': 5}
           for a in range(5) for j in range(5)]
    t = fit_tree(pts, [max(p['a'], p['j']) for p in pts])
    print('demo — rediscovered closed form for y = max(a, j):')
    print(tree_str(t))
