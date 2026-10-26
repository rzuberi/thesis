#!/usr/bin/env bash
# ACQ: bin one BAM into the discovery hg38 50 kb QDNAseq bins (61,775 bins from a discovery 50.QDNAseq.RData), at native depth and
# downsampled to fixed nominal depths. Counting rule = QDNAseq 1.38/1.42 binReadCounts with the discovery generator's options
# (minMapq 37, isUnmappedQuery FALSE, isNotPassingQualityControls FALSE, isDuplicate FALSE, secondary/supplementary not filtered):
# a record counts in the bin holding its leftmost 1-based position (POS). Implemented as samtools view | awk.
# Nominal depth = primary reads (flag & 0x900 == 0, unmapped and duplicates included) x modal read length / 3,088,269,832.
# Downsampling: samtools view --subsample F --subsample-seed S (read-name hash, mates kept together), applied to all records before the filters.
# usage: tp_acq_count.sh BAM OUTDIR KEY "0.4 0.29" SEED [THREADS]   (registration: seed 1, i.e. samtools view -s 1.<fraction>; seeds 2-5 for the ICC only)
set -euo pipefail
BAM=$1; OUT=$2; KEY=$3; TARGETS=${4:-"0.4 0.29"}; SEED=${5:-1}; TH=${6:-4}
ST=/mnt/scratche/slow/fmlab/zuberi01/envs/killcoyne_r/bin/samtools
BINS=/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ/disc_bins_hg38_50kb.tsv
GL=3088269832
mkdir -p "$OUT"; T0=$(date +%s)
# awk binner: reads "flag rname pos mapq" lines; prints primary-record count, counted records, then one count per bin in bin order
BINAWK='BEGIN{FS="\t"; while((getline l < B)>0){ split(l,a,"\t"); if(a[1]=="location") continue; n++; ch[n]=a[2]; st[n]=a[3]; key=a[2]":"int((a[3]-1)/50000); ok[key]=1 } }
{ f=$1; if (and(f,2304)==0) prim++; if (and(f,1540)!=0 || $4<37) next; c=$2; sub(/^chr/,"",c); k=c":"int(($3-1)/50000); if (k in ok) { cnt[k]++; used++ } else other++ }
END{ print "#primary\t" prim+0; print "#counted\t" used+0; print "#offbin\t" other+0; for(i=1;i<=n;i++){ k=ch[i]":"int((st[i]-1)/50000); print cnt[k]+0 } }'
# header facts
$ST view -H "$BAM" > "$OUT/header.txt"
RG=$(grep -c '^@RG' "$OUT/header.txt" || true); CHR1=$(awk -F'\t' '$1=="@SQ"{for(i=2;i<=NF;i++){if($i=="SN:chr1"||$i=="SN:1"){for(j=2;j<=NF;j++) if($j~/^LN:/) print substr($j,4)}}}' "$OUT/header.txt" | head -1)
RL=$($ST view -F 0x900 "$BAM" 2>/dev/null | head -20000 | awk -F'\t' '{print length($10)}' | sort -n | uniq -c | sort -k1,1nr | head -1 | awk '{print $2}' || true)
# native pass: all records -> awk (needs gawk 'and'); gawk check
AWK=$(command -v gawk || echo awk)
t1=$(date +%s)
$ST view -@ $TH "$BAM" | cut -f2-5 | $AWK -v B="$BINS" "$BINAWK" > "$OUT/native.cnt"
t2=$(date +%s)
PRIM=$(awk -F'\t' '$1=="#primary"{print $2}' "$OUT/native.cnt"); NOM=$(awk -v p=$PRIM -v l=$RL -v g=$GL 'BEGIN{printf "%.6f", p*l/g}')
echo -e "key\t$KEY\nbam_bytes\t$(stat -c %s "$BAM")\nread_groups\t$RG\nchr1_len\t$CHR1\nread_len_mode\t$RL\nprimary_reads\t$PRIM\nnominal_depth\t$NOM\nseed\t$SEED\nnative_secs\t$((t2-t1))" > "$OUT/stats.tsv"
for tg in $TARGETS; do
  [ "$tg" = none ] && continue
  FR=$(awk -v t=$tg -v d=$NOM 'BEGIN{f=t/d; if (f>=1) print "NA"; else printf "%.8f", f}')
  tag=$(awk -v t=$tg 'BEGIN{printf "d%.2f", t}' | tr . p)
  if [ "$FR" = NA ]; then echo -e "${tag}_fraction\tNA (native below target)" >> "$OUT/stats.tsv"; continue; fi
  t1=$(date +%s)
  $ST view -@ $TH --subsample $FR --subsample-seed $SEED "$BAM" | cut -f2-5 | $AWK -v B="$BINS" "$BINAWK" > "$OUT/$tag.cnt"
  t2=$(date +%s)
  P2=$(awk -F'\t' '$1=="#primary"{print $2}' "$OUT/$tag.cnt")
  echo -e "${tag}_target\t$tg\n${tag}_fraction\t$FR\n${tag}_primary_reads\t$P2\n${tag}_realised_depth\t$(awk -v p=$P2 -v l=$RL -v g=$GL 'BEGIN{printf "%.6f", p*l/g}')\n${tag}_secs\t$((t2-t1))" >> "$OUT/stats.tsv"
done
# write QDNAseq-style raw count tables (location chrom start end KEY), gzip
for c in "$OUT"/*.cnt; do b=$(basename $c .cnt)
  awk -F'\t' '$1=="#counted"{print "'${b}'_counted\t"$2} $1=="#offbin"{print "'${b}'_offbin\t"$2}' $c >> "$OUT/stats.tsv"
  paste <(cut -f1-4 "$BINS" | sed "1s/.*/location\tchrom\tstart\tend/") <(echo "$KEY"; grep -v '^#' $c) | gzip -n > "$OUT/50.raw_read_counts.$b.txt.gz"; rm $c
done
echo -e "total_secs\t$(( $(date +%s) - T0 ))\nout_bytes\t$(du -cb "$OUT"/*.gz | tail -1 | cut -f1)" >> "$OUT/stats.tsv"
echo "COUNT DONE $KEY"
