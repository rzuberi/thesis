#!/usr/bin/env bash
# ACQ smoke: pick one BAM per batch (Batch1-4 markdup incl. one 99A999999A9-format name in Batch3, one Pilot) with a fixed seed, and
# count each at native depth and at 0.4x and 0.29x nominal (tp_acq_count.sh) as one Slurm job per BAM; sacct gives memory afterwards.
A=/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ
~/miniforge3/envs/erin/bin/python - <<'PY' > $A/smoke/picks.tsv
import pandas as pd, numpy as np, re
d = pd.read_csv("/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ/bam_inventory.tsv", sep="\t")
d = d[(d.kind != "markdup.dedup") & d.quickcheck_ok]; rs = np.random.RandomState(0); out = []
for b in ["Batch1", "Batch2", "Batch3", "Batch4", "Pilot"]:
    x = d[d.batch == b]
    if b == "Batch3": x = x[x.name.str.match(r"^\d{2}[A-Z]\d{6}[A-Z]\d$")]
    r = x.iloc[rs.randint(len(x))]; out.append((f"smoke_{b}", r.path))
for k, p in out: print(f"{k}\t{p}")
PY
while IFS=$'\t' read -r key bam; do
  sbatch -p epyc -c 8 --mem 16G -t 4:00:00 -J tpacq_smoke -o $A/logs/smoke_${key}_%j.log \
    --wrap="bash $A/scripts/tp_acq_count.sh '$bam' $A/smoke/$key $key '0.4 0.29' 1 6"
done < $A/smoke/picks.tsv
