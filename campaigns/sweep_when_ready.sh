#!/usr/bin/env bash
T=/mnt/scratche/slow/fmlab/zuberi01/phd/thesis
for try in $(seq 1 300); do
  for enc in virchow2 gigapath phikon2 hoptimus0 hoptimus1; do
    n=$(ls /mnt/scratche/fast/fmlab/datasets/imaging/ERIN/features/20x_224px/features_$enc/*.h5 2>/dev/null | wc -l)
    marker=$T/feasibility/runs/erin_ch3_$enc
    if [ "$n" -ge 2270 ] && [ ! -d "$marker" ]; then
      sbatch --job-name=ch3sw_$enc --partition=cuda --gres=gpu:1 --time=24:00:00 --cpus-per-task=8 --mem=96G \
        -o $T/campaigns/slurm/ch3sw_${enc}_%j.out -e $T/campaigns/slurm/ch3sw_${enc}_%j.err \
        --export=ALL,FEAT_SUB=features_$enc,TASK_NAME=erin_ch3_$enc,TASK_CMD="python $T/scripts/task_erin_ch3.py",CONDA_ENV=erin \
        --wrap="bash $T/feasibility/run_task.sh" && echo "submitted ch3 sweep for $enc"
    fi
  done
  sleep 1800
done
