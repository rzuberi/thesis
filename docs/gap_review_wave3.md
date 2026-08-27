# Wave-3 gap review verdict (2026-08-27)

Six frontier families read the complete results corpus (~40 result files) and
answered only: what compute is missing before writing? Raw:
review/gapreview_*.json. Grok-4.6: ZERO gaps. Qwen3.8-Max: one. Four families
converged on a finite closure list — almost entirely our own declared items:

BLOCKING (converged):
1. 1.21 progression v2-vs-v3 reconciliation (5/6) — CPU join + audit table.
2. Encoder sweep on OCCAMS v3 + TCGA-OAC survival (4/6) — pre-registered tasks
   never swept; requires 4-encoder extraction (~720 slides) then downstream.
3. 1.20 50-perm nulls for flagged controls + final-pipeline permutation
   controls for tcga_abmil and ERIN progression (4/6).
4. Holm computation over the 4 confirmatory contrasts (2/6) — trivial, declared
   in multiplicity_plan.md, never run.
5. Patient-level aggregation for ERIN grade metrics (Terra-Pro sev-5) — the
   frozen protocol says patient-level; slide-level was reported. Recompute
   from saved OOF.

NON-BLOCKING (recorded, not gating): seed-repetition uncertainty on central
contrasts; SWG jury rerun (2.14); TCGA label-source replication; encoder-mix
stage (or record as deviation); report-slide disagreement analysis.

GATE DECISION: compute is NOT closed until items 1-5 are done. All five are
mapped to jobs the same day. Writing starts when they land.
