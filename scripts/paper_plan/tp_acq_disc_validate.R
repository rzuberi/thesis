# ACQ: re-count discovery BAMs with QDNAseq::binReadCounts using the discovery bins and the discovery generator's options
# (minMapq 37, pairedEnds FALSE, other flags at QDNAseq defaults) and compare bin by bin with the stored 50.raw_read_counts.txt
# and with the samtools|awk counter (tp_acq_count.sh). Row-level output stays in killcoyne_mm/two_papers_ACQ/.
suppressMessages({library(QDNAseq); library(Biobase)})
a <- commandArgs(TRUE); bam <- a[1]; stored <- a[2]; awkf <- a[3]; out <- a[4]
bins <- readRDS("/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/feasibility/paper_plan/killcoyne_mm/two_papers_ACQ/disc_bins_hg38_50kb.rds")
t0 <- Sys.time(); rc <- binReadCounts(bins, bamfiles = bam, minMapq = 37, pairedEnds = FALSE, verbose = FALSE); secs <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
q <- as.numeric(assayDataElement(rc, "counts")[, 1])
s <- read.delim(stored, check.names = FALSE); sv <- s[[5]]; stopifnot(identical(s$location, rownames(fData(rc))))
w <- read.delim(gzfile(awkf), check.names = FALSE)[[5]]
r <- c(qdnaseq_vs_stored_exact = mean(q == sv), awk_vs_stored_exact = mean(w == sv), awk_vs_qdnaseq_exact = mean(w == q),
       stored_total = sum(sv), qdnaseq_total = sum(q), awk_total = sum(w), qdnaseq_total_reads_pdata = pData(rc)$total.reads,
       max_abs_diff_qdnaseq_stored = max(abs(q - sv)), n_bins = length(sv), qdnaseq_secs = secs)
print(r); write.table(t(r), out, sep = "\t", quote = FALSE, row.names = FALSE)
