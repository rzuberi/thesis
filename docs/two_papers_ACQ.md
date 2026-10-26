# Two papers, agent ACQ: ACE-B sequencing — counting smoke test, BAM indexing, sample manifest

26 October 2026. Rules: `paper/two_papers/RUN_RULES.md`, with the authorised exception for the ACE-B sequencing files in `aceb_seq/` under outcome blinding. Aggregates only; cells of 1–4 are "<5". No sample ID appears here.

**Blinding.** No pathology, histology, diagnosis, grade, progression, treatment or outcome field was read from any file or database. From the sample sheet only `Batch`, `Name`, `PatientID`, `SLX`, `SampleID` and `Mean_Coverage` were read (pandas `usecols`, after reading the header line). From ABD's linkage table only `PatientID` and `participant_id` were read. No model scored anything and no segmentation was run. Only read counts were produced.

## Plan

1. Take the discovery hg38 50 kb bins from a discovery `50.QDNAseq.RData` and the parameters stored with them. Re-count discovery BAMs and compare bin by bin with the stored `50.raw_read_counts.txt`.
2. Count 5 ACE-B BAMs (one from each of Batch1–4 and the Pilot; the Batch3 one with a `99A999999A9`-format name) at native depth, 0.4× and 0.29× nominal. Record time, memory, size and reads used, and estimate the full run.
3. Index every BAM that lacks a `.bai` (one Slurm job each) and verify each index with `samtools idxstats`.
4. Build the manifest: QC metrics, sheet and ABD linkage (ID columns only), and genotype identity from the fingerprint SNPs.

## How it was run

- Scripts (`scripts/paper_plan/`):
  - `tp_acq_disc_probe.R`: reads the bins and options from the discovery RData.
  - `tp_acq_disc_validate.R`: re-counts discovery BAMs with QDNAseq and compares with the stored counts.
  - `tp_acq_count.sh`: the counter. One run per BAM gives native, 0.4× and 0.29× nominal.
  - `tp_acq_smoke_submit.sh`, `tp_acq_smoke_summary.py`: smoke submission and summary.
  - `tp_acq_inventory.py`: BAM inventory.
  - `tp_acq_index.sh`: indexing and verification.
  - `tp_acq_fp_sites.py`, `tp_acq_fp_pileup.py`, `tp_acq_fingerprint.py`: fingerprints.
  - `tp_acq_manifest.py`, `tp_acq_manifest_checks.py`: manifest and extra checks.
- Tools: samtools 1.24, QDNAseq 1.42 and R from `/mnt/scratche/slow/fmlab/zuberi01/envs/killcoyne_r` (used read-only).
- Slurm: `tpacq_*` jobs plus the campaigns `tpacqidx` (69 index tasks) and `tpacqfp` (82 pileup tasks), all on epyc.
- Outputs:
  - Row-level, on the cluster only (chmod 600/700): `killcoyne_mm/two_papers_ACQ/`. This holds `aceb_manifest.tsv`, `bam_inventory.tsv`, `fp/`, `smoke/` and `disc_val/`.
  - Aggregates: `results/paper_final/two_papers_ACQ/`: `discovery_count_validation.json`, `smoke.json` and `aceb_manifest_summary.json`.
  - Figure: `paper/two_papers/figs_ACQ/acq_smoke_binned_counts.png`.

## 1. Counting

### Discovery binning, reproduced exactly

