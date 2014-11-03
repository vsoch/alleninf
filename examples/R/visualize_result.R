# This script will visualize a result (expression and image map correlations)
# from the alleninf package.  If the original image is available, it will
# visualize the overlap in the map

library(ggplot2)

setwd("/home/vanessa/Documents/Work/GENE_EXPRESSION/alleninf")

data_files = list.files(pattern="*alleninf.csv")

for (file in data_files){
  data = read.csv(file,head=TRUE)
  plot_data = data.frame(allen.expression=data[,3],nifti=data$NIFTI.values)
  model = lm(plot_data$nifti~plot_data$allen.expression)
  png(file = paste(colnames(data)[3],".png",sep=""))
  plot(plot_data,pch=19,col="orange",main=paste(colnames(data)[3],"vs Brain Map"),xlab=names(data)[3],ylab="Brain Map Value")
  abline(model,lty=2,col="red") 
  dev.off()
}
