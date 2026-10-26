"""ACQ: ACE-B sample manifest (row level: killcoyne_mm/two_papers_ACQ/aceb_manifest.tsv, chmod 600) and aggregate JSON
(results/paper_final/two_papers_ACQ/aceb_manifest_summary.json, counts only). Inputs: bam_inventory.tsv (tp_acq_inventory.py),
idxstats of every indexed BAM (run here), modal read length from the first 20,000 primary reads (run here), fingerprint pairs
(tp_acq_fingerprint.py), the sample sheet (columns Batch, Name, PatientID, SLX, SampleID, Mean_Coverage only) and ABD's linkage table
(columns PatientID, participant_id only). No pathology, grade, date, treatment or outcome field is read."""
import os, re, glob, json, subprocess, numpy as np, pandas as pd, networkx as nx
A = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ"; RES = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/results/paper_final/two_papers_ACQ"
ST = "/mnt/scratche/slow/fmlab/zuberi01/envs/killcoyne_r/bin/samtools"; GL = 3088269832; OH_T = float(os.environ.get("OH_T", "0.03")); MIN_INF = 200
os.makedirs(RES, exist_ok=True)
D = pd.read_csv(f"{A}/bam_inventory.tsv", sep="\t")
# ---- per-BAM facts that need samtools (cheap: index lookups and the first reads)
def idx(p):
    r = subprocess.run([ST, "idxstats", p], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip(): return (False, np.nan, np.nan)
    t = [l.split("\t") for l in r.stdout.strip().split("\n")]; return (True, sum(int(x[2]) for x in t), sum(int(x[3]) for x in t))
def rlen(p):
    o = subprocess.run(f"{ST} view -F 0x900 {p} 2>/dev/null | head -20000 | cut -f10", shell=True, capture_output=True, text=True).stdout.split()
    L = np.array([len(x) for x in o]); return (int(np.bincount(L).argmax()), float(L.mean()), int(L.max())) if len(L) else (np.nan, np.nan, np.nan)
D["has_index"] = D.path.map(lambda p: os.path.exists(p + ".bai") or os.path.exists(p[:-4] + ".bai"))
X = D.path.map(lambda p: idx(p) if (os.path.exists(p + ".bai") or os.path.exists(p[:-4] + ".bai")) else (False, np.nan, np.nan))
D["idxstats_ok"] = [x[0] for x in X]; D["idx_mapped"] = [x[1] for x in X]; D["idx_unmapped"] = [x[2] for x in X]
Lr = D.path.map(rlen); D["read_len_mode"] = [x[0] for x in Lr]; D["read_len_mean20k"] = [x[1] for x in Lr]; D["read_len_max"] = [x[2] for x in Lr]
# primary reads: MarkDuplicates examined + unmapped (Picard counts primary records only); idxstats total minus secondary/supplementary as a check
D["primary_reads"] = D.md_total_reads; D["idx_primary_est"] = D.idx_mapped + D.idx_unmapped - D.md_secsup
D["idx_vs_md_match"] = (D.idx_primary_est == D.md_total_reads)
D["nominal_depth"] = D.primary_reads * D.read_len_mode / GL; D["base_depth_meanlen"] = D.primary_reads * D.am_mean_len / GL
D["mapped_reads"] = D.md_unpaired + 2 * D.md_pairs; D["dup_reads"] = D.md_dup_reads
# coverage: mosdepth total mean; else Batch1 depth.txt; else Pilot samtools-coverage (length-weighted over chr1-22, X, Y)
def cov(r):
    if pd.notna(r.get("mos_mean")): return r["mos_mean"], "mosdepth"
    if r.batch == "Batch1":
        f = f"/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_seq/Batch1/QC/Aligned/Merged/{r['name']}.depth.txt"
        if os.path.exists(f):
            try: return float(open(f).read().split()[0]), "depth.txt"
            except Exception: pass
    if r.batch == "Pilot":
        f = f"/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_seq/Pilot/QC/Aligned/coverage/merged.{r['name']}.hg38.srt.coverage.txt"
        if os.path.exists(f):
            c = pd.read_csv(f, sep="\t"); c = c[c["#rname"].isin([f"chr{i}" for i in list(range(1, 23)) + ["X", "Y"]])]
            return float((c.meandepth * (c.endpos - c.startpos + 1)).sum() / (c.endpos - c.startpos + 1).sum()), "samtools_coverage"
    return np.nan, ""
C = D.apply(cov, axis=1); D["mean_coverage"] = [c[0] for c in C]; D["coverage_source"] = [c[1] for c in C]
if D.batch.eq("Pilot").any():   # Pilot MarkDuplicates metrics live in AlignOut/<name>.hg38.srt.alignment_metrics.txt
    for i in D.index[D.batch == "Pilot"]:
        f = f"/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_seq/Pilot/AlignOut/{D.at[i, 'name']}.hg38.srt.alignment_metrics.txt"
        if os.path.exists(f):
            L = [l.rstrip("\n").split("\t") for l in open(f) if l.strip() and not l.startswith("#")]; h = L[0]; rows = [dict(zip(h, x)) for x in L[1:] if len(x) == len(h)]
            g = lambda k: sum(float(x[k]) for x in rows)
            D.at[i, "md_unpaired"] = g("UNPAIRED_READS_EXAMINED"); D.at[i, "md_pairs"] = g("READ_PAIRS_EXAMINED"); D.at[i, "md_unmapped"] = g("UNMAPPED_READS"); D.at[i, "md_secsup"] = g("SECONDARY_OR_SUPPLEMENTARY_RDS")
            D.at[i, "md_dup_reads"] = g("UNPAIRED_READ_DUPLICATES") + 2 * g("READ_PAIR_DUPLICATES"); D.at[i, "md_total_reads"] = D.at[i, "md_unpaired"] + 2 * D.at[i, "md_pairs"] + D.at[i, "md_unmapped"]
            D.at[i, "md_pct_dup"] = D.at[i, "md_dup_reads"] / (D.at[i, "md_unpaired"] + 2 * D.at[i, "md_pairs"])
    D["primary_reads"] = D.md_total_reads; D["mapped_reads"] = D.md_unpaired + 2 * D.md_pairs; D["dup_reads"] = D.md_dup_reads
    D["nominal_depth"] = D.primary_reads * D.read_len_mode / GL; D["idx_primary_est"] = D.idx_mapped + D.idx_unmapped - D.md_secsup; D["idx_vs_md_match"] = (D.idx_primary_est == D.md_total_reads)
# ---- identifiers: sheet (ID, batch, coverage columns only) and ABD link (ID columns only)
sh = pd.read_csv("/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_meta/ACEB_samples_for Rehan.csv", usecols=["Batch", "Name", "PatientID", "SLX", "SampleID", "Mean_Coverage"], dtype=str, encoding_errors="replace")
ab = pd.read_csv(f"{A}/../two_papers_ABD/aceb_db_link.csv", usecols=["PatientID", "participant_id"], dtype=str)
linked = set(ab.loc[ab.participant_id.notna() & (ab.participant_id != ""), "PatientID"])
norm = lambda s: re.sub(r"[_\s]", "", str(s)).upper()
byname = sh.groupby(sh.Name.map(norm)); bysid = sh.groupby(sh.SampleID.map(norm))
def sheet_hit(r):
    if r.batch == "Pilot":
        k = norm(r["name"]); g = bysid.groups.get(k)
        if g is None:   # Pilot pool prefix may differ: match on the barcode suffix within the same SLX pools
            suf = k.split(".", 1)[-1]; g = [i for i in sh.index if norm(sh.SampleID[i]).endswith("." + suf) and any(s in k for s in re.findall(r"SLX-\d+", sh.SampleID[i]))] or None
            return (g, "sampleid_suffix") if g else (None, "")
        return (list(g), "sampleid")
    g = byname.groups.get(norm(re.sub(r"\.dedup$", "", r["name"]))); return (list(g), "name") if g is not None else (None, "")
H = D.apply(sheet_hit, axis=1)
D["in_sheet"] = [h[0] is not None for h in H]; D["sheet_match_by"] = [h[1] for h in H]; D["sheet_rows"] = [len(h[0]) if h[0] else 0 for h in H]
D["sheet_batch"] = [";".join(sorted(set(sh.Batch[h[0]]))) if h[0] else "" for h in H]; D["patient_id"] = [";".join(sorted(set(sh.PatientID[h[0]]))) if h[0] else "" for h in H]
D["sheet_mean_coverage"] = [pd.to_numeric(sh.Mean_Coverage[h[0]], errors="coerce").mean() if h[0] else np.nan for h in H]
D["abd_linked"] = D.patient_id.map(lambda p: p in linked if p else False)
D["name_format"] = D.name.map(lambda s: "PS" if re.match(r"^PS\d{2}-\d+", s) else "99A999999A9" if re.match(r"^\d{2}[A-Z]\d{6}[A-Z]\d", s) else "SLX_barcode" if s.startswith("SLX") else "other")
D["sample_norm"] = D.name.map(lambda s: norm(re.sub(r"\.dedup$", "", s)))
# ---- fingerprints: one profile per BAM key "Batch|name"; prefer the pileup (made from the BAM as it is now), else the VCF
P = pd.read_csv(f"{A}/fp/fp_pairs.tsv", sep="\t"); FS = pd.read_csv(f"{A}/fp/fp_samples.tsv", sep="\t")
src = {}; [src.setdefault(k.split(":", 1)[1], []).append(k) for k in FS.key]
D["fp_key"] = (D.batch + "|" + D.name).map(lambda k: (sorted(src.get(k, []), key=lambda x: not x.startswith("pile"))[:1] or [""])[0])
D.loc[D.kind == "markdup.dedup", "fp_key"] = (D.batch + "|" + D.name.str.replace(r"\.dedup$", "", regex=True)).map(lambda k: (sorted(src.get(k, []), key=lambda x: not x.startswith("pile"))[:1] or [""])[0])
# method check: same BAM with both VCF and pileup
same = P[(P.a.str.split(":", n=1).str[1] == P.b.str.split(":", n=1).str[1]) & (P.a.str[:3] != P.b.str[:3])]
use = set(D.loc[D.kind != "markdup.dedup", "fp_key"]) - {""}
Q = P[P.a.isin(use) & P.b.isin(use) & (P.n_hom_both >= MIN_INF)]
# profile QC: a clean profile matches its own individual (OH < 0.03) and sits near 0.25 against everyone else. Flag profiles with
# < 1,000 sites at depth >= 3, a heterozygous share > 0.5 (possible mixture/contamination), or >= 5 partners at intermediate OH (0.03-0.17).
FS["het_frac"] = FS.n_het / (FS.n_het + FS.n_hom)
mm = pd.concat([Q[["a", "oh"]].rename(columns={"a": "k"}), Q[["b", "oh"]].rename(columns={"b": "k"})])
nmid = mm[(mm.oh >= OH_T) & (mm.oh < 0.17)].groupby("k").size()
FS["n_mid"] = FS.key.map(nmid).fillna(0).astype(int)
FS["fp_flag"] = np.select([FS.n_sites_dp3 < 1000, FS.het_frac > 0.5, FS.n_mid >= 5], ["low_coverage", "high_het", "intermediate_oh"], "")
flagged = set(FS.key[FS.fp_flag != ""])
D["fp_flag"] = D.fp_key.map(dict(zip(FS.key, FS.fp_flag))).fillna("")
D["fp_het_frac"] = D.fp_key.map(dict(zip(FS.key, FS.het_frac))); D["fp_n_mid"] = D.fp_key.map(dict(zip(FS.key, FS.n_mid)))
best = mm.sort_values("oh").groupby("k").head(1).set_index("k").oh; D["fp_min_oh"] = D.fp_key.map(best)
Qc = Q[~Q.a.isin(flagged) & ~Q.b.isin(flagged)]
G = nx.Graph(); G.add_nodes_from(use); G.add_edges_from(Q.loc[Q.oh < OH_T, ["a", "b"]].values.tolist())   # flagged profiles keep their < OH_T links (identity), reported separately
comp = {k: i for i, c in enumerate(nx.connected_components(G)) for k in c}
D["geno_cluster"] = D.fp_key.map(lambda k: comp.get(k, -1))
# ---- aggregates
M = D[D.kind != "markdup.dedup"].copy(); dd = D[D.kind == "markdup.dedup"]
def n5(x): x = int(x); return x if (x == 0 or x >= 5) else "<5"
out = {"generated": pd.Timestamp.now().isoformat(timespec="seconds"), "oh_threshold": OH_T, "min_informative_sites": MIN_INF}
out["bams"] = {f"{b}|{k}": {"n": int(len(x)), "TB": round(x.bytes.sum() / 1e12, 3), "indexed": int(x.has_index.sum()), "idxstats_ok": int(x.idxstats_ok.sum()), "quickcheck_ok": int(x.quickcheck_ok.sum())} for (b, k), x in D.groupby(["batch", "kind"])}
out["per_batch"] = {b: {"n": int(len(x)), "name_format": x.name_format.value_counts().to_dict(), "in_sheet": n5(x.in_sheet.sum()), "abd_linked_patient": n5(x.abd_linked.sum()),
                        "read_groups_median": float(x.n_rg.median()), "read_len_mode": x.read_len_mode.value_counts().head(3).to_dict(), "read_len_mean_median": round(float(x.am_mean_len.median()), 1) if x.am_mean_len.notna().any() else None,
                        "primary_reads_median_M": round(float(x.primary_reads.median()) / 1e6, 1), "pct_dup_median": round(float(x.md_pct_dup.median()) * 100, 1),
                        "mean_coverage_median": round(float(x.mean_coverage.median()), 2), "mean_coverage_range": [round(float(x.mean_coverage.min()), 2), round(float(x.mean_coverage.max()), 2)],
                        "nominal_depth_median": round(float(x.nominal_depth.median()), 2), "nominal_depth_range": [round(float(x.nominal_depth.min()), 2), round(float(x.nominal_depth.max()), 2)],
                        "coverage_source": x.coverage_source.value_counts().to_dict(), "idx_vs_md_match": int(x.idx_vs_md_match.sum()), "fingerprint_vcf": int((x.fingerprint_vcf.fillna("") != "").sum()), "fp_profile": int((x.fp_key != "").sum())}
                    for b, x in M.groupby("batch")}
out["sheet"] = {"rows": int(len(sh)), "names_unique": int(sh.Name.nunique()), "patients": int(sh.PatientID.nunique()), "rows_with_bam": int(sum(any(norm(n) == s for s in M.sample_norm) for n in sh.Name) if False else len(set(sh.Name.map(norm)) & set(M.sample_norm))),
                "sheet_names_without_bam": n5(len(set(sh.Name.map(norm)) - set(M.sample_norm) - set(M.loc[M.batch == 'Pilot', 'sample_norm'])))}
out["redundant_dedup"] = {"n": int(len(dd)), "TB": round(dd.bytes.sum() / 1e12, 3), "truncated": int((~dd.quickcheck_ok).sum()), "truncated_TB": round(dd[~dd.quickcheck_ok].bytes.sum() / 1e12, 3),
                          "bai_TB": round(sum(os.path.getsize(p) for p in dd.index_path.dropna() if isinstance(p, str) and os.path.exists(p)) / 1e12, 4)}
# duplicates: same normalised sample name in more than one BAM (non-dedup), and Pilot <-> sheet sample
dup_names = M.groupby("sample_norm").filter(lambda x: len(x) > 1)
out["same_name_across_batches"] = {"samples": n5(dup_names.sample_norm.nunique()), "bams": n5(len(dup_names)), "batch_pairs": dup_names.groupby("sample_norm").batch.apply(lambda s: "+".join(sorted(s))).value_counts().to_dict()}
pil = M[M.batch == "Pilot"]; out["pilot"] = {"n": int(len(pil)), "matched_to_sheet_sampleid": n5(pil.in_sheet.sum()), "match_by": pil.sheet_match_by.value_counts().to_dict()}
b4 = M[M.batch == "Batch4"]; out["batch4"] = {"n": int(len(b4)), "name_matches_sheet_name": n5(b4.in_sheet.sum()), "name_matches_other_batch_bam": n5(b4.sample_norm.isin(M.loc[M.batch != "Batch4", "sample_norm"]).sum())}
# fingerprint aggregates
oh = Qc.oh.values; out["fingerprint"] = {"profiles": int(len(use)), "flagged_profiles": {k: n5(v) for k, v in FS[FS.key.isin(use)].fp_flag.replace("", "clean").value_counts().items()},
    "flagged_min_oh": [round(float(x), 3) for x in sorted(D.loc[(D.fp_flag != "") & (D.kind != "markdup.dedup"), "fp_min_oh"].dropna())], "pairs_used_clean": int(len(Qc)), "pairs_all": int(len(Q)), "oh_hist_all_0_0.5_by_0.01": np.histogram(Q.oh.values, bins=np.linspace(0, 0.5, 51))[0].tolist(), "pairs_below_threshold": int((oh < OH_T).sum()), "oh_hist_0_0.5_by_0.01": np.histogram(oh, bins=np.linspace(0, 0.5, 51))[0].tolist(),
    "oh_gap": {"max_below": float(oh[oh < OH_T].max()) if (oh < OH_T).any() else None, "min_above": float(oh[oh >= OH_T].min()) if (oh >= OH_T).any() else None},
    "vcf_vs_pileup_same_bam_oh": [round(float(x), 4) for x in same.oh.values], "clusters": int(len(set(comp.values()))), "cluster_size_counts": pd.Series(list(comp.values())).value_counts().value_counts().sort_index().to_dict()}
# genotype vs sheet patient (only BAMs with a sheet patient and a profile)
K = M[(M.patient_id != "") & (M.geno_cluster >= 0)]
pat_split = K.groupby("patient_id").geno_cluster.nunique(); cl_multi = K.groupby("geno_cluster").patient_id.nunique()
out["genotype_vs_sheet"] = {"bams_compared": int(len(K)), "patients_compared": int(K.patient_id.nunique()), "patients_with_>1_bam": int((K.groupby("patient_id").size() > 1).sum()),
    "patients_split_across_genotypes": n5((pat_split > 1).sum()), "genotypes_spanning_>1_sheet_patient": n5((cl_multi > 1).sum()),
    "bams_in_conflict": n5(K[K.patient_id.isin(pat_split[pat_split > 1].index) | K.geno_cluster.isin(cl_multi[cl_multi > 1].index)].shape[0])}
# unlabelled BAMs (no sheet patient): do they share a genotype with a sheet patient?
U = M[(M.patient_id == "") & (M.geno_cluster >= 0)]; lab = set(K.geno_cluster)
out["unlabelled_genotype"] = {b: {"n": int(len(x)), "share_genotype_with_sheet_patient": n5(x.geno_cluster.isin(lab).sum()), "distinct_new_individuals": n5(x.loc[~x.geno_cluster.isin(lab), "geno_cluster"].nunique())} for b, x in U.groupby("batch")}
out["individuals_total"] = int(M.loc[M.geno_cluster >= 0, "geno_cluster"].nunique())
D.to_csv(f"{A}/aceb_manifest.tsv", sep="\t", index=False); os.chmod(f"{A}/aceb_manifest.tsv", 0o600)
json.dump(out, open(f"{RES}/aceb_manifest_summary.json", "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str)); print("MANIFEST DONE")
