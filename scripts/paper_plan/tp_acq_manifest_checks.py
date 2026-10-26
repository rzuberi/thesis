"""ACQ: extra aggregate checks on the row-level manifest (index vs MarkDuplicates totals, Pilot twins, fingerprint flags, Batch4 genotype links); prints batch-level counts only."""
import pandas as pd, numpy as np
A="/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ"
D=pd.read_csv(f"{A}/aceb_manifest.tsv",sep="\t",dtype={"patient_id":str}); D.patient_id=D.patient_id.fillna("")
M=D[D.kind!="markdup.dedup"].copy()
x=M[~M.idx_vs_md_match.astype(bool)]; print("idx/md mismatch", x[["batch","idx_primary_est","md_total_reads","index_newer","mtime"]].assign(diff=x.idx_primary_est-x.md_total_reads).drop(columns="mtime").to_string(index=False))
print("index older than BAM by batch", M.groupby("batch").index_newer.apply(lambda s:(~s.astype(bool)).sum()).to_dict())
p=M[M.batch=="Pilot"]; print("pilot sheet batch", p.sheet_batch.value_counts().to_dict())
# does the pilot's sheet sample also have a batch BAM?
names=set(M.loc[M.batch!="Pilot","sample_norm"])
sh=pd.read_csv("/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_meta/ACEB_samples_for Rehan.csv",usecols=["Name","SampleID"],dtype=str)
norm=lambda s: str(s).replace("_","").replace(" ","").upper()
sid2name=dict(zip(sh.SampleID.map(norm),sh.Name.map(norm)))
pn=p.sample_norm.map(lambda k: sid2name.get(k))
print("pilot with sheet name that has a batch BAM", pn.isin(names).sum(), "of", len(p))
# genotype: pilot cluster shared with batch BAM of same sample name
for i,r in p.iterrows():
    pass
bm=M[M.batch!="Pilot"].set_index("sample_norm").geno_cluster
same=[(bm.get(n)==g) if n in bm.index else None for n,g in zip(pn,p.geno_cluster)]
print("pilot genotype equals its batch twin", pd.Series(same).value_counts(dropna=False).to_dict())
# Batch2/Batch3 same-name pair genotype
dn=M.groupby("sample_norm").filter(lambda x: len(x)>1); print("same-name pair clusters", dn.groupby("sample_norm").geno_cluster.nunique().to_dict().values())
print("flagged", M[M.fp_flag.fillna("")!=""][["batch","fp_flag","fp_het_frac","fp_n_mid","fp_min_oh","mean_coverage"]].to_string(index=False))
# conflicts
K=M[(M.patient_id!="")&(M.geno_cluster>=0)]
ps=K.groupby("patient_id").geno_cluster.nunique(); bad=ps[ps>1].index
print("split patients", len(bad), K[K.patient_id.isin(bad)][["batch","geno_cluster","fp_flag","fp_min_oh","name_format"]].to_string(index=False))
# singletons
cs=M.groupby("geno_cluster").size(); sing=M[M.geno_cluster.map(cs)==1]
print("singleton clusters by batch", sing.batch.value_counts().to_dict(), "with sheet patient", (sing.patient_id!="").sum())
# patients' BAM counts and sample counts
print("BAMs per sheet patient", K.groupby("patient_id").size().value_counts().sort_index().to_dict())
# batch4 new individuals sizes
b4=M[M.batch=="Batch4"]; lab=set(K.geno_cluster); new=b4[~b4.geno_cluster.isin(lab)]
print("batch4 new individuals cluster sizes", new.groupby("geno_cluster").size().value_counts().to_dict())
print("batch4 known: distinct sheet patients", K[K.geno_cluster.isin(b4.geno_cluster)].patient_id.nunique(), "abd-linked", K[K.geno_cluster.isin(b4.geno_cluster)].drop_duplicates("patient_id").abd_linked.sum())
# Batch3 abd
print("batch3 patients", K[K.batch=="Batch3"].patient_id.nunique(), "patients also in other batches", K[K.batch=="Batch3"].patient_id.isin(K[K.batch!="Batch3"].patient_id).sum())
print("sheet patients abd linked", K.drop_duplicates("patient_id").abd_linked.sum(), "of", K.patient_id.nunique())
print("dup name sheet rows", sh.Name.map(norm).duplicated().sum())
print("sheet Mean_Coverage vs mosdepth corr", M[["sheet_mean_coverage","mean_coverage"]].corr().iloc[0,1].round(3), "n", M.sheet_mean_coverage.notna().sum(), "median ratio", (M.mean_coverage/M.sheet_mean_coverage).median().round(3))
print("nominal<0.4", (M.nominal_depth<0.4).sum(), "nominal<1", (M.nominal_depth<1).sum(), "cov<1", (M.mean_coverage<1).sum())
print("read len mean by batch", M.groupby("batch").read_len_mean20k.median().round(1).to_dict())
print("ratio mode/mean len", (M.read_len_mode/M.read_len_mean20k).median().round(3))
print("total nondedup TB", round(M.bytes.sum()/1e12,3), "max GB", round(M.bytes.max()/1e9,1), "median GB", round(M.bytes.median()/1e9,1))
