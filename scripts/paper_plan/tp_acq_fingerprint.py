"""ACQ fingerprints, step C: genotype identity across all ACE-B BAMs from REF/ALT read counts at the fingerprint SNP sites
(existing VCFs, tp_acq_fp_sites.py; samtools mpileup for BAMs without a VCF, tp_acq_fp_pileup.py).
Metric: opposite-homozygote rate (OH) = share of sites, among those called homozygous in both samples (>= 3 reads, all REF or all ALT),
where one is homozygous REF and the other homozygous ALT. Same individual -> ~0 (sequencing error only; LOH cannot turn REF/REF into
ALT/ALT); different individuals -> about 2pq-weighted, typically > 0.1. Row-level output: fp/fp_pairs.tsv, fp/fp_samples.tsv."""
import glob, os, numpy as np, pandas as pd, json
O = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ/fp"; DMIN = 3
v = np.load(f"{O}/fp_vcf_counts.npz"); keys = [f"vcf:{k}" for k in v["keys"]]; R = [v["ref"].astype(np.int32)]; Al = [v["alt"].astype(np.int32)]
for f in sorted(glob.glob(f"{O}/pile_*.npz")):
    p = np.load(f); keys.append(f"pile:{p['key']}"); R.append(p["ref"][None].astype(np.int32)); Al.append(p["alt"][None].astype(np.int32))
R = np.vstack(R); Al = np.vstack(Al); n = len(keys); print("profiles", n)
HR = ((R >= DMIN) & (Al == 0)).astype(np.float32); HA = ((Al >= DMIN) & (R == 0)).astype(np.float32); H = HR + HA
both = H @ H.T; opp = HR @ HA.T + HA @ HR.T; oh = np.where(both > 0, opp / np.maximum(both, 1), np.nan)
iu = np.triu_indices(n, 1)
P = pd.DataFrame({"a": np.array(keys)[iu[0]], "b": np.array(keys)[iu[1]], "n_hom_both": both[iu].astype(int), "oh": oh[iu]})
P.to_csv(f"{O}/fp_pairs.tsv", sep="\t", index=False); os.chmod(f"{O}/fp_pairs.tsv", 0o600)
S = pd.DataFrame({"key": keys, "n_sites_dp3": ((R + Al) >= DMIN).sum(1), "n_hom": H.sum(1).astype(int), "n_het": (((R >= 1) & (Al >= 1)) & ((R + Al) >= DMIN)).sum(1)})
S.to_csv(f"{O}/fp_samples.tsv", sep="\t", index=False); os.chmod(f"{O}/fp_samples.tsv", 0o600)
h, e = np.histogram(P.oh.dropna(), bins=np.linspace(0, 0.5, 51)); print("OH histogram (0..0.5 by 0.01):", h.tolist())
print("informative sites per pair: median", int(P.n_hom_both.median()), "min", int(P.n_hom_both.min())); print("FINGERPRINT DONE")