- **Bins and options.** The discovery `50.QDNAseq.RData` (made 12 March 2025 by another user's pipeline, QDNAseq 1.38) stores:
  - the 61,775 hg38 50 kb bins (50,497 `use`), contiguous from position 1, chromosomes 1–22, X and Y;
  - the run options: `min_mapping_quality 37`, `paired_end FALSE`, `include_chrX FALSE`, `bin_size 50`.
- **Counting rule.** It is QDNAseq `binReadCounts` with those options and its default flags. A record is counted if it is mapped, not QC-fail, not a duplicate and has MAPQ ≥ 37. Secondary and supplementary records are not filtered. It is counted in the bin that holds its leftmost position, after `chr` is stripped. Reads on alt, decoy and other contigs fall outside the bins.
- **Discovery BAMs.** They are on the cluster (`SWGCohort/dna_seq_bam`, 50 bp single-end, bwa aln, MarkDuplicates).

**Validation.** 5 discovery BAMs were re-counted, one in each of the 5 discovery name formats: 308,875 bins in all.

| Method | Bins matching the stored `50.raw_read_counts.txt` exactly |
|---|---|
| QDNAseq 1.42 `binReadCounts` (same options) | 308,875 / 308,875 (100%), total reads identical |
| `samtools view \| awk` counter (`tp_acq_count.sh`) | 308,875 / 308,875 (100%) |

The two methods agree exactly, so the fast samtools counter is used for ACE-B. It writes files in the format of `50.raw_read_counts.txt`.

On the registered depth definition (primary reads × modal read length / 3,088,269,832), these discovery BAMs are at 0.43–0.71× nominal (read length 50). The counted reads are 13.8–21.0 M.

### ACE-B smoke (5 BAMs, seed 1)

- **Downsampling.** `samtools view --subsample f --subsample-seed 1`. This is the registration's `-s 1.<fraction>`: a read-name hash that keeps mates together, applied before the filters.
- **Fraction.** f = target ÷ native nominal depth. Native nominal = primary reads (flag & 0x900 = 0, unmapped and duplicates included) × modal read length / 3,088,269,832.
- **Resources.** One job per BAM, 8 CPUs requested.

| Smoke BAM | BAM GB | Native nominal | Counted reads, native | 0.4× fraction | Counted at 0.4× | Counted at 0.29× | Wall | Max RSS | CPU time |
|---|---|---|---|---|---|---|---|---|---|
| Batch1 | 26.5 | 18.2× | 377.6 M | 0.0220 | 8.32 M | 6.03 M | 9 min 42 s | 0.64 GB | 33.9 min |
| Batch2 | 15.5 | 10.2× | 224.3 M | 0.0392 | 8.80 M | 6.38 M | 5 min 16 s | 0.35 GB | 19.3 min |
| Batch3 (`99A999999A9` name) | 7.7 | 5.1× | 116.0 M | 0.0789 | 9.16 M | 6.64 M | 2 min 30 s | 0.35 GB | 7.2 min |
| Batch4 | 17.6 | 12.1× | 289.7 M | 0.0331 | 9.58 M | 6.94 M | 5 min 58 s | 0.35 GB | 16.6 min |
| Pilot | 12.5 | 9.8× | 265.6 M | 0.0406 | 10.79 M | 7.82 M | 5 min 14 s | 0.34 GB | 13.0 min |

- **Depth reached.** The realised nominal depth after downsampling was 0.3998–0.4004× and 0.2897–0.2903×.
- **Time.** The native pass takes 84–89% of the wall time. Each downsampled pass reads the whole BAM again but takes about a tenth as long.
- **Output.** About 1.95 MB per sample (three gzipped count tables).
- **Figure.** `paper/two_papers/figs_ACQ/acq_smoke_binned_counts.png` shows the Batch2 sample's binned counts genome-wide (count ÷ median, `use` bins) at all three depths. The median per bin is 4,143 native, 163 at 0.4× and 118 at 0.29×.

### Full-run estimate (all 310 BAMs, per-sample jobs)

The 310 BAMs are all `markdup.bam` and Pilot BAMs; the redundant `markdup.dedup.bam` files are excluded. They total 5.65 TB (median 17.5 GB, largest 48.8 GB). From the smoke:
- CPU time is about 66 CPU-s per GB, and single-job wall time about 21 s per GB.
- **Native + 0.4× + 0.29×.** About 105 CPU-hours, or 33 hours if the jobs ran one after another. The longest single job (48.8 GB) takes about 17 min.
  - With 60–100 jobs running at once (the index campaign ran 69 at once without trouble), wall time is about 1–2 hours including queueing.
  - Request 4 CPUs and 2 GB per job.
- **Registered ICC seeds 2–5 on the 0.4× arm.** Each adds one more pass of about a tenth of the native time. Together they add about 35 CPU-hours, for a total of about 140 CPU-hours.
- **Output.** About 0.6 GB in all, or about 1.4 GB with the ICC seeds.

### Two things the registration should state before the full run

1. **Modal read length.**
   - The ACE-B reads are adapter-trimmed 100 bp paired-end reads. The mode is 100 in all 310 BAMs, but the mean is 82–89 bp (median ratio of mode to mean 1.15).
   - "0.4× nominal" by the modal-length rule is therefore about 0.35× in sequenced bases.
   - The discovery reads are untrimmed 50 bp single-end, so mode and mean are the same there.
2. **Paired ends and counted reads.**
   - The discovery count call (`pairedEnds FALSE`) counts each mate as a read. ACE-B counted the same way gives 8.3–10.8 M counted reads at 0.4× nominal. That is about 4–5 M fragments, because mates land in the same or neighbouring bins.
   - The discovery BAMs give 13.8–21.0 M counted single-end reads at native depth. The shipped discovery median is about 0.29× on the QDNAseq-total basis, which is about 18 M reads.
   - So the registered ACE-B 0.4× arm has about half the counted reads of the discovery training data, and about a quarter of the independent read positions.
   - Matching counted reads would take about 0.7–0.9× nominal. Matching fragments would take about 1.5×.
   - This is a design choice for Rehan and the registration, not something to settle here. One option is to keep 0.4× as registered and add a "counted-reads matched to the discovery median" arm, stated before scoring.

## 2. Indexing

- **Indexes created.** 69 BAMs had no index: 53 Batch1 `markdup.bam` and all 16 Pilot `hg38.srt.bam`. Each was indexed in its own job (samtools index into a temporary file, then renamed; no existing file was overwritten).
- **Verification.** `samtools idxstats` ran cleanly on all 69 (456 contigs each, no stderr). Index time was 35–548 s per BAM, 6.7 CPU-hours in all.
- **Coverage now.** All 310 analysis BAMs have an index, and `idxstats` runs on all 310.
- **Existing indexes.** 103 are older than their BAM by modification time (Batch1 1, Batch2 57, Batch4 45). This looks like copy order: idxstats totals equal the MarkDuplicates totals for all of them except the two BAMs listed in §3.
- **Not touched.** The `markdup.dedup.bam` files were not touched; one of their indexes fails `idxstats`. Nothing was deleted or moved.

## 3. Manifest summary

`killcoyne_mm/two_papers_ACQ/aceb_manifest.tsv` holds one row per BAM, 406 rows including the dedup files. Columns: batch, file, size, index, quickcheck, read groups/lanes, read length (mode, mean), primary/mapped/duplicate reads (MarkDuplicates), idxstats totals, mean coverage (mosdepth; Batch1 `depth.txt` where mosdepth is missing; Pilot samtools coverage), nominal depth, sheet and ABD linkage, and fingerprint profile, flag and genotype cluster.

| Batch | BAMs | TB | Read groups (median) | Primary reads (median) | Duplicates | Mean coverage, median (range) | Nominal depth, median (range) | In sheet | Patient linked to DB (ABD) |
|---|---|---|---|---|---|---|---|---|---|
| Batch1 | 96 | 2.24 | 7 | 473 M | 18.8% | 10.0× (5.6–19.2) | 15.3× (8.5–30.6) | 96 | 94 |
| Batch2 | 96 | 1.83 | 5 | 330 M | 19.3% | 7.0× (0.6–23.9) | 10.7× (1.0–34.8) | 96 | 95 |
| Batch3 | 42 | 0.32 | 2 | 153 M | 12.9% | 3.4× (1.9–4.9) | 4.9× (3.0–7.4) | 42 | <5 |
| Batch4 | 60 | 1.01 | 4 | 348 M | 11.9% | 8.0× (4.5–16.5) | 11.3× (6.1–21.3) | 0 | 0 |
| Pilot | 16 | 0.25 | 7 | 341 M | 17.2% | 7.7× (4.8–13.4) | 11.0× (7.9–21.6) | 16 (by SLX SampleID) | 16 |
| Batch2 `markdup.dedup` (redundant) | 96 | 0.84 | — | — | — | — | — | — | — |

- **Coverage.** No BAM is below 0.4× nominal, so every sample can be downsampled; one is below 1×. The study team's "about 7×" fits Batch2, Batch4 and the Pilot; Batch1 is deeper (about 10×) and Batch3 shallower (about 3.4×).
- **Sheet coverage.** The sheet's `Mean_Coverage` correlates 0.95 with mosdepth (n = 207) but is 1.58× lower at the median, so it is probably measured after filtering.
- **Sheet against BAMs.** The sheet has 234 rows, 233 unique names and 117 patients. Every sheet name has a BAM. One name appears twice, as the same sample sequenced in Batch2 and Batch3; the genotypes agree.
- **Pilot.** All 16 Pilot BAMs match a sheet `SampleID` (15 exactly, 1 by barcode within the same SLX pools). They are re-sequencing of 9 batch-1 and 7 batch-2 samples. For 15 of them the same sample also has a Batch1/2 BAM, and the genotype agrees in 15 of 15. The Pilot is a technical replicate set, not new samples.
- **Batch4.** None of the 60 names (`PS`-format, some with `_A`-style suffixes) is in the sheet or matches another batch's BAM. By genotype:
  - 31 Batch4 BAMs are further samples from 28 sheet patients (27 of them linked to the DB by ABD);
  - 29 come from 13 individuals who are not in the sheet (clusters of 2–4 BAMs, <5 singletons).
- **Nottingham-format names (Batch3).** Batch3's 42 BAMs (41 Nottingham-format names plus the one `PS` sample also sequenced in Batch2) come from 17 sheet patients, <5 of whom are also in other batches. The Nottingham-format samples have sheet `PatientID`s but almost no DB linkage (<5 Batch3 patients linked), as ABD found.

**Genotype identity.**
- **Method.** 15,645 fingerprint SNPs. 232 existing `*.fingerprint.vcf` files were used, plus samtools pileups for the 62 Batch1 and 16 Pilot BAMs that have none.
- **Metric.** The opposite-homozygote rate (OH) at sites where both samples are homozygous with ≥ 3 reads. Pairs need ≥ 200 such sites; the median is 3,298.
- **Method check.** VCF and pileup gave OH = 0 for each of 5 BAMs profiled both ways.
- **Separation.** Same-individual pairs have OH ≤ 0.018. All other clean pairs are ≥ 0.173, with a mode near 0.25. The threshold of 0.03 sits in an empty gap.
- **Individuals.** 310 BAMs form 130 individuals: the 117 sheet patients plus the 13 Batch4-only individuals.
- **Genotype against the sheet.** 0 sheet patients are split across genotypes, and 0 genotypes span two sheet patients, so no sample swap was found among the 250 sheet-linked BAMs. A BAM-to-patient link can be confirmed only where the patient has more than one BAM; 33 of the 117 sheet patients have only one.

**Flags.**
- 7 profiles were flagged. 4 Batch2 profiles are only borderline: 5–6 partners at intermediate OH, but identity is clear (minimum OH ≤ 0.010).
- **Possible mixture (1 Batch4 BAM).** Its heterozygous share is 0.51, against a typical 0.30–0.35, and it has 25 intermediate-OH partners. Its genotype still matches its own patient (OH 0.006), so it may be contaminated.
- **Inconsistent BAM (1 Batch2 BAM).** Its MarkDuplicates metrics, mosdepth (0.63×) and fingerprint VCF describe a 30 M-read file. The BAM itself holds 130 M primary reads, with 12.5% secondary alignments, only 64% properly paired and 31% of mates on another chromosome. Its pileup still has few SNP sites with ≥ 3 reads (809). The QC belongs to another version of the file, and the library looks chimeric or contaminated. Its idxstats totals do not match MarkDuplicates.
- **Low coverage (1 Batch3 BAM).** It has few covered SNP sites but matches its same-name twin.
- One Batch1 BAM differs from its MarkDuplicates total by 8 reads, which is negligible.

**Truncated or unusable files.**
- All 310 analysis BAMs pass `samtools quickcheck`.
- 56 of the 96 Batch2 `markdup.dedup.bam` files are truncated (no EOF block). The other 40 are complete but redundant: they are the `markdup.bam` with duplicates removed.
- The inconsistent Batch2 BAM above should not be used until Tim explains it.

**Space.** Deleting all 96 `markdup.dedup.bam` files (and their indexes, 0.5 GB) would free **0.835 TB**, of which 0.311 TB is the 56 truncated files. This waits for Rehan's OK and Tim's confirmation; nothing was deleted.

## What this changes

The counting step is ready and validated: the discovery bins and counting rule are reproduced exactly (100% of 308,875 bins). The full ACE-B count is about 140 CPU-hours and 1–2 hours of wall time as per-sample jobs. Before it runs, the registration should say how ACE-B's trimmed 100 bp paired-end reads map onto "0.4× nominal". As written, that arm has about half the counted reads of the discovery data. ACE-B is also bigger than the sheet: 60 Batch4 BAMs, 13 of whose individuals are not in the sheet, and a 16-sample Pilot that duplicates batch samples.

## To ask Tim or Leanne

1. **Batch4.** Patient IDs for the 60 BAMs. By genotype, 31 are extra samples from 28 sheet patients and 29 come from 13 people who are not in the sheet. Is Batch4 part of the ACE-B cohort, and which endoscopy is each sample from?
2. **Pilot.** These 16 BAMs re-sequence batch-1 and batch-2 samples. Which copy is canonical? Proposal: the batch BAM is primary and the Pilot is a technical replicate.
3. **Same sample in Batch2 and Batch3.** One sample is listed in both batches. Which BAM should be used?
4. **The inconsistent Batch2 BAM.** Its QC files describe a 30 M-read version, but the BAM holds 130 M reads and looks chimeric. Was it re-merged? Please supply the correct file.
5. **Possible contamination.** One Batch4 BAM has a mixture-like fingerprint.
6. **Nottingham-format samples (41).** Which centre do they come from, and what is the route to their histology and follow-up? They do not link to the Cambridge database.
7. **The `markdup.dedup.bam` files.** Confirm they may be deleted (0.84 TB, 56 truncated), and that the originals or FASTQs are kept by Tim or the Fitzgerald lab.
8. **Batch1 QC.** Fingerprints and mosdepth exist for only 34 of 96 Batch1 BAMs. Not needed now (pileups replaced the fingerprints), but worth knowing.
