#!/bin/bash
#SBATCH -p epyc -c 16 --mem=64G -t 03:00:00 -J x_clf_tfidf -o /mnt/scratche/slow/fmlab/zuberi01/analysis/rl_explore/clf/tfidf_%j.log
source ~/miniforge3/etc/profile.d/conda.sh; conda activate pathology
cd /mnt/scratche/slow/fmlab/zuberi01/phd/thesis/scripts/rl/explore/clf && OMP_NUM_THREADS=16 python -u tfidf.py
