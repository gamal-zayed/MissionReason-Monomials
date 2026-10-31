# Stage 1: MissionReason expert policy as monomial concepts

Run (needs numpy; Python >= 3.9):

    python mr_algebra.py                                   # self-test of the ideal toolkit
    python region_analysis.py --repo /path/to/mission-reason --out results
    python sweep.py /path/to/mission-reason                # discretization sensitivity

`region_analysis.py` imports `optimization_rules.py` and `scenarios.py` from your repo
unchanged. Nothing in the repo is modified.

Scope notes
- Decision regions are computed on PURE cells only (cells where the policy returns one action
  everywhere inside). MIXED cells are reported separately as abstraction error.
- `remaining_pass_time` is ignored: the policy never reads it.
- Necessary conditions / minimal primes describe the pure-cell abstraction, not every raw input.
