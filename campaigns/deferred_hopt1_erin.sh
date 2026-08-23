#!/usr/bin/env bash
# waits for queue room, then submits the two hoptimus1 ERIN extraction arrays
DEP=$(squeue -u zuberi01 -h -n dl_hopt1 -o %i | head -1)
[ -z "$DEP" ] && DEP_OPT="" || DEP_OPT="--dependency=afterok:$DEP"
SRC="source ~/miniforge3/etc/profile.d/conda.sh && conda activate virchow2"
for try in $(seq 1 200); do
  ok=0
  for spec in "ea 0-1499%20 0" "eb 0-780%20 1500"; do set -- $spec
    name=x3_hoptimus1_$1
    squeue -u zuberi01 -h -n $name | grep -q . && { ok=$((ok+1)); continue; }
    if sbatch --job-name=$name --partition=cuda --gres=gpu:1 --array=$2 $DEP_OPT --time=00:30:00 --cpus-per-task=8 --mem=48G \
      -o /mnt/scratche/slow/fmlab/zuberi01/phd/thesis/campaigns/slurm/${name}_%A_%a.out \
      -e /mnt/scratche/slow/fmlab/zuberi01/phd/thesis/campaigns/slurm/${name}_%A_%a.err \
      --export=ALL,OFFSET=$3,ENCODER=hoptimus1 \
      --wrap="$SRC && python /mnt/scratche/slow/fmlab/zuberi01/phd/thesis/scripts/extract_one_hf.py --manifest /mnt/scratche/slow/fmlab/zuberi01/phd/thesis/campaigns/erin_manifest.txt --outdir /mnt/scratche/fast/fmlab/datasets/imaging/ERIN/features/20x_224px/features_hoptimus1"; then
      echo "submitted $name"; ok=$((ok+1))
    fi
  done
  [ "$ok" -ge 2 ] && echo "both in" && exit 0
  sleep 1800
done
