"""ACQ: ACE-B BAM inventory (row level, cluster only) -> killcoyne_mm/two_papers_ACQ/bam_inventory.tsv.
Per BAM: batch, kind, size, index present and newer than the BAM, samtools quickcheck, @RG count, lanes (PU), aligner/MarkDuplicates
versions, and existing QC (MarkDuplicates metrics, Picard alignment summary, mosdepth summary). Identifier columns only from the sheet
are read later (tp_acq_manifest.py). No pathology or outcome field is read anywhere."""
import os, re, glob, subprocess, json, pandas as pd, numpy as np
R = "/mnt/scratche/slow/fmlab/zuberi01/phd/aceb_seq"; A = "/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ"
ST = "/mnt/scratche/slow/fmlab/zuberi01/envs/killcoyne_r/bin/samtools"
def picard(f, first=None):
    """Picard metrics table -> list of row dicts."""
    if not f or not os.path.exists(f): return []
    L = [l.rstrip("\n") for l in open(f, errors="replace")]
    try: i = next(k for k, l in enumerate(L) if l and not l.startswith("#") and "\t" in l)
    except StopIteration: return []
    h = L[i].split("\t"); rows = []
    for l in L[i + 1:]:
        if not l.strip() or l.startswith("#"): break
        rows.append(dict(zip(h, l.split("\t"))))
    return rows
def num(x):
    try: return float(x)
    except: return np.nan
