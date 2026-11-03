# Two papers, agent KCF (docs/two_papers_KCF.md): Killcoyne 2020 Extended Data Fig. 6 (accuracy vs number of training patients) on our cohort.
# The kv_cv.R outer loop (kv_common.R cvcurves: class-error-minimum lambda from 10 x 5 patient-grouped CV inside the training patients) with the
# training patients of each outer fold subsampled to K patients, stratified by status at the fold's training prevalence. The same subsample
# (seed 100000 * K + 100 * REP + fold, independent of FEAT) is used for copy number and H&E, so the combined score is the mean of two models
# trained on the same patients. Held-out patients are the full outer test fold, so every size is scored on the same patients.
# FEAT = cnv (shipped matrix, cnv_their_C.csv, as L-CNV) | clean (ART clean-tile mean embedding, z-scaled on the training rows, as clean L-IMG).
# FEAT K REP -> killcoyne_mm/two_papers_KCF/lc/<FEAT>_k<K>_rep_XX.csv (row-level, cluster only).
source("/mnt/scratche/slow/fmlab/zuberi01/phd/thesis/scripts/paper_plan/kv_common.R")
FEAT <- Sys.getenv("FEAT"); K_ <- as.integer(Sys.getenv("K")); REP <- as.integer(Sys.getenv("REP"))
OD <- file.path(M, "two_papers_KCF", "lc"); dir.create(OD, recursive = TRUE, showWarnings = FALSE)
fo_ <- file.path(OD, sprintf("%s_k%d_rep_%02d.csv", FEAT, K_, REP)); if (file.exists(fo_)) quit(save = "no")
RAW <- if (FEAT == "cnv") readblock("cnv_their_C.csv") else {
  R <- read_csv(file.path(M, "two_papers_ART", "feats", "clean.csv.gz"), col_types = cols(Sample = "c", .default = "d"), progress = FALSE)
  X <- as.matrix(R[, -1]); rownames(X) <- R$Sample; stopifnot(all(ids %in% rownames(X))); X[ids, , drop = FALSE] }
strat_folds <- function(pp, yy, seed, nf) { pl <- tapply(yy, pp, max); Pp <- names(pl)[pl == 1]; Np <- names(pl)[pl == 0]; set.seed(seed); ord <- c(sample(Pp), sample(Np)); setNames(rep(1:nf, length.out = length(ord)), ord) }
fold_of <- strat_folds(pat, y, REP, 10)   # identical to kv_cv.R
out <- list()
for (k in 1:10) {
  te <- fold_of[pat] == k; trp <- unique(pat[!te]); pl <- tapply(y[!te], pat[!te], max)[trp]
  set.seed(100000 * K_ + 100 * REP + k); nP <- round(K_ * mean(pl)); keep <- c(sample(trp[pl == 1], min(nP, sum(pl == 1))), sample(trp[pl == 0], min(K_ - nP, sum(pl == 0))))
  tr <- which(pat %in% keep)
  X <- if (FEAT == "cnv") RAW else zs(RAW, tr)
  cv <- cvcurves(X[tr, ], y[tr], pat[tr]); pr <- predict(cv$fit, X[te, , drop = FALSE], s = cv$class_min, type = "response")[, 1]
  nz <- sum(as.numeric(as.matrix(coef(cv$fit, s = cv$class_min)))[-1] != 0)
  out[[k]] <- data.frame(Sample = ids[te], Patient = pat[te], y = y[te], feat = FEAT, K = K_, rep = REP, fold = k, n_train_pat = length(keep), lambda = cv$class_min, nonzero = nz, pred = pr)
}
write_csv(bind_rows(out), fo_); message("KCF LC DONE ", FEAT, " K ", K_, " rep ", REP)
