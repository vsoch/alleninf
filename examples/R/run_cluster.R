# run_cluster.R will launch instances of alleninf to run in a cluster environment

# Here is a folder with images to perform inference on
input_folder = "/scratch/users/vsochat/DATA/BRAINBEHAVIOR/DisorderMaps"

# The images to perform inference on
mrs = list.files(input_folder,pattern="*_z_FDR_0.05.nii.gz")

# Here is an output directory
output_dir = "/scratch/users/vsochat/DATA/GENE_EXPRESSION/alleninf"

for (i in 1:length(mrs)){
  mr = mrs[i]
  nifti_file = paste(input_folder,"/",mr,sep="")
  output_prefix = gsub("_z_FDR_0.05.nii.gz","",mr)
  outfile = paste(output_dir,"/",output_prefix,"allen_brain_inference.tsv",sep="")
  jobby = paste(folder,"96.job",sep="")
  sink(file=paste(".job/",jobby,sep=""))
  cat("#!/bin/bash\n")
  cat("#SBATCH --job-name=",jobby,"\n",sep="")  
  cat("#SBATCH --output=.out/",jobby,".out\n",sep="")  
  cat("#SBATCH --error=.out/",jobby,".err\n",sep="")  
  cat("#SBATCH --time=2-00:00\n",sep="")
  cat("#SBATCH --mem=64000\n",sep="")
  cat("alleninf --radius 3 --out ",outfile,nifti_file,\n")
  sink()
    
  # SUBMIT R SCRIPT TO RUN ON CLUSTER  
  system(paste("sbatch -p dpwall ",paste(".job/",jobby,sep="")))
  }  
}
