"""ACQ fingerprints, step B: REF/ALT read counts at the fingerprint sites for one BAM with samtools mpileup (no reference; default
filters: unmapped, secondary, QC-fail and duplicate reads excluded, base quality >= 13; reads fetched through the index), for BAMs without a fingerprint VCF (and a few
with one, as a method check). usage: tp_acq_fp_pileup.py BAM KEY"""
import sys, subprocess, re, os, numpy as np, pandas as pd
bam, key = sys.argv[1], sys.argv[2]; O = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ/fp"
ST = "/mnt/scratche/slow/fmlab/zuberi01/envs/killcoyne_r/bin/samtools"
S = pd.read_csv(f"{O}/fp_sites.tsv", sep="\t"); idx = {(c, p): i for i, (c, p) in enumerate(zip(S.chrom, S.pos))}
rc = np.zeros(len(S), np.int16); ac = np.zeros(len(S), np.int16)
# indexed BAM: samtools view -M -L jumps to the sites through the index; mpileup then piles up only those reads
p = subprocess.Popen(f"{ST} view -u -M -L {O}/fp_sites.bed {bam} | {ST} mpileup -l {O}/fp_sites.bed -d 250 -", shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
for l in p.stdout:
    f = l.split("\t"); i = idx.get((f[0], int(f[1])))
    if i is None: continue
    b = re.sub(r"\^.", "", f[4]); b = re.sub(r"[$]", "", b)
    # drop indel annotations +n/-n followed by n bases
    out = []; j = 0
    while j < len(b):
        if b[j] in "+-":
            m = re.match(r"[+-](\d+)", b[j:]); j += len(m.group(0)) + int(m.group(1)); continue
        out.append(b[j]); j += 1
    b = "".join(out).upper(); rc[i] = b.count(S.ref[i]); ac[i] = b.count(S.alt[i])
p.wait(); safe = re.sub(r"[^A-Za-z0-9_.-]", "_", key)
np.savez_compressed(f"{O}/pile_{safe}.npz", key=key, ref=rc, alt=ac, rc=p.returncode); os.chmod(f"{O}/pile_{safe}.npz", 0o600)
print("PILEUP DONE", (rc + ac >= 3).sum(), "sites with depth>=3")
