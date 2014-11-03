# parse_cluster.R will read in and parse results

setwd("/scratch/users/vsochat/DATA/GENE_EXPRESSION/alleninf")

# Here is a folder with images to perform inference on
files = list.files(pattern="*.tsv")

# FDR threshold
thresh = 0.25

# Here we will keep significant results
sig = c()

for (f in files){
  result = read.csv(f,sep="\t",head=TRUE)
  # Calculate FDR corrected p values
  fdr = p.adjust(result$p_value,method="fdr")
  if (!is.na(unique(result$p_value))){
    if (any(fdr<=thresh)) {
     cat("Found significant result!\n")
     sigresult = result[which(fdr <= thresh),]
     sigresult = cbind(rep(f,nrow(sigresult)),sigresult,fdr[which(fdr <= thresh)])
     sig = rbind(sig,sigresult)
    }
  }
}

colnames(sig)[1] = "brain_map"
colnames(sig)[9] = "fdr"

write.table(sig,file="random_effects_sig_result.tsv.res",sep="\t",col.names=TRUE,row.names=FALSE)
