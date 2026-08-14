#!/usr/bin/env bash
# Launch the three thesis campaigns as maximally-parallel per-item jobs.
# 1. ERIN UNI2 extraction  — one GPU job per slide (2 offset arrays, cuda partition)
# 2. TCGA-ESCA acquisition — 65 download jobs (epyc) + 65 extraction jobs (cuda, aftercorr)
# 3. OCCAMS fusion v2      — single CPU job (redesigned second pass)
set -uo pipefail
C="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"          # campaigns dir
F="$(dirname "$C")/feasibility"                             # feasibility dir (runner lives here)
ERIN_SLIDES=/mnt/scratche/fast/fmlab/datasets/imaging/ERIN/slides
ERIN_FEAT=/mnt/scratche/fast/fmlab/datasets/imaging/ERIN/features/20x_224px/features_uni_v2
TCGA_DIR=/mnt/scratche/fast/fmlab/datasets/imaging/tcga_esca
mkdir -p "$C/slurm" "$ERIN_FEAT" "$TCGA_DIR/slides" "$TCGA_DIR/features/20x_224px/features_uni_v2"

# --- manifests ---
if [[ ! -s "$C/erin_manifest.txt" ]]; then
  # largest tiff per slide dir = the actual WSI (small ones are macro/label images)
  find "$ERIN_SLIDES" -maxdepth 2 -name "*.tif*" -printf "%s %p\n" 2>/dev/null \
    | awk '{dir=$2; sub(/\/[^\/]+$/,"",dir); if ($1>sz[dir]) {sz[dir]=$1; f[dir]=$2}} END {for (d in f) print f[d]}' \
    | sort > "$C/erin_manifest.txt"
fi
N_ERIN=$(wc -l < "$C/erin_manifest.txt")
echo "ERIN manifest: $N_ERIN slides"

if [[ ! -s "$C/tcga_dl_manifest.csv" ]]; then
  ~/miniforge3/envs/pathology/bin/python - "$F/runs/tcga_esca_smoke/output/esca_slide_files.csv" "$C/tcga_dl_manifest.csv" <<'EOF'
import sys, pandas as pd
df = pd.read_csv(sys.argv[1])
df[df["target_oac"] & df["diagnostic"]].reset_index(drop=True).to_csv(sys.argv[2], index=False)
EOF
fi
N_TCGA=$(($(wc -l < "$C/tcga_dl_manifest.csv") - 1))
echo "TCGA manifest: $N_TCGA slides"

GPUARGS=(--partition=cuda --gres=gpu:1 --time=00:40:00 --cpus-per-task=8 --mem=48G)

# --- 1. ERIN extraction: two offset arrays (MaxArraySize=2001 < N) ---
HALF=1500
sbatch --job-name=erin_x_a "${GPUARGS[@]}" --array=0-$((HALF<N_ERIN?HALF-1:N_ERIN-1)) \
  --output="$C/slurm/erin_x_a_%A_%a.out" --error="$C/slurm/erin_x_a_%A_%a.err" \
  --export=ALL,OFFSET=0 \
  --wrap="source ~/miniforge3/etc/profile.d/conda.sh && conda activate erin && python $C/extract_one.py --manifest $C/erin_manifest.txt --outdir $ERIN_FEAT --name-from dir"
if (( N_ERIN > HALF )); then
sbatch --job-name=erin_x_b "${GPUARGS[@]}" --array=0-$((N_ERIN-HALF-1)) \
  --output="$C/slurm/erin_x_b_%A_%a.out" --error="$C/slurm/erin_x_b_%A_%a.err" \
  --export=ALL,OFFSET=$HALF \
  --wrap="source ~/miniforge3/etc/profile.d/conda.sh && conda activate erin && python $C/extract_one.py --manifest $C/erin_manifest.txt --outdir $ERIN_FEAT --name-from dir"
fi

# --- 2. TCGA: downloads then element-wise dependent extraction ---
DL=$(sbatch --parsable --job-name=tcga_dl --partition=epyc --array=0-$((N_TCGA-1)) \
  --time=00:45:00 --cpus-per-task=2 --mem=4G \
  --output="$C/slurm/tcga_dl_%A_%a.out" --error="$C/slurm/tcga_dl_%A_%a.err" \
  --wrap="source ~/miniforge3/etc/profile.d/conda.sh && conda activate pathology && python $C/download_one.py $C/tcga_dl_manifest.csv $TCGA_DIR/slides")
echo "tcga download array: $DL"
# extraction manifest = expected slide paths in manifest order
~/miniforge3/envs/pathology/bin/python - "$C/tcga_dl_manifest.csv" "$TCGA_DIR/slides" "$C/tcga_extract_manifest.txt" <<'EOF'
import sys, pandas as pd
df = pd.read_csv(sys.argv[1])
open(sys.argv[3], "w").write("\n".join(f"{sys.argv[2]}/{n}" for n in df["file_name"]) + "\n")
EOF
sbatch --job-name=tcga_x "${GPUARGS[@]}" --array=0-$((N_TCGA-1)) --dependency=aftercorr:$DL \
  --output="$C/slurm/tcga_x_%A_%a.out" --error="$C/slurm/tcga_x_%A_%a.err" \
  --export=ALL,OFFSET=0 \
  --wrap="source ~/miniforge3/etc/profile.d/conda.sh && conda activate erin && python $C/extract_one.py --manifest $C/tcga_extract_manifest.txt --outdir $TCGA_DIR/features/20x_224px/features_uni_v2 --name-from file"

# --- 3. OCCAMS fusion v2 (race-to-run runner) ---
for p in epyc cuda; do
  sbatch --job-name=occams_fus2_$p --partition=$p --time=02:00:00 --cpus-per-task=8 --mem=48G \
    --output="$C/slurm/occams_fus2_${p}_%j.out" --error="$C/slurm/occams_fus2_${p}_%j.err" \
    --export=ALL,TASK_NAME=occams_fusion2,TASK_CMD="python $C/task_occams_fusion2.py",CONDA_ENV=pathology \
    --wrap="bash $F/run_task.sh"
done
echo "all campaigns submitted"
