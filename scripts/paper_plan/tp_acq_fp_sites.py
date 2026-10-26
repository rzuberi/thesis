"""ACQ fingerprints, step A: parse the existing per-sample fingerprint VCFs (bcftools mpileup -T SNP bed) into per-site REF/ALT read
counts; build the union site list with REF and the most common ALT across samples (fp_sites.tsv, fp_sites.bed for samtools mpileup).
Row-level output in killcoyne_mm/two_papers_ACQ/fp/."""
import glob, os, re, collections, numpy as np, pandas as pd
R = "/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_seq"; O = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ/fp"
os.makedirs(O, exist_ok=True)
vcfs = sorted(glob.glob(f"{R}/Batch*/QC/Aligned/Fingerprints/*.fingerprint.vcf")); print("vcfs", len(vcfs))
per = {}; refs = {}; altc = collections.defaultdict(collections.Counter)
for v in vcfs:
    b = v.split("/")[-5]; s = os.path.basename(v).replace(".markdup.fingerprint.vcf", ""); d = {}
    for l in open(v):
        if l[0] == "#": continue
        f = l.rstrip("\n").split("\t"); k = (f[0], int(f[1])); refs[k] = f[3]
        alts = [] if f[4] == "." else f[4].split(","); fmt = f[8].split(":"); val = f[9].split(":")
        if "AD" not in fmt: continue
        ad = [int(x) if x != "." else 0 for x in val[fmt.index("AD")].split(",")]
        d[k] = dict(zip([f[3]] + alts, ad))
        for a, c in zip(alts, ad[1:]):
            if a != "<*>" and len(a) == 1 and c > 0: altc[k][a] += 1
    per[f"{b}|{s}"] = d
sites = sorted(refs, key=lambda k: (k[0], k[1]))
S = pd.DataFrame({"chrom": [k[0] for k in sites], "pos": [k[1] for k in sites], "ref": [refs[k] for k in sites], "alt": [altc[k].most_common(1)[0][0] if altc[k] else "" for k in sites]})
S = S[(S.ref.str.len() == 1) & (S.alt != "")].reset_index(drop=True); print("sites with an observed SNV alt", len(S))
S.to_csv(f"{O}/fp_sites.tsv", sep="\t", index=False); S.assign(s=S.pos - 1)[["chrom", "s", "pos"]].to_csv(f"{O}/fp_sites.bed", sep="\t", header=False, index=False)
idx = {(c, p): i for i, (c, p) in enumerate(zip(S.chrom, S.pos))}; keys = sorted(per)
RC = np.zeros((len(keys), len(S)), np.int16); AC = np.zeros_like(RC)
for j, kk in enumerate(keys):
    for k, d in per[kk].items():
        i = idx.get(k)
        if i is None: continue
        RC[j, i] = d.get(S.ref[i], 0); AC[j, i] = d.get(S.alt[i], 0)
np.savez_compressed(f"{O}/fp_vcf_counts.npz", keys=np.array(keys), ref=RC, alt=AC); os.chmod(f"{O}/fp_vcf_counts.npz", 0o600)
print("median sites with depth>=3 per sample", int(np.median(((RC + AC) >= 3).sum(1)))); print("FP SITES DONE")
