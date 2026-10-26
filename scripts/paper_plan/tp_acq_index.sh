#!/usr/bin/env bash
# ACQ: index one ACE-B BAM that lacks a .bai (samtools index into a temporary file, then rename; never overwrites an existing index),
# then verify with samtools idxstats. Writes only <bam>.bai next to the BAM plus a row-level idxstats file in two_papers_ACQ/index/.
set -euo pipefail
BAM=$1; ST=/mnt/scratche/slow/fmlab/zuberi01/envs/killcoyne_r/bin/samtools; A=/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ
K=$(basename "$BAM" .bam); T0=$(date +%s)
if [ -e "$BAM.bai" ] || [ -e "${BAM%.bam}.bai" ]; then echo "index exists, verify only"; else
  $ST index -@ 4 -o "$BAM.bai.acqtmp" "$BAM"; mv -n "$BAM.bai.acqtmp" "$BAM.bai"; fi
$ST idxstats "$BAM" > "$A/index/$K.idxstats" 2> "$A/index/$K.idxstats.err"
echo -e "$K\t$(awk '{m+=$3; u+=$4} END{print m"\t"u"\t"NR}' "$A/index/$K.idxstats")\t$(( $(date +%s) - T0 ))" > "$A/index/$K.done"
echo "INDEX DONE $K"