rows = []
for b in ["Batch1", "Batch2", "Batch3", "Batch4", "Pilot"]:
    bams = sorted(glob.glob(f"{R}/{b}/Aligned/*.bam") + glob.glob(f"{R}/{b}/AlignOut/Merged/*.bam"))
    for p in bams:
        fn = os.path.basename(p)
        kind = "markdup.dedup" if fn.endswith(".markdup.dedup.bam") else "markdup" if fn.endswith(".markdup.bam") else "pilot_srt" if fn.endswith(".hg38.srt.bam") else "other"
        name = re.sub(r"(\.markdup\.dedup\.bam|\.markdup\.bam|\.hg38\.srt\.bam)$", "", fn)
        st = os.stat(p); bai = [x for x in (p + ".bai", p[:-4] + ".bai") if os.path.exists(x)]
        qc = subprocess.run([ST, "quickcheck", "-v", p], capture_output=True, text=True); hdr = subprocess.run([ST, "view", "-H", p], capture_output=True, text=True).stdout.splitlines()
        rg = [l for l in hdr if l.startswith("@RG")]; pu = set(re.findall(r"\tPU:([^\t]+)", "\n".join(rg))); ids = set(re.findall(r"\tID:([^\t]+)", "\n".join(rg)))
        pg = [l for l in hdr if l.startswith("@PG")]; pgn = sorted(set(re.findall(r"\tPN:([^\t]+)", "\n".join(pg)) + re.findall(r"\tID:([^\t.]+)", "\n".join(pg))))
        vers = {k: (re.search(r"\tVN:([^\t]+)", l).group(1) if re.search(r"\tVN:([^\t]+)", l) else "") for l in pg for k in [re.search(r"\tID:([^\t]+)", l).group(1)]}
        sq = {re.search(r"SN:([^\t]+)", l).group(1): int(re.search(r"LN:(\d+)", l).group(1)) for l in hdr if l.startswith("@SQ")}
        r = dict(batch=b, kind=kind, file=fn, path=p, name=name, bytes=st.st_size, mtime=int(st.st_mtime), has_index=bool(bai), index_path=bai[0] if bai else "",
                 index_newer=bool(bai) and os.stat(bai[0]).st_mtime >= st.st_mtime, quickcheck_ok=(qc.returncode == 0), quickcheck_msg=(qc.stdout + qc.stderr).strip()[:200].replace(p, "<bam>"),
                 n_rg=len(rg), n_rg_id=len(ids), n_pu=len(pu), n_sq=len(sq), chr1_len=sq.get("chr1", sq.get("1")), has_alt=any(k.endswith("_alt") for k in sq),
                 pg=";".join(pgn)[:200], bwa_ver=";".join(sorted(v for k, v in vers.items() if "bwa" in k.lower()))[:60], md_ver=";".join(sorted(v for k, v in vers.items() if "markdup" in k.lower() or "MarkDuplicates" in k))[:60])
        # QC files
        if b == "Pilot":
            q = f"{R}/Pilot"; md = []; [md.extend(picard(f)) for f in glob.glob(f"{q}/AlignOut/MarkDupMetrics/{name.split('_', 1)[-1] if '_SLX' in name else name}*_dedup_metrics.txt")]
            am = picard(f"{q}/AlignOut/{name}.hg38.srt.alignment_metrics.txt"); cov = f"{q}/QC/Aligned/coverage/merged.{name}.hg38.srt.coverage.txt"
            r["pilot_coverage_file"] = os.path.exists(cov); mos = None; mosq = None
        else:
            q = f"{R}/{b}/QC/Aligned/Merged"; base = re.sub(r"\.dedup$", "", name)
            mdf = next((f for f in (f"{q}/{base}.markdup_metrics.txt", f"{q}/{base}.bam.markdup_metrics.txt") if os.path.exists(f)), None); md = picard(mdf)
            am = picard(f"{q}/{base}.alignment_metrics.txt"); mos = f"{q}/{base}.mosdepth.summary.txt"; mosq = f"{q}/{base}.Q40.mosdepth.summary.txt"
            r["fingerprint_vcf"] = next((f for f in (f"{R}/{b}/QC/Aligned/Fingerprints/{base}.markdup.fingerprint.vcf",) if os.path.exists(f)), "")
        if md:
            r["md_rows"] = len(md); r["md_unpaired"] = sum(num(x.get("UNPAIRED_READS_EXAMINED")) for x in md); r["md_pairs"] = sum(num(x.get("READ_PAIRS_EXAMINED")) for x in md)
            r["md_unmapped"] = sum(num(x.get("UNMAPPED_READS")) for x in md); r["md_secsup"] = sum(num(x.get("SECONDARY_OR_SUPPLEMENTARY_RDS")) for x in md)
            r["md_dup_reads"] = sum(num(x.get("UNPAIRED_READ_DUPLICATES")) + 2 * num(x.get("READ_PAIR_DUPLICATES")) for x in md)
            r["md_pct_dup"] = (r["md_dup_reads"] / (r["md_unpaired"] + 2 * r["md_pairs"])) if (r["md_unpaired"] + 2 * r["md_pairs"]) > 0 else np.nan
            r["md_total_reads"] = r["md_unpaired"] + 2 * r["md_pairs"] + r["md_unmapped"]
        pair = [x for x in am if x.get("CATEGORY") == "PAIR"] or [x for x in am if x.get("CATEGORY") == "UNPAIRED"]
        if pair:
            x = pair[0]; r["am_total_reads"] = num(x.get("TOTAL_READS")); r["am_aligned"] = num(x.get("PF_READS_ALIGNED")); r["am_mean_len"] = num(x.get("MEAN_READ_LENGTH"))
            r["am_median_len"] = num(x.get("MEDIAN_READ_LENGTH")); r["am_max_len"] = num(x.get("MAX_READ_LENGTH"))
        for tag, f in (("mos", mos), ("mosq40", mosq)):
            if f and os.path.exists(f):
                for l in open(f):
                    s = l.split("\t")
                    if s[0] == "total": r[f"{tag}_mean"] = num(s[3])
        rows.append(r); print(b, kind, r["quickcheck_ok"], r["has_index"], flush=True)
D = pd.DataFrame(rows); D.to_csv(f"{A}/bam_inventory.tsv", sep="\t", index=False); os.chmod(f"{A}/bam_inventory.tsv", 0o600)
print(D.groupby(["batch", "kind"]).agg(n=("file", "size"), TB=("bytes", lambda x: x.sum() / 1e12), idx=("has_index", "sum"), qc_ok=("quickcheck_ok", "sum")))
print("INVENTORY DONE")
