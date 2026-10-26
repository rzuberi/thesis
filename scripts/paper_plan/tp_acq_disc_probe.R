# ACQ: inspect one discovery 50.QDNAseq.RData (object class, featureData columns, pData, bin count) and export the 61,775-bin hg38 annotation.
suppressMessages({library(QDNAseq); library(Biobase)})
args <- commandArgs(TRUE); f <- args[1]; out <- args[2]
e <- new.env(); nm <- load(f, envir = e); cat("objects:", nm, "\n")
for (n in nm) { o <- get(n, e); cat(n, "class", class(o), "\n")
  if (is(o, "eSet")) { cat("dims", dim(o), "\n"); fd <- fData(o); cat("fData cols:", colnames(fd), "\n"); print(head(fd, 3)); print(pData(o)[, setdiff(colnames(pData(o)), c("name"))])
    cat("assayData:", ls(assayData(o)), "\n"); cat("bins:", nrow(fd), "use TRUE:", sum(fd$use), "\n")
    if (!is.null(out)) { saveRDS(AnnotatedDataFrame(fd), out); write.table(cbind(location = rownames(fd), fd), sub(".rds$", ".tsv", out), sep = "\t", quote = FALSE, row.names = FALSE) }
    print(experimentData(o)); print(annotation(o)); md <- o@.__classVersion__; print(md)
  } else str(o, max.level = 1) }
