"""
mr_algebra.py -- a small, dependency-free toolkit for SQUAREFREE monomial ideals.

Why squarefree only?  In the "Algebraic Machine Reasoning: Mathematical
Preliminaries" note, observations are encoded as squarefree monomials (one
attribute value per attribute), so every object we handle is a squarefree
monomial ideal.  For those ideals everything reduces to set operations:

    monomial            <->  frozenset of variable names
    ideal               <->  antichain of monomials (its minimal generators)
    lcm(m1, m2)         <->  m1 | m2
    m1 divides m2       <->  m1 <= m2   (subset)

Facts used (standard; see Miller-Sturmfels, "Combinatorial Commutative Algebra"):
  * J1 + J2  = <gens of both>
  * J1 * J2  = <g*h>                      (here: g | h)
  * J1 & J2  = <lcm(g, h)>                (here: g | h)    [monomial ideals]
  * The minimal primes of a squarefree monomial ideal I are exactly <T> for the
    minimal transversals (minimal vertex covers) T of the hypergraph whose edges
    are the supports of the minimal generators, and  I = intersection of them.
"""
from __future__ import annotations

from itertools import product
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set

Mono = FrozenSet[str]


# ----------------------------------------------------------------------------
# Basic ideal arithmetic
# ----------------------------------------------------------------------------
def minimalize(gens: Iterable[Mono]) -> List[Mono]:
    """Return the unique minimal generating set (an antichain under subset)."""
    uniq = sorted(set(gens), key=lambda m: (len(m), sorted(m)))
    kept: List[Mono] = []
    for m in uniq:
        if not any(k <= m for k in kept):
            kept.append(m)
    return kept


def ideal_sum(a: Iterable[Mono], b: Iterable[Mono]) -> List[Mono]:
    return minimalize(list(a) + list(b))


def ideal_product(a: Iterable[Mono], b: Iterable[Mono]) -> List[Mono]:
    return minimalize(g | h for g, h in product(a, b))


def ideal_intersection(a: Iterable[Mono], b: Iterable[Mono]) -> List[Mono]:
    # For monomial ideals: I & J = <lcm(g, h)>.  For squarefree: lcm = union.
    return minimalize(g | h for g, h in product(a, b))


def contains(ideal: Sequence[Mono], m: Mono) -> bool:
    """Ideal membership of a monomial: some generator divides it."""
    return any(g <= m for g in ideal)


def ideal_contains_ideal(big: Sequence[Mono], small: Sequence[Mono]) -> bool:
    """small <= big  iff every generator of small lies in big."""
    return all(contains(big, g) for g in small)


def same_ideal(a: Sequence[Mono], b: Sequence[Mono]) -> bool:
    return set(minimalize(a)) == set(minimalize(b))


# ----------------------------------------------------------------------------
# Primary (= prime, for squarefree) decomposition
# ----------------------------------------------------------------------------
class TooManyTransversals(RuntimeError):
    pass


def minimal_transversals(edges: Iterable[Mono], limit: Optional[int] = None) -> List[Mono]:
    """Berge's algorithm for the minimal transversals of a hypergraph.

    Worst-case output size is exponential; `limit` aborts if the intermediate
    antichain grows beyond it (raises TooManyTransversals).
    """
    edges = minimalize(edges)
    trans: List[Mono] = [frozenset()]
    for e in edges:
        new: List[Mono] = []
        for t in trans:
            if t & e:
                new.append(t)
            else:
                new.extend(t | {v} for v in e)
        trans = minimalize(new)
        if limit is not None and len(trans) > limit:
            raise TooManyTransversals(f"> {limit} partial transversals")
    return trans


def minimal_primes(gens: Iterable[Mono], limit: Optional[int] = None) -> List[Mono]:
    """Variable sets T such that <T> are the minimal primes of <gens>."""
    return minimal_transversals(gens, limit=limit)


def intersect_primes(primes: Iterable[Mono]) -> List[Mono]:
    """Generators of the intersection of the prime ideals <T>, T in primes."""
    out: Optional[List[Mono]] = None
    for T in primes:
        P = [frozenset([v]) for v in T]
        out = P if out is None else ideal_intersection(out, P)
    return out or []


def check_decomposition(gens: Sequence[Mono], primes: Sequence[Mono]) -> bool:
    """Verify  <gens> == intersection of <T> over the given primes."""
    return same_ideal(gens, intersect_primes(primes))


# ----------------------------------------------------------------------------
# Attribute-level ("semantically meaningful") components
# ----------------------------------------------------------------------------
def attribute_components(
    gens: Sequence[Mono], attr_vars: Dict[str, Sequence[str]]
) -> Dict[str, Optional[FrozenSet[str]]]:
    """Minimal primes of <gens> that lie inside a single attribute concept J_l.

    This is the "inductive bias" filter of the preliminaries note: only
    components I with I <= J_l = <A_l> for some attribute l are kept.

    Because each minimal generator is a *pattern* (at most one value per
    attribute), the single-attribute prime <S> contains <gens> iff every
    generator mentions attribute l, and the minimal such S is the set of values
    of l mentioned by the generators.  Returns, per attribute, that set S, or
    None if some generator ignores the attribute (no necessary condition on it).
    """
    out: Dict[str, Optional[FrozenSet[str]]] = {}
    for attr, vars_ in attr_vars.items():
        vs = set(vars_)
        mentioned: Set[str] = set()
        ok = True
        for g in gens:
            hit = g & vs
            if not hit:
                ok = False
                break
            mentioned |= hit
        out[attr] = frozenset(mentioned) if ok and gens else None
    return out


# ----------------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------------
def _selftest(trials: int = 300, seed: int = 0) -> None:
    import random

    rng = random.Random(seed)
    V = [f"x{i}" for i in range(6)]
    for _ in range(trials):
        gens = minimalize(
            frozenset(rng.sample(V, rng.randint(1, 3))) for _ in range(rng.randint(1, 5))
        )
        primes = minimal_primes(gens)
        assert check_decomposition(gens, primes), (gens, primes)
        # every minimal prime must contain the ideal (hit all generators)
        assert all(all(T & g for g in gens) for T in primes)
        # minimality of the primes (antichain)
        assert all(not (a < b) for a in primes for b in primes)
    # Emergency-style example: <a, b> has the single minimal prime (a, b)
    e = [frozenset(["a"]), frozenset(["b"])]
    assert minimal_primes(e) == [frozenset(["a", "b"])]
    print(f"mr_algebra self-test passed ({trials} random squarefree ideals).")


if __name__ == "__main__":
    _selftest()
