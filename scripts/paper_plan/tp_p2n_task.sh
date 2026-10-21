#!/bin/bash
# Two papers, agent P2N: one campaign task of the selection-aware null (docs/two_papers_P2N.md).
#   tp_p2n_task.sh a SHUF            full refit of L-IMG and L-CNV under permutation SHUF (4 Rscript processes in parallel), then the rule search (MODE a)
#   tp_p2n_task.sh b KIND S1 [S2..]  rule search on stored predictions (MODE b) for each listed permutation of kind free|strat
# Must run inside the erin python environment (campaign conda_env column); R comes from the killcoyne_r environment by absolute path.
set -euo pipefail
PP=/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/scripts/paper_plan; RS=/mnt/scratche/slow/fmlab/zuberi01/envs/killcoyne_r/bin/Rscript
MODE=$1; shift
if [ "$MODE" = a ]; then
  S=$1; pids=()
  for spec in "img 1-5" "img 6-10" "cnv 1-5" "cnv 6-10"; do set -- $spec; SHUF=$S MODEL=$1 REPS=$2 $RS $PP/tp_p2n_refit.R & pids+=($!); done
  for p in "${pids[@]}"; do wait $p; done
  TASK=search SHUF=$S MODE=a KIND=free python $PP/tp_p2n_search.py
else
  KIND=$1; shift
  for S in "$@"; do TASK=search SHUF=$S MODE=b KIND=$KIND python $PP/tp_p2n_search.py; done
fi
